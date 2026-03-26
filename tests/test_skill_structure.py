from pathlib import Path


def test_skill_file_exists() -> None:
    assert Path("SKILL.md").exists()


def test_skill_frontmatter_contains_required_fields() -> None:
    content = Path("SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "\nname: arxiv-skill\n" in content
    assert "\ndescription: " in content


def test_expected_skill_directories_exist() -> None:
    assert Path("scripts").is_dir()
    assert Path("references").is_dir()
    assert Path("assets/examples").is_dir()


def test_reference_files_exist() -> None:
    assert Path("references/workflow.md").exists()
    assert Path("references/search-syntax.md").exists()
    assert Path("references/storage-format.md").exists()
    assert Path("references/analysis-framework.md").exists()


def test_script_entrypoints_exist() -> None:
    assert Path("scripts/search_arxiv.py").exists()
    assert Path("scripts/cache_paper.py").exists()
    assert Path("scripts/list_cached_papers.py").exists()
    assert Path("scripts/read_cached_paper.py").exists()
