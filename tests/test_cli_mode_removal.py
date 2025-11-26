"""
Sprint 1.1: Tests to verify single-shot mode removal

These tests ensure that:
1. The --mode flag no longer exists in doc-update command
2. The mode parameter is removed from doc_update function
3. single_generator import is removed
4. Mode-related docstring references are removed
"""

import inspect
from pathlib import Path

from click.testing import CliRunner

from doc_evergreen.cli import cli, doc_update


class TestModeRemoval:
    """Test that mode-related code has been removed"""

    def test_no_mode_flag_in_help(self):
        """--mode flag should not exist in doc-update command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ["doc-update", "--help"])
        assert result.exit_code == 0
        assert "--mode" not in result.output.lower(), "Found --mode flag in help output"

    def test_no_mode_parameter_in_signature(self):
        """doc_update function should not accept mode parameter"""
        sig = inspect.signature(doc_update)
        assert "mode" not in sig.parameters, "Found 'mode' parameter in doc_update signature"

    def test_no_single_generator_import(self):
        """Should not import single_generator module"""
        cli_file = Path("src/doc_evergreen/cli.py")
        content = cli_file.read_text()
        assert "single_generator" not in content.lower(), "Found 'single_generator' reference in cli.py"

    def test_no_mode_in_docstring_line_4(self):
        """Line 4 docstring should not mention both modes"""
        cli_file = Path("src/doc_evergreen/cli.py")
        lines = cli_file.read_text().split("\n")
        # Line 4 (index 3) should not mention "single-shot and chunked"
        assert "single-shot" not in lines[3].lower(), "Found 'single-shot' in line 4 docstring"

    def test_no_mode_choice_type(self):
        """Should not have Choice type for mode selection"""
        cli_file = Path("src/doc_evergreen/cli.py")
        content = cli_file.read_text()
        assert 'Choice(["single", "chunked"])' not in content, "Found mode Choice type definition"

    def test_doc_update_uses_chunked_generator_only(self):
        """doc_update should only use ChunkedGenerator, not route based on mode"""
        cli_file = Path("src/doc_evergreen/cli.py")
        content = cli_file.read_text()
        
        # Should not have mode-based routing logic
        assert 'if mode == "chunked"' not in content, "Found mode-based routing logic"
        
        # The Generator import should be gone (single-shot generator)
        lines = content.split("\n")
        for line in lines:
            if "from doc_evergreen.single_generator import Generator" in line:
                assert False, "Found import of single_generator.Generator"
