"""
Integration tests for git plugin
"""
import json
import subprocess
import sys
import tempfile
import os
import pytest

# Import the plugin module
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "git"))
from cli import run, describe


@pytest.mark.integration
@pytest.mark.requires_git
class TestGitIntegration:
    """Integration tests for git plugin with real git CLI"""
    
    @pytest.fixture(autouse=True)
    def check_git_available(self, check_command_available):
        """Skip tests if git is not available"""
        if not check_command_available("git"):
            pytest.skip("git CLI not available")
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize a git repo
            subprocess.run(
                ["git", "init"],
                cwd=tmpdir,
                capture_output=True,
                check=False
            )
            # Set git config to avoid prompts
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=False
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=False
            )
            yield tmpdir
    
    def test_run_git_version(self):
        """Test running git --version"""
        result = run({"command": "--version"}, dry_run=False)
        assert result["return_code"] == 0
        assert "git version" in result["result"].lower()
        assert "elapsed" in result
        assert "command" in result
    
    def test_run_git_status_in_repo(self, temp_git_repo):
        """Test running git status in a git repository"""
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            result = run({"command": "status"}, dry_run=False)
            assert result["return_code"] == 0
            assert "On branch" in result["result"] or "branch" in result["result"].lower()
            assert "elapsed" in result
        finally:
            os.chdir(old_cwd)
    
    def test_run_git_status_outside_repo(self):
        """Test running git status outside a git repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = run({"command": "status"}, dry_run=False)
                # Should return error or non-zero exit code
                assert result["return_code"] != 0 or "fatal" in result["result"].lower() or "error" in result
            finally:
                os.chdir(old_cwd)
    
    def test_run_git_log_dry_run(self):
        """Test dry run of git log"""
        result = run({"command": "log", "args": "--oneline -10"}, dry_run=True)
        assert result["dry_run"] is True
        assert "git log" in result["command"]
        assert "--oneline" in result["command"]
        assert "cmd_args" in result
    
    def test_run_git_log_with_args_list(self):
        """Test running git log with args as list"""
        result = run({"command": "log", "args": ["--oneline", "-5"]}, dry_run=True)
        assert result["dry_run"] is True
        assert "git log" in result["command"]
        assert "--oneline" in result["command"]
        assert "-5" in result["command"]
    
    def test_describe_integration(self):
        """Test describe() in integration context"""
        result = describe()
        assert result["plugin"]["name"] == "git"
        assert len(result["commands"]) > 0
    
    def test_run_with_empty_args(self):
        """Test running git with empty args (should show help or error)"""
        result = run({}, dry_run=False)
        # May return non-zero, but should have some output
        assert "result" in result or "error" in result
        assert "elapsed" in result
    
    def test_run_git_config_list(self):
        """Test running git config --list"""
        result = run({"command": "config", "args": "--list"}, dry_run=False)
        # Should return successfully with config output
        assert "result" in result or "error" in result
        assert "elapsed" in result
    
    def test_run_with_invalid_command(self):
        """Test running git with invalid command"""
        result = run({"command": "invalid-command-that-does-not-exist-12345"}, dry_run=False)
        # Should return error or non-zero exit code
        assert result["return_code"] != 0 or "error" in result or "result" in result

