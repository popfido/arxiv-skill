from __future__ import annotations

import json
import os
import xml.etree.ElementTree as element_tree
from datetime import datetime
from pathlib import Path
from typing import NotRequired, Sequence, TypedDict

import arxiv
import httpx
import pymupdf4llm
from dateutil import parser

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
DEFAULT_MAX_RESULTS = 50
VALID_CATEGORY_PREFIXES = {
    "cs",
    "econ",
    "eess",
    "math",
    "physics",
    "q-bio",
    "q-fin",
    "stat",
    "astro-ph",
    "cond-mat",
    "gr-qc",
    "hep-ex",
    "hep-lat",
    "hep-ph",
    "hep-th",
    "math-ph",
    "nlin",
    "nucl-ex",
    "nucl-th",
    "quant-ph",
}


class PaperRecord(TypedDict):
    id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: str
    url: str


class SearchResponse(TypedDict):
    query: str
    total_results: int
    papers: list[PaperRecord]


class CacheResponse(TypedDict):
    status: str
    paper_id: str
    markdown_path: str
    pdf_path: str | None
    reused_cache: bool


class CachedPaperRecord(TypedDict):
    paper_id: str
    markdown_path: str
    title: NotRequired[str]
    summary: NotRequired[str]
    authors: NotRequired[list[str]]
    pdf_url: NotRequired[str]


class ListResponse(TypedDict):
    total_papers: int
    papers: list[CachedPaperRecord]


class ReadResponse(TypedDict):
    status: str
    paper_id: str
    markdown_path: str
    content: str


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_storage_path() -> Path:
    return skill_root() / ".cache" / "arxiv-skill" / "papers"


def resolve_storage_path(explicit_path: str | None = None) -> Path:
    raw_path = (
        explicit_path
        or os.getenv("ARXIV_SKILL_STORAGE_PATH")
        or str(default_storage_path())
    )
    storage_path = Path(raw_path).expanduser().resolve()
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def build_paper_paths(paper_id: str, storage_path: Path) -> tuple[Path, Path]:
    return storage_path / f"{paper_id}.md", storage_path / f"{paper_id}.pdf"


def validate_categories(categories: Sequence[str]) -> list[str]:
    validated: list[str] = []
    for category in categories:
        prefix = category.split(".", 1)[0]
        if prefix not in VALID_CATEGORY_PREFIXES:
            raise ValueError(f"Invalid arXiv category prefix: {prefix}")
        validated.append(category)
    return validated


def normalize_query(query: str) -> str:
    return query.strip()


def process_paper(paper: arxiv.Result) -> PaperRecord:
    return {
        "id": paper.get_short_id(),
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "abstract": paper.summary,
        "categories": list(paper.categories),
        "published": paper.published.isoformat(),
        "url": paper.pdf_url,
    }


def parse_arxiv_atom_response(xml_text: str) -> list[PaperRecord]:
    results: list[PaperRecord] = []
    try:
        root = element_tree.fromstring(xml_text)
    except element_tree.ParseError as exc:
        raise ValueError(f"Failed to parse arXiv API response: {exc}") from exc

    for entry in root.findall("atom:entry", ARXIV_NS):
        id_element = entry.find("atom:id", ARXIV_NS)
        if id_element is None or id_element.text is None:
            continue

        raw_paper_id = id_element.text.split("/abs/")[-1]
        paper_id = raw_paper_id.split("v")[0] if "v" in raw_paper_id else raw_paper_id

        title_element = entry.find("atom:title", ARXIV_NS)
        summary_element = entry.find("atom:summary", ARXIV_NS)
        published_element = entry.find("atom:published", ARXIV_NS)

        authors: list[str] = []
        for author in entry.findall("atom:author", ARXIV_NS):
            name_element = author.find("atom:name", ARXIV_NS)
            if name_element is not None and name_element.text:
                authors.append(name_element.text)

        categories: list[str] = []
        primary_category = entry.find("arxiv:primary_category", ARXIV_NS)
        if primary_category is not None:
            primary_term = primary_category.get("term")
            if primary_term:
                categories.append(primary_term)

        for category in entry.findall("atom:category", ARXIV_NS):
            term = category.get("term")
            if term and term not in categories:
                categories.append(term)

        pdf_url = ""
        for link in entry.findall("atom:link", ARXIV_NS):
            if link.get("title") == "pdf" and link.get("href"):
                pdf_url = link.get("href", "")
                break
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{raw_paper_id}"

        results.append(
            {
                "id": paper_id,
                "title": (
                    title_element.text.strip().replace("\n", " ")
                    if title_element is not None and title_element.text
                    else ""
                ),
                "authors": authors,
                "abstract": (
                    summary_element.text.strip().replace("\n", " ")
                    if summary_element is not None and summary_element.text
                    else ""
                ),
                "categories": categories,
                "published": (
                    published_element.text
                    if published_element is not None and published_element.text
                    else ""
                ),
                "url": pdf_url,
            }
        )

    return results


def build_raw_search_url(
    query: str,
    max_results: int,
    sort_by: str,
    date_from: str | None,
    date_to: str | None,
    categories: Sequence[str],
) -> str:
    query_parts: list[str] = []
    normalized_query = normalize_query(query)
    if normalized_query:
        query_parts.append(f"({normalized_query})")
    if categories:
        category_filter = " OR ".join(f"cat:{category}" for category in categories)
        query_parts.append(f"({category_filter})")
    if date_from or date_to:
        start_date = (
            parser.parse(date_from).strftime("%Y%m%d0000")
            if date_from
            else "199107010000"
        )
        end_date = (
            parser.parse(date_to).strftime("%Y%m%d2359")
            if date_to
            else datetime.now().strftime("%Y%m%d2359")
        )
        query_parts.append(f"submittedDate:[{start_date}+TO+{end_date}]")
    if not query_parts:
        raise ValueError("No search criteria provided")

    final_query = " AND ".join(query_parts)
    encoded_query = (
        final_query.replace(" AND ", "+AND+").replace(" OR ", "+OR+").replace(" ", "+")
    )
    sort_key = "submittedDate" if sort_by == "date" else "relevance"
    return (
        f"{ARXIV_API_URL}?search_query={encoded_query}"
        f"&max_results={max_results}&sortBy={sort_key}&sortOrder=descending"
    )


def raw_arxiv_search(
    query: str,
    max_results: int,
    sort_by: str,
    date_from: str | None,
    date_to: str | None,
    categories: Sequence[str],
) -> list[PaperRecord]:
    url = build_raw_search_url(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        date_from=date_from,
        date_to=date_to,
        categories=categories,
    )
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url)
        response.raise_for_status()
    return parse_arxiv_atom_response(response.text)


def search_papers(
    query: str,
    max_results: int = 10,
    date_from: str | None = None,
    date_to: str | None = None,
    categories: Sequence[str] = (),
    sort_by: str = "relevance",
) -> SearchResponse:
    if sort_by not in {"relevance", "date"}:
        raise ValueError("sort_by must be one of: relevance, date")

    validated_categories = validate_categories(categories)
    limited_results = min(max_results, DEFAULT_MAX_RESULTS)
    normalized_query = normalize_query(query)

    if date_from or date_to:
        papers = raw_arxiv_search(
            query=normalized_query,
            max_results=limited_results,
            sort_by=sort_by,
            date_from=date_from,
            date_to=date_to,
            categories=validated_categories,
        )
        return {
            "query": normalized_query,
            "total_results": len(papers),
            "papers": papers,
        }

    query_parts: list[str] = []
    if normalized_query:
        query_parts.append(f"({normalized_query})")
    if validated_categories:
        category_filter = " OR ".join(
            f"cat:{category}" for category in validated_categories
        )
        query_parts.append(f"({category_filter})")
    if not query_parts:
        raise ValueError("No search criteria provided")

    final_query = " ".join(query_parts)
    sort_criterion = (
        arxiv.SortCriterion.SubmittedDate
        if sort_by == "date"
        else arxiv.SortCriterion.Relevance
    )
    client = arxiv.Client()
    search = arxiv.Search(
        query=final_query,
        max_results=limited_results,
        sort_by=sort_criterion,
    )

    papers: list[PaperRecord] = []
    for paper in client.results(search):
        papers.append(process_paper(paper))
        if len(papers) >= limited_results:
            break

    return {
        "query": normalized_query,
        "total_results": len(papers),
        "papers": papers,
    }


def cache_paper(
    paper_id: str,
    storage_path: Path,
    keep_pdf: bool = False,
    force: bool = False,
) -> CacheResponse:
    markdown_path, pdf_path = build_paper_paths(paper_id, storage_path)
    if markdown_path.exists() and not force:
        return {
            "status": "success",
            "paper_id": paper_id,
            "markdown_path": str(markdown_path),
            "pdf_path": str(pdf_path) if pdf_path.exists() else None,
            "reused_cache": True,
        }

    client = arxiv.Client()
    try:
        paper = next(iter(client.results(arxiv.Search(id_list=[paper_id]))))
    except StopIteration as exc:
        raise ValueError(f"Paper {paper_id} not found on arXiv") from exc

    paper.download_pdf(dirpath=str(storage_path), filename=pdf_path.name)
    markdown = pymupdf4llm.to_markdown(pdf_path, show_progress=False)
    markdown_path.write_text(markdown, encoding="utf-8")

    retained_pdf_path: str | None = str(pdf_path)
    if not keep_pdf:
        if pdf_path.exists():
            pdf_path.unlink()
        retained_pdf_path = None

    return {
        "status": "success",
        "paper_id": paper_id,
        "markdown_path": str(markdown_path),
        "pdf_path": retained_pdf_path,
        "reused_cache": False,
    }


def list_cached_papers(
    storage_path: Path, include_metadata: bool = False
) -> ListResponse:
    markdown_files = sorted(storage_path.glob("*.md"))
    papers: list[CachedPaperRecord] = [
        {"paper_id": markdown_file.stem, "markdown_path": str(markdown_file)}
        for markdown_file in markdown_files
    ]

    if include_metadata and papers:
        client = arxiv.Client()
        results = list(
            client.results(
                arxiv.Search(id_list=[paper["paper_id"] for paper in papers])
            )
        )
        metadata_by_id: dict[str, CachedPaperRecord] = {}
        for result in results:
            metadata_by_id[result.get_short_id()] = {
                "paper_id": result.get_short_id(),
                "markdown_path": str(storage_path / f"{result.get_short_id()}.md"),
                "title": result.title,
                "summary": result.summary,
                "authors": [author.name for author in result.authors],
                "pdf_url": result.pdf_url,
            }
        merged_papers: list[CachedPaperRecord] = []
        for paper in papers:
            merged_papers.append(metadata_by_id.get(paper["paper_id"], paper))
        papers = merged_papers

    return {
        "total_papers": len(papers),
        "papers": papers,
    }


def read_cached_paper(paper_id: str, storage_path: Path) -> ReadResponse:
    markdown_path, _ = build_paper_paths(paper_id, storage_path)
    if not markdown_path.exists():
        raise FileNotFoundError(
            f"Paper {paper_id} not found in cache. Cache it first with scripts/cache_paper.py."
        )
    return {
        "status": "success",
        "paper_id": paper_id,
        "markdown_path": str(markdown_path),
        "content": markdown_path.read_text(encoding="utf-8"),
    }


def print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2))
