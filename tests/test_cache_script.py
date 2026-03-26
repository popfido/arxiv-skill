import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts import cache_paper as cache_paper_script
from scripts.common import cache_paper, list_cached_papers, read_cached_paper


class MockAuthor:
    def __init__(self, name: str):
        self.name = name


@pytest.fixture
def mock_paper() -> MagicMock:
    paper = MagicMock()
    paper.get_short_id.return_value = "2103.12345"
    paper.title = "Test Paper"
    paper.authors = [MockAuthor("John Doe")]
    paper.summary = "Test abstract"
    paper.categories = ["cs.AI"]
    paper.published = datetime(2023, 1, 1, tzinfo=timezone.utc)
    paper.pdf_url = "https://arxiv.org/pdf/2103.12345"

    def download_pdf(dirpath: str, filename: str) -> None:
        Path(dirpath, filename).write_bytes(b"%PDF-1.4")

    paper.download_pdf.side_effect = download_pdf
    return paper


def test_cache_paper_creates_markdown_and_deletes_pdf(
    mock_paper: MagicMock, tmp_path: Path
) -> None:
    mock_client = MagicMock()
    mock_client.results.return_value = [mock_paper]
    with patch("scripts.common.arxiv.Client", return_value=mock_client):
        with patch(
            "scripts.common.pymupdf4llm.to_markdown",
            return_value="# Test Paper\nConverted content",
        ):
            result = cache_paper("2103.12345", tmp_path)

    assert result["status"] == "success"
    assert result["reused_cache"] is False
    assert Path(result["markdown_path"]).exists()
    assert result["pdf_path"] is None
    assert not tmp_path.joinpath("2103.12345.pdf").exists()


def test_cache_paper_reuses_existing_markdown(tmp_path: Path) -> None:
    markdown_path = tmp_path / "2103.12345.md"
    markdown_path.write_text("# Existing Paper", encoding="utf-8")
    result = cache_paper("2103.12345", tmp_path)
    assert result["reused_cache"] is True
    assert result["markdown_path"] == str(markdown_path)


def test_cache_script_main_prints_json(
    mock_paper: MagicMock,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.results.return_value = [mock_paper]
    with patch("scripts.common.arxiv.Client", return_value=mock_client):
        with patch(
            "scripts.common.pymupdf4llm.to_markdown",
            return_value="# Test Paper\nConverted content",
        ):
            monkeypatch.setattr(
                "sys.argv",
                [
                    "cache_paper.py",
                    "--paper-id",
                    "2103.12345",
                    "--storage-path",
                    str(tmp_path),
                ],
            )
            cache_paper_script.main()
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "success"


def test_list_cached_papers_without_metadata(tmp_path: Path) -> None:
    paper_path = tmp_path / "2401.12345.md"
    paper_path.write_text("# Paper", encoding="utf-8")
    result = list_cached_papers(tmp_path, include_metadata=False)
    assert result["total_papers"] == 1
    assert result["papers"][0]["paper_id"] == "2401.12345"


def test_list_cached_papers_with_metadata(
    tmp_path: Path, mock_paper: MagicMock
) -> None:
    paper_path = tmp_path / "2103.12345.md"
    paper_path.write_text("# Paper", encoding="utf-8")
    mock_client = MagicMock()
    mock_client.results.return_value = [mock_paper]
    with patch("scripts.common.arxiv.Client", return_value=mock_client):
        result = list_cached_papers(tmp_path, include_metadata=True)
    assert result["papers"][0]["title"] == "Test Paper"


def test_read_cached_paper_returns_content(tmp_path: Path) -> None:
    paper_path = tmp_path / "2401.12345.md"
    paper_path.write_text("# Paper\nBody", encoding="utf-8")
    result = read_cached_paper("2401.12345", tmp_path)
    assert result["paper_id"] == "2401.12345"
    assert result["content"] == "# Paper\nBody"


def test_read_cached_paper_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found in cache"):
        read_cached_paper("does-not-exist", tmp_path)
