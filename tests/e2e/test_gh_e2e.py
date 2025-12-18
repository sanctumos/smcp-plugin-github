"""
End-to-end tests for gh plugin
"""
import json
import subprocess
import sys
import pytest

# Import the plugin module
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "gh"))
from cli import main


@pytest.mark.e2e
@pytest.mark.requires_gh
class TestGhE2E:
    """End-to-end tests for gh plugin CLI"""
    
    @pytest.fixture(autouse=True)
    def check_gh_available(self, check_command_available):
        """Skip tests if gh is not available"""
        if not check_command_available("gh"):
            pytest.skip("gh CLI not available")
    
    def test_cli_describe_flag(self, capsys):
        """Test CLI --describe flag end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "--describe"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["plugin"]["name"] == "gh"
        assert "commands" in output
    
    def test_cli_run_version(self, capsys):
        """Test CLI run --version end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "run", "--command", "--version"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 0
        assert "gh" in result["command"]
        assert "version" in result["command"]
        assert "elapsed" in result
    
    def test_cli_run_dry_run(self, capsys):
        """Test CLI run --dry-run end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "run", "--dry-run", "--command", "repo", "--subcommand", "list"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["dry_run"] is True
        assert "gh repo list" in result["command"]
    
    def test_cli_run_with_subcommand(self, capsys):
        """Test CLI run with command and subcommand end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "run", "--command", "repo", "--subcommand", "view"]):
            try:
                main()
            except SystemExit as e:
                # May be 0 or 1 depending on authentication/context
                assert e.code in [0, 1]
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "gh repo view" in result["command"]
        assert "elapsed" in result
    
    def test_cli_run_empty_args(self, capsys):
        """Test CLI run with no args end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "run"]):
            try:
                main()
            except SystemExit as e:
                # May be 0 or 1 depending on gh help output
                assert e.code in [0, 1]
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "command" in result
        assert "elapsed" in result
    
    def test_cli_unknown_command(self, capsys):
        """Test CLI with unknown command end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "unknown"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 1
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "error" in result
        assert "Unknown command" in result["error"]

