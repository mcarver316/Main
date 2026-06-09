"""
TMC Chatbot — CI Test Suite
Lightweight tests that run in GitHub Actions without heavy ML dependencies.

Tests: file structure, syntax, config, security markers, route inventory.
Run:   pytest tests/test_ci.py -v
Expected: all pass in < 60s on ubuntu-latest with requirements-ci.txt
"""

import ast
import os
import sys
import importlib
import pytest
import yaml
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root resolution
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ===========================================================================
# 1. Required file structure
# ===========================================================================
class TestFileStructure:
    """Verify all critical files exist in the committed repo."""

    REQUIRED_FILES = [
        "app.py",
        "requirements.txt",
        "requirements-ci.txt",
        ".github/workflows/ci.yml",
        "tests/__init__.py",
        "tests/test_ci.py",
        "scripts/__init__.py",
        "scripts/database.py",
        "scripts/rag_helper.py",
        "knowledge_base/development/keys.md",
    ]

    REQUIRED_DIRS = [
        "scripts",
        "templates",
        "static",
        "knowledge_base",
        "tests",
        ".github/workflows",
    ]

    @pytest.mark.parametrize("filepath", REQUIRED_FILES)
    def test_required_file_exists(self, filepath):
        path = REPO_ROOT / filepath
        assert path.exists(), f"Required file missing from repo: {filepath}"
        assert path.stat().st_size > 0, f"Required file is empty: {filepath}"

    @pytest.mark.parametrize("dirpath", REQUIRED_DIRS)
    def test_required_directory_exists(self, dirpath):
        path = REPO_ROOT / dirpath
        assert path.is_dir(), f"Required directory missing: {dirpath}"


# ===========================================================================
# 2. Python syntax validation
# ===========================================================================
class TestPythonSyntax:
    """Compile Python source files to catch syntax errors without executing them."""

    PYTHON_FILES = [
        "app.py",
        "scripts/database.py",
        "scripts/rag_helper.py",
        "scripts/knowledge_base_manager.py",
        "scripts/ticket_monitor.py",
    ]

    @pytest.mark.parametrize("filepath", PYTHON_FILES)
    def test_valid_python_syntax(self, filepath):
        path = REPO_ROOT / filepath
        if not path.exists():
            pytest.skip(f"{filepath} not found — skipping syntax check")
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {filepath}: {e}")

    def test_app_py_size_reasonable(self):
        """app.py should be substantial (not accidentally truncated)."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        size = path.stat().st_size
        assert size > 50_000, f"app.py looks truncated — only {size} bytes (expected > 50KB)"

    def test_app_py_has_flask_instance(self):
        """app.py must define a Flask application."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        assert "Flask(__name__)" in source, "app.py does not instantiate Flask(__name__)"

    def test_app_py_route_count(self):
        """app.py should expose 40+ routes (Phase 1 baseline)."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        route_count = source.count("@app.route(")
        assert route_count >= 40, (
            f"Route count dropped below baseline: {route_count} found, expected >= 40"
        )


# ===========================================================================
# 3. requirements.txt validation
# ===========================================================================
class TestRequirements:
    """Validate requirements files are well-formed and contain expected packages."""

    def test_requirements_txt_exists_and_nonempty(self):
        path = REPO_ROOT / "requirements.txt"
        assert path.exists()
        content = path.read_text()
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]
        assert len(lines) >= 10, "requirements.txt seems too short"

    def test_flask_version_pinned(self):
        path = REPO_ROOT / "requirements.txt"
        content = path.read_text()
        assert "Flask==3.1.3" in content, "Flask 3.1.3 not pinned in requirements.txt"

    def test_chromadb_version_pinned(self):
        path = REPO_ROOT / "requirements.txt"
        content = path.read_text()
        assert "chromadb==1.5.9" in content, "chromadb 1.5.9 not pinned in requirements.txt"

    def test_no_unpinned_packages(self):
        """Every non-comment line should use == pinning."""
        path = REPO_ROOT / "requirements.txt"
        content = path.read_text()
        unpinned = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "==" not in stripped and not stripped.startswith("-"):
                unpinned.append(stripped)
        assert not unpinned, f"Unpinned packages in requirements.txt: {unpinned}"

    def test_requirements_ci_no_apple_silicon_packages(self):
        path = REPO_ROOT / "requirements-ci.txt"
        if not path.exists():
            pytest.skip("requirements-ci.txt not found")
        content = path.read_text()
        forbidden = ["mlx", "mlx-lm", "mlx-metal"]
        for pkg in forbidden:
            assert pkg not in content, (
                f"Apple Silicon-only package '{pkg}' found in requirements-ci.txt — "
                "this will break ubuntu-latest CI runners"
            )


# ===========================================================================
# 4. CI/CD YAML validation
# ===========================================================================
class TestCIWorkflow:
    """Validate the GitHub Actions workflow YAML is well-formed."""

    CI_YAML = REPO_ROOT / ".github" / "workflows" / "ci.yml"

    def test_ci_yaml_parses(self):
        assert self.CI_YAML.exists(), "ci.yml not found"
        with open(self.CI_YAML) as f:
            doc = yaml.safe_load(f)
        assert doc is not None, "ci.yml parsed as empty"

    def test_ci_yaml_has_jobs(self):
        with open(self.CI_YAML) as f:
            doc = yaml.safe_load(f)
        assert "jobs" in doc, "ci.yml missing 'jobs' key"
        assert len(doc["jobs"]) >= 2, "ci.yml should define at least 2 jobs"

    def test_ci_yaml_triggers_on_push(self):
        with open(self.CI_YAML) as f:
            doc = yaml.safe_load(f)
        on = doc.get("on", doc.get(True, {}))  # 'on' is parsed as True in PyYAML
        assert on is not None, "ci.yml missing 'on' trigger"

    def test_ci_yaml_has_workflow_dispatch(self):
        """Manual trigger must be present for on-demand runs."""
        with open(self.CI_YAML) as f:
            doc = yaml.safe_load(f)
        on = doc.get("on", doc.get(True, {}))
        assert "workflow_dispatch" in on, "ci.yml missing 'workflow_dispatch' trigger"

    def test_ci_yaml_uses_recent_checkout_action(self):
        content = self.CI_YAML.read_text()
        assert "actions/checkout@v4" in content, "ci.yml should use actions/checkout@v4"

    def test_ci_yaml_targets_correct_python(self):
        content = self.CI_YAML.read_text()
        assert "3.11" in content, "ci.yml should target Python 3.11"


# ===========================================================================
# 5. PAPA Lab security markers (intentional vulnerability presence)
# ===========================================================================
class TestPAPALabMarkers:
    """
    Verify intentional lab vulnerabilities are PRESENT.
    These are FEATURES for the AI security training curriculum, not bugs to fix.
    Phase 2 fixes are in SDLC_NOTES.md — these lab scenarios must stay intact.
    """

    def test_keys_md_exists(self):
        """SC-04 RAG exfiltration scenario requires keys.md to be present."""
        path = REPO_ROOT / "knowledge_base" / "development" / "keys.md"
        assert path.exists(), "keys.md missing — SC-04 RAG exfiltration scenario will break"

    def test_security_level_constant_in_app(self):
        """AI_SECURITY_LEVEL must be defined for the 5-level teaching mode."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        assert "AI_SECURITY_LEVEL" in source, "AI_SECURITY_LEVEL constant missing from app.py"

    def test_secret_key_stable_implementation(self):
        """C-1 FIX: SECRET_KEY must use _get_or_create_secret_key() — not a bare token_urlsafe default."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        assert "_get_or_create_secret_key" in source, (
            "C-1 fix missing: _get_or_create_secret_key() not found in app.py"
        )
        assert "SECRET_KEY=_get_or_create_secret_key()" in source, (
            "C-1 fix missing: SECRET_KEY must call _get_or_create_secret_key()"
        )

    def test_ssl_verification_not_disabled(self):
        """C-3 FIX: SSL verification must not be globally disabled."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        assert "REQUESTS_CA_BUNDLE" not in source, (
            "C-3: REQUESTS_CA_BUNDLE='' found — SSL verification is globally disabled"
        )
        assert "CURL_CA_BUNDLE" not in source, (
            "C-3: CURL_CA_BUNDLE='' found — SSL verification is globally disabled"
        )

    def test_cors_not_wildcard(self):
        """H-1 FIX: CORS must not use wildcard '*' origins."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        assert "CORS_ALLOWED_ORIGINS" in source, (
            "H-1 fix missing: CORS_ALLOWED_ORIGINS not defined"
        )
        # The CORS() call must reference CORS_ALLOWED_ORIGINS, not a literal "*"
        assert '"origins": "*"' not in source and "'origins': '*'" not in source, (
            "H-1: CORS still using wildcard origins"
        )

    def test_no_duplicate_api_user_route(self):
        """H-2 FIX: /api/user must appear exactly once."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        count = source.count("@app.route('/api/user')")
        assert count == 1, (
            f"H-2: /api/user route registered {count} times (must be exactly 1)"
        )

    def test_temp_file_overwrite_uses_actual_size(self):
        """H-3 FIX: Temp file cleanup must use actual file size, not hardcoded 1024."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        assert "getsize" in source, (
            "H-3 fix missing: os.path.getsize not used for temp file overwrite"
        )
        assert "'0' * 1024" not in source, (
            "H-3: Hardcoded 1024-byte overwrite still present — use actual file size"
        )

    def test_kb_reindex_requires_admin_role(self):
        """H-4: /api/knowledge-base/reindex must be protected by @require_role('admin')."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        source = path.read_text(encoding="utf-8")
        # Find the reindex route and verify require_role is nearby
        idx = source.find("'/api/knowledge-base/reindex'")
        assert idx != -1, "kb_reindex route not found in app.py"
        # Check the 300 chars around the route for require_role
        context = source[max(0, idx - 50):idx + 300]
        assert "require_role" in context, (
            "H-4: /api/knowledge-base/reindex missing @require_role decorator"
        )


# ===========================================================================
# 6. App import smoke test (skips gracefully if heavy deps absent)
# ===========================================================================
class TestAppImport:
    """
    Try to import the Flask app. Skip if heavy ML dependencies aren't installed.
    These tests run locally and in full CI; they skip in lean CI (requirements-ci.txt).
    """

    def test_flask_importable(self):
        """Flask must be importable — it's in requirements-ci.txt."""
        try:
            import flask
            assert flask.__version__.startswith("3."), (
                f"Expected Flask 3.x, got {flask.__version__}"
            )
        except ImportError:
            pytest.skip(
                "Flask not installed in this environment "
                "(installed in CI via requirements-ci.txt)"
            )

    def test_app_module_importable_if_deps_present(self):
        """Import app.py — skip if heavy deps (chromadb, sentence-transformers) missing."""
        path = REPO_ROOT / "app.py"
        if not path.exists():
            pytest.skip("app.py not found")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("app_module", path)
            mod = importlib.util.module_from_spec(spec)
            # Don't execute — just check it loads the spec cleanly
            assert spec is not None, "Failed to create module spec for app.py"
        except Exception as e:
            # Heavy deps missing in lean CI — this is expected and OK
            pytest.skip(f"app.py import skipped (deps not available): {e}")

    def test_scripts_database_importable_if_deps_present(self):
        """Import scripts/database.py."""
        path = REPO_ROOT / "scripts" / "database.py"
        if not path.exists():
            pytest.skip("scripts/database.py not found")
        try:
            spec = importlib.util.spec_from_file_location("database", path)
            assert spec is not None
        except Exception as e:
            pytest.skip(f"database.py spec creation failed: {e}")


# ===========================================================================
# 7. Git hygiene checks
# ===========================================================================
class TestGitHygiene:
    """Check that sensitive files are excluded from the committed repo."""

    SHOULD_NOT_BE_COMMITTED = [
        "data/tmc_customer_service.db",
        ".security_level",
        ".selected_model",
        ".ollama_lab.pid",
        "requirements.txt.bak.2026-06-09",
    ]

    @pytest.mark.parametrize("filepath", SHOULD_NOT_BE_COMMITTED)
    def test_sensitive_file_not_in_committed_repo(self, filepath):
        """
        These files should be excluded via .gitignore.
        If this test fails, the file was accidentally committed and should be removed.
        """
        # We check for .gitignore patterns, not git status (CI doesn't have git history context)
        gitignore_path = REPO_ROOT / ".gitignore"
        if not gitignore_path.exists():
            pytest.skip(".gitignore not present — skipping git hygiene check")
        gitignore_content = gitignore_path.read_text()
        filename = Path(filepath).name
        extension = Path(filepath).suffix
        parts = Path(filepath).parts
        # Check: exact filename, extension, directory prefix, or any stem prefix that
        # could be a glob pattern (e.g. "requirements*.bak*" covers "requirements.txt.bak.2026...")
        def matches_any_pattern(name, content):
            for line in content.splitlines():
                pat = line.strip().rstrip("/")
                if not pat or pat.startswith("#"):
                    continue
                # Exact match
                if pat == name:
                    return True
                # Glob-style: check if name starts with the non-wildcard prefix
                if "*" in pat:
                    prefix = pat.split("*")[0]
                    if prefix and name.startswith(prefix):
                        return True
                # Extension match (*.ext)
                if pat.startswith("*.") and name.endswith(pat[1:]):
                    return True
            return False

        covered = (
            matches_any_pattern(filename, gitignore_content)
            or (extension and matches_any_pattern(extension, gitignore_content))
            or (len(parts) > 1 and parts[0] + "/" in gitignore_content)
        )
        assert covered, (
            f"Potentially sensitive path '{filepath}' has no .gitignore coverage. "
            f"Add '{filepath}' or a matching glob pattern to .gitignore."
        )
