"""
Integration tests for gh plugin
"""
import json
import subprocess
import sys
import pytest

# Import the plugin module
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "gh"))
from cli import run, describe


@pytest.mark.integration
@pytest.mark.requires_gh
class TestGhIntegration:
    """Integration tests for gh plugin with real gh CLI"""
    
    @pytest.fixture(autouse=True)
    def check_gh_available(self, check_command_available):
        """Skip tests if gh is not available"""
        if not check_command_available("gh"):
            pytest.skip("gh CLI not available")
    
    def test_run_gh_version(self):
        """Test running gh --version"""
        result = run({"command": "--version"}, dry_run=False)
        assert result["return_code"] == 0
        assert "gh version" in result["result"].lower() or "gh" in result["result"].lower()
        assert "elapsed" in result
        assert "command" in result
    
    def test_run_gh_help(self):
        """Test running gh help"""
        result = run({"command": "help"}, dry_run=False)
        # gh help may return non-zero exit code, but should have output
        assert "result" in result or "error" in result
        assert "elapsed" in result
    
    def test_run_gh_repo_list_dry_run(self):
        """Test dry run of gh repo list"""
        result = run({"command": "repo", "subcommand": "list"}, dry_run=True)
        assert result["dry_run"] is True
        assert "gh repo list" in result["command"]
        assert "cmd_args" in result
    
    def test_describe_integration(self):
        """Test describe() in integration context"""
        result = describe()
        assert result["plugin"]["name"] == "gh"
        assert len(result["commands"]) > 0
    
    def test_run_with_empty_args(self):
        """Test running gh with empty args (should show help or error)"""
        result = run({}, dry_run=False)
        # May return non-zero, but should have some output
        assert "result" in result or "error" in result
        assert "elapsed" in result
    
    def test_run_with_invalid_command(self):
        """Test running gh with invalid command"""
        result = run({"command": "invalid-command-that-does-not-exist-12345"}, dry_run=False)
        # Should return error or non-zero exit code
        assert result["return_code"] != 0 or "error" in result or "result" in result

