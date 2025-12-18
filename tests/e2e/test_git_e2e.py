"""
End-to-end tests for git plugin
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
from cli import main


@pytest.mark.e2e
@pytest.mark.requires_git
class TestGitE2E:
    """End-to-end tests for git plugin CLI"""
    
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
        assert output["plugin"]["name"] == "git"
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
        assert "git" in result["command"]
        assert "version" in result["command"]
        assert "elapsed" in result
    
    def test_cli_run_dry_run(self, capsys):
        """Test CLI run --dry-run end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "run", "--dry-run", "--command", "status"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["dry_run"] is True
        assert "git status" in result["command"]
    
    def test_cli_run_status_in_repo(self, capsys, temp_git_repo):
        """Test CLI run status in git repo end-to-end"""
        from unittest.mock import patch
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            with patch("sys.argv", ["cli.py", "run", "--command", "status"]):
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0
            
            captured = capsys.readouterr()
            result = json.loads(captured.out)
            assert result["return_code"] == 0
            assert "git status" in result["command"]
            assert "elapsed" in result
        finally:
            os.chdir(old_cwd)
    
    def test_cli_run_with_args(self, capsys):
        """Test CLI run with command and args end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "run", "--command", "config", "--args", "--list"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "git config" in result["command"]
        assert "--list" in result["command"]
        assert "elapsed" in result
    
    def test_cli_run_empty_args(self, capsys):
        """Test CLI run with no args end-to-end"""
        from unittest.mock import patch
        with patch("sys.argv", ["cli.py", "run"]):
            try:
                main()
            except SystemExit as e:
                # May be 0 or 1 depending on git help output
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
    
    def test_cli_run_log_with_multiple_args(self, capsys, temp_git_repo):
        """Test CLI run log with multiple args end-to-end"""
        from unittest.mock import patch
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            # Create a commit for log to show
            with open(os.path.join(temp_git_repo, "test.txt"), "w") as f:
                f.write("test")
            subprocess.run(
                ["git", "add", "test.txt"],
                cwd=temp_git_repo,
                capture_output=True,
                check=False
            )
            subprocess.run(
                ["git", "commit", "-m", "test commit"],
                cwd=temp_git_repo,
                capture_output=True,
                check=False
            )
            
            with patch("sys.argv", ["cli.py", "run", "--command", "log", "--args", "--oneline", "-5"]):
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0
            
            captured = capsys.readouterr()
            result = json.loads(captured.out)
            assert result["return_code"] == 0
            assert "git log" in result["command"]
            assert "--oneline" in result["command"]
            assert "-5" in result["command"]
        finally:
            os.chdir(old_cwd)

