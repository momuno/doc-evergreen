"""
Integration tests for doc-evergreen CLI installation and entry point.

Tests verify that after installation, the doc-evergreen command is available
and works correctly from any directory.
"""

import subprocess


class TestCLIInstallation:
    """Test CLI entry point is correctly installed and accessible."""

    def test_cli_help_command_is_available(self):
        """
        Given: doc-evergreen is installed via uv
        When: Running 'uv run doc-evergreen --help'
        Then: Command executes successfully with exit code 0
        """
        result = subprocess.run(
            ["uv", "run", "doc-evergreen", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_help_output_contains_command_name(self):
        """
        Given: doc-evergreen CLI is available
        When: Running '--help' command
        Then: Output contains 'doc-evergreen' command name
        """
        result = subprocess.run(
            ["uv", "run", "doc-evergreen", "--help"],
            capture_output=True,
            text=True,
        )

        output = result.stdout.lower()
        assert "doc-evergreen" in output

    def test_regen_doc_subcommand_exists(self):
        """
        Given: doc-evergreen CLI is available
        When: Running 'doc-evergreen regen-doc --help'
        Then: Command executes successfully showing regen-doc subcommand help
        """
        result = subprocess.run(
            ["uv", "run", "doc-evergreen", "regen-doc", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout.lower()
        assert "regen-doc" in output

    def test_command_works_from_different_directory(self, tmp_path):
        """
        Given: doc-evergreen is installed
        When: Running command from a different directory (not installation dir)
        Then: Command still works and returns help successfully
        """
        # Create and change to temp directory
        test_dir = tmp_path / "test_run"
        test_dir.mkdir()

        result = subprocess.run(
            ["uv", "run", "doc-evergreen", "--help"],
            capture_output=True,
            text=True,
            cwd=test_dir,
        )

        assert result.returncode == 0
        assert "doc-evergreen" in result.stdout.lower()

    def test_invalid_subcommand_shows_error(self):
        """
        Given: doc-evergreen CLI is available
        When: Running with an invalid subcommand
        Then: Command fails with non-zero exit code and helpful error
        """
        result = subprocess.run(
            ["uv", "run", "doc-evergreen", "nonexistent-command"],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        # Error should be in stderr or stdout
        error_output = (result.stderr + result.stdout).lower()
        assert "error" in error_output or "invalid" in error_output or "usage" in error_output
