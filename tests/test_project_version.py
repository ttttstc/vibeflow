import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def test_project_version_matches_plugin_manifests():
    version = read_text(REPO_ROOT / "VERSION").strip()
    plugin_manifest = read_json(REPO_ROOT / ".claude-plugin" / "plugin.json")
    marketplace_manifest = read_json(REPO_ROOT / ".claude-plugin" / "marketplace.json")

    assert version
    assert plugin_manifest["version"] == version
    assert marketplace_manifest["plugins"][0]["version"] == version


def test_installers_support_version_selection_and_latest_resolution():
    expectations = {
        "opencode/install.sh": [
            "VIBEFLOW_VERSION",
            "releases/latest",
            "git clone --depth 1 --branch",
        ],
        "claude-code/install.sh": [
            "VIBEFLOW_VERSION",
            "releases/latest",
            "archive/refs/${ARCHIVE_KIND}/${RESOLVED_REF}.zip",
        ],
        "claude-code/install.ps1": [
            "$env:VIBEFLOW_VERSION",
            "releases/latest",
            "git clone --depth 1 --branch $ResolvedRef",
        ],
        "codex/install.sh": [
            "VIBEFLOW_VERSION",
            "releases/latest",
            "Restart Codex to activate new skills.",
        ],
        "codex/install.ps1": [
            "$env:VIBEFLOW_VERSION",
            "releases/latest",
            "Restart Codex to pick up the new skills.",
        ],
    }

    for relative_path, markers in expectations.items():
        text = read_text(REPO_ROOT / relative_path)
        for marker in markers:
            assert marker in text, f"{relative_path} is missing expected marker: {marker}"


def test_install_surface_is_consolidated():
    removed_paths = [
        REPO_ROOT / "install.sh",
        REPO_ROOT / "claude-code" / "install-simple.ps1",
        REPO_ROOT / "claude-code" / "install-all-in-one.ps1",
        REPO_ROOT / "claude-code" / "vibeflow-launcher.ps1",
        REPO_ROOT / "claude-code" / "INSTALL-PROMPT.md",
    ]

    for path in removed_paths:
        assert not path.exists(), f"{path} should have been removed"


def test_install_docs_show_specific_version_examples():
    doc_paths = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "README_EN.md",
    ]

    for path in doc_paths:
        text = read_text(path)
        assert "VIBEFLOW_VERSION" in text


def test_readmes_only_reference_consolidated_install_scripts():
    readmes = [REPO_ROOT / "README.md", REPO_ROOT / "README_EN.md"]
    disallowed_markers = [
        "install-simple.ps1",
        "install-all-in-one.ps1",
        "vibeflow-launcher.ps1",
        "INSTALL-PROMPT.md",
    ]

    for path in readmes:
        text = read_text(path)
        for marker in disallowed_markers:
            assert marker not in text, f"{path} should not reference {marker}"


def test_readmes_reference_all_supported_hosts():
    readmes = [REPO_ROOT / "README.md", REPO_ROOT / "README_EN.md"]
    required_markers = [
        "claude-code/install.sh",
        "claude-code/install.ps1",
        "deepwiki.com/ttttstc/vibeflow/1-vibeflow-overview",
    ]

    for path in readmes:
        text = read_text(path)
        for marker in required_markers:
            assert marker in text, f"{path} should reference {marker}"


def test_readmes_do_not_include_codex_or_opencode_install_guidance():
    readmes = [REPO_ROOT / "README.md", REPO_ROOT / "README_EN.md"]
    forbidden_markers = [
        "codex/install.sh",
        "codex/install.ps1",
        "opencode/install.sh",
    ]

    for path in readmes:
        text = read_text(path)
        for marker in forbidden_markers:
            assert marker not in text, f"{path} should not reference {marker}"


def test_readmes_navigation_prefers_deepwiki_over_local_architecture_link():
    readmes = [REPO_ROOT / "README.md", REPO_ROOT / "README_EN.md"]

    for path in readmes:
        header_slice = "\n".join(read_text(path).splitlines()[:25])
        assert "deepwiki.com/ttttstc/vibeflow/1-vibeflow-overview" in header_slice
        assert "](ARCHITECTURE.md)" not in header_slice
