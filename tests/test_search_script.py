import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from scripts import search_arxiv
from scripts.common import (
    build_raw_search_url,
    parse_arxiv_atom_response,
    search_papers,
    validate_categories,
)


class MockAuthor:
    def __init__(self, name: str):
        self.name = name


@pytest.fixture
def mock_paper() -> MagicMock:
    paper = MagicMock()
    paper.get_short_id.return_value = "2103.12345"
    paper.title = "Test Paper"
    paper.authors = [MockAuthor("John Doe"), MockAuthor("Jane Smith")]
    paper.summary = "Test abstract"
    paper.categories = ["cs.AI", "cs.LG"]
    paper.published = datetime(2023, 1, 1, tzinfo=timezone.utc)
    paper.pdf_url = "https://arxiv.org/pdf/2103.12345"
    return paper


def test_validate_categories_accepts_valid_prefixes() -> None:
    assert validate_categories(["cs.AI", "math.OC"]) == ["cs.AI", "math.OC"]


def test_validate_categories_rejects_invalid_prefixes() -> None:
    with pytest.raises(ValueError, match="Invalid arXiv category prefix"):
        validate_categories(["invalid.category"])


def test_parse_arxiv_atom_response() -> None:
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
        <entry>
            <id>http://arxiv.org/abs/2301.00001v1</id>
            <title>Test Paper Title</title>
            <summary>This is a test abstract.</summary>
            <published>2023-01-01T00:00:00Z</published>
            <author><name>John Doe</name></author>
            <author><name>Jane Smith</name></author>
            <arxiv:primary_category term="cs.AI"/>
            <category term="cs.AI"/>
            <category term="cs.LG"/>
            <link title="pdf" href="http://arxiv.org/pdf/2301.00001v1"/>
        </entry>
    </feed>"""

    results = parse_arxiv_atom_response(sample_xml)
    assert results[0]["id"] == "2301.00001"
    assert results[0]["authors"] == ["John Doe", "Jane Smith"]
    assert results[0]["categories"] == ["cs.AI", "cs.LG"]


def test_build_raw_search_url_preserves_to_operator() -> None:
    url = build_raw_search_url(
        query="LLM",
        max_results=5,
        sort_by="date",
        date_from="2023-01-01",
        date_to="2023-12-31",
        categories=["cs.AI"],
    )
    assert "+TO+" in url
    assert "submittedDate:" in url
    assert "cat:cs.AI" in url


def test_search_papers_uses_arxiv_client_for_non_date_queries(
    mock_paper: MagicMock,
) -> None:
    mock_client = MagicMock()
    mock_client.results.return_value = [mock_paper]
    with patch("scripts.common.arxiv.Client", return_value=mock_client):
        result = search_papers(query="test query", max_results=1)
    assert result["total_results"] == 1
    assert result["papers"][0]["id"] == "2103.12345"


def test_search_script_main_prints_json(
    mock_paper: MagicMock,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.results.return_value = [mock_paper]
    with patch("scripts.common.arxiv.Client", return_value=mock_client):
        monkeypatch.setattr(
            "sys.argv",
            ["search_arxiv.py", "--query", "test query", "--max-results", "1"],
        )
        search_arxiv.main()
    output = json.loads(capsys.readouterr().out)
    assert output["total_results"] == 1
