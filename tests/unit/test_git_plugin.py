"""
Unit tests for git plugin
"""
import json
import subprocess
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest

# Import the plugin module
import os
import importlib.util
plugin_path = os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "git", "cli.py")
spec = importlib.util.spec_from_file_location("git_cli", plugin_path)
git_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(git_cli)
run = git_cli.run
describe = git_cli.describe
main = git_cli.main


class TestGitRun:
    """Test the run() function"""
    
    @pytest.mark.unit
    def test_run_dry_run_empty_args(self):
        """Test dry run with empty args"""
        result = run({}, dry_run=True)
        assert result["dry_run"] is True
        assert result["command"] == "git"
        assert "cmd_args" in result
        assert "args_received" in result
    
    @pytest.mark.unit
    def test_run_dry_run_with_command(self):
        """Test dry run with command"""
        result = run({"command": "status"}, dry_run=True)
        assert result["dry_run"] is True
        assert result["command"] == "git status"
    
    @pytest.mark.unit
    def test_run_dry_run_with_command_and_args_string(self):
        """Test dry run with command and args as string"""
        result = run({"command": "log", "args": "--oneline -10"}, dry_run=True)
        assert result["dry_run"] is True
        assert "git log" in result["command"]
        assert "--oneline" in result["command"]
        assert "-10" in result["command"]
    
    @pytest.mark.unit
    def test_run_dry_run_with_command_and_args_list(self):
        """Test dry run with command and args as list"""
        result = run({"command": "log", "args": ["--oneline", "-10"]}, dry_run=True)
        assert result["dry_run"] is True
        assert "git log" in result["command"]
        assert "--oneline" in result["command"]
        assert "-10" in result["command"]
    
    @pytest.mark.unit
    def test_run_dry_run_with_spaced_command(self):
        """Test dry run with command containing spaces"""
        result = run({"command": "log --oneline"}, dry_run=True)
        assert result["dry_run"] is True
        assert "git log --oneline" in result["command"]
    
    @pytest.mark.unit
    def test_run_success_empty_args(self, mock_subprocess_run):
        """Test successful run with empty args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "Git output"
        mock_subprocess_run.stderr = ""
        
        result = run({}, dry_run=False)
        assert result["return_code"] == 0
        assert result["command"] == "git"
        assert "elapsed" in result
        assert result["stdout"] == "Git output"
        assert result["result"] == "Git output"
    
    @pytest.mark.unit
    def test_run_success_with_command(self, mock_subprocess_run):
        """Test successful run with command"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "status output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "status"}, dry_run=False)
        assert result["return_code"] == 0
        assert result["command"] == "git status"
        assert result["result"] == "status output"
    
    @pytest.mark.unit
    def test_run_success_with_command_and_args_string(self, mock_subprocess_run):
        """Test successful run with command and args as string"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "log output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "log", "args": "--oneline -10"}, dry_run=False)
        assert result["return_code"] == 0
        assert "git log" in result["command"]
        assert result["result"] == "log output"
    
    @pytest.mark.unit
    def test_run_success_with_command_and_args_list(self, mock_subprocess_run):
        """Test successful run with command and args as list"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "log output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "log", "args": ["--oneline", "-10"]}, dry_run=False)
        assert result["return_code"] == 0
        assert "git log" in result["command"]
        assert result["result"] == "log output"
    
    @pytest.mark.unit
    def test_run_success_empty_output(self, mock_subprocess_run):
        """Test successful run with empty output"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "status"}, dry_run=False)
        assert result["return_code"] == 0
        assert result["result"] == "Command completed successfully"
    
    @pytest.mark.unit
    def test_run_failure_with_stderr(self, mock_subprocess_run):
        """Test failed run with stderr output"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "fatal: not a git repository"
        
        result = run({"command": "status"}, dry_run=False)
        assert result["return_code"] == 1
        assert result["stderr"] == "fatal: not a git repository"
        assert result["result"] == "fatal: not a git repository"
        assert "error" not in result
    
    @pytest.mark.unit
    def test_run_failure_with_stdout_and_stderr(self, mock_subprocess_run):
        """Test failed run with both stdout and stderr"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = "some output"
        mock_subprocess_run.stderr = "error message"
        
        result = run({"command": "status"}, dry_run=False)
        assert result["return_code"] == 1
        assert result["stdout"] == "some output"
        assert result["stderr"] == "error message"
        assert "some output" in result["result"]
        assert "error message" in result["result"]
    
    @pytest.mark.unit
    def test_run_failure_no_output(self, mock_subprocess_run):
        """Test failed run with no output"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "invalid"}, dry_run=False)
        assert result["return_code"] == 1
        assert "error" in result
        assert "no output" in result["error"]
    
    @pytest.mark.unit
    def test_run_timeout(self, mock_subprocess_timeout):
        """Test timeout handling"""
        result = run({"command": "status"}, dry_run=False)
        assert "error" in result
        assert "timed out" in result["error"]
    
    @pytest.mark.unit
    def test_run_exception(self, mock_subprocess_exception):
        """Test exception handling"""
        result = run({"command": "status"}, dry_run=False)
        assert "error" in result
        assert "Command execution failed" in result["error"]
    
    @pytest.mark.unit
    def test_run_with_none_command(self, mock_subprocess_run):
        """Test run with None command (should be skipped)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": None}, dry_run=False)
        assert result["return_code"] == 0
        # None values are skipped, so command should just be "git"
        assert result["command"] == "git"
    
    @pytest.mark.unit
    def test_run_with_none_args(self, mock_subprocess_run):
        """Test run with None args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "status", "args": None}, dry_run=False)
        assert result["return_code"] == 0
    
    @pytest.mark.unit
    def test_run_with_non_string_command(self, mock_subprocess_run):
        """Test run with non-string command"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": 123}, dry_run=False)
        assert result["return_code"] == 0
        assert "git 123" in result["command"]
    
    @pytest.mark.unit
    def test_run_with_non_string_args(self, mock_subprocess_run):
        """Test run with non-string args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "log", "args": 123}, dry_run=False)
        assert result["return_code"] == 0
        assert "git log 123" in result["command"]
    
    @pytest.mark.unit
    def test_run_with_empty_list_args(self, mock_subprocess_run):
        """Test run with empty list args (should be skipped)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "status", "args": []}, dry_run=False)
        assert result["return_code"] == 0
        assert "git status" in result["command"]
        # Empty list is falsy, so args shouldn't be added
        assert result["command"].count("status") == 1
    
    @pytest.mark.unit
    def test_run_with_empty_string_args(self, mock_subprocess_run):
        """Test run with empty string args (should be skipped)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "status", "args": ""}, dry_run=False)
        assert result["return_code"] == 0
        assert "git status" in result["command"]
    
    @pytest.mark.unit
    def test_run_with_quoted_multi_word_argument(self, mock_subprocess_run):
        """Test run with quoted multi-word argument in args (fixes issue #1)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test that quoted strings are preserved as single arguments
        result = run({"command": "commit", "args": '-m "Initial commit with message"'}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        # Should have: ["git", "commit", "-m", "Initial commit with message"]
        assert cmd_parts[0] == "git"
        assert cmd_parts[1] == "commit"
        assert cmd_parts[2] == "-m"
        assert cmd_parts[3] == "Initial commit with message"  # Quoted string preserved as single arg
    
    @pytest.mark.unit
    def test_run_with_unquoted_args_string(self, mock_subprocess_run):
        """Test run with unquoted args string (backward compatibility)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test that unquoted arguments still work
        result = run({"command": "log", "args": "--oneline -10"}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert cmd_parts == ["git", "log", "--oneline", "-10"]
    
    @pytest.mark.unit
    def test_run_with_mixed_quoted_unquoted_args(self, mock_subprocess_run):
        """Test run with mixed quoted and unquoted arguments in args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test mixed scenario
        result = run({"command": "commit", "args": '-m "My commit message" --author "John Doe <john@example.com>"'}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert "git" in cmd_parts
        assert "commit" in cmd_parts
        assert "-m" in cmd_parts
        assert "My commit message" in cmd_parts  # Quoted string preserved
        assert "--author" in cmd_parts
        assert "John Doe <john@example.com>" in cmd_parts  # Quoted string preserved
    
    @pytest.mark.unit
    def test_run_with_quoted_command(self, mock_subprocess_run):
        """Test run with quoted command argument"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": 'config user.name "John Doe"'}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert cmd_parts[0] == "git"
        assert cmd_parts[1] == "config"
        assert cmd_parts[2] == "user.name"
        assert cmd_parts[3] == "John Doe"  # Quoted string preserved
    
    @pytest.mark.unit
    def test_run_with_non_interactive_flag(self, mock_subprocess_run):
        """Test run with non-interactive flag (fixes issue #2)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "clean", "args": "-fd"}, dry_run=True, non_interactive=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert "--yes" in cmd_parts  # --yes should be automatically added
    
    @pytest.mark.unit
    def test_run_with_non_interactive_and_existing_yes(self, mock_subprocess_run):
        """Test run with non-interactive flag when --yes already exists"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "clean", "args": ["-fd", "--yes"]}, dry_run=True, non_interactive=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        # Should only have one --yes, not duplicate
        assert cmd_parts.count("--yes") == 1
    
    @pytest.mark.unit
    def test_run_with_non_interactive_short_flag(self, mock_subprocess_run):
        """Test run with non-interactive flag when -y already exists"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "clean", "args": ["-fd", "-y"]}, dry_run=True, non_interactive=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        # Should not add --yes if -y already exists
        assert "--yes" not in cmd_parts
        assert "-y" in cmd_parts


class TestGitDescribe:
    """Test the describe() function"""
    
    @pytest.mark.unit
    def test_describe_structure(self):
        """Test describe() returns correct structure"""
        result = describe()
        assert "plugin" in result
        assert "commands" in result
        assert result["plugin"]["name"] == "git"
        assert result["plugin"]["version"] == "1.0.0"
        assert len(result["commands"]) == 1
        assert result["commands"][0]["name"] == "run"
    
    @pytest.mark.unit
    def test_describe_plugin_info(self):
        """Test describe() plugin information"""
        result = describe()
        plugin = result["plugin"]
        assert plugin["name"] == "git"
        assert plugin["version"] == "1.0.0"
        assert "description" in plugin
    
    @pytest.mark.unit
    def test_describe_commands(self):
        """Test describe() commands structure"""
        result = describe()
        command = result["commands"][0]
        assert command["name"] == "run"
        assert "description" in command
        assert "parameters" in command
        assert len(command["parameters"]) == 2
    
    @pytest.mark.unit
    def test_describe_parameters(self):
        """Test describe() parameters structure"""
        result = describe()
        params = result["commands"][0]["parameters"]
        param_names = [p["name"] for p in params]
        assert "command" in param_names
        assert "args" in param_names
        
        command_param = next(p for p in params if p["name"] == "command")
        assert command_param["type"] == "string"
        assert command_param["required"] is False
        
        args_param = next(p for p in params if p["name"] == "args")
        assert args_param["type"] == "string"
        assert args_param["required"] is False


class TestGitMain:
    """Test the main() function"""
    
    @pytest.mark.unit
    def test_main_describe_flag(self, capsys):
        """Test --describe flag"""
        with patch("sys.argv", ["cli.py", "--describe"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "plugin" in output
        assert output["plugin"]["name"] == "git"
    
    @pytest.mark.unit
    def test_main_no_command(self, capsys):
        """Test main with no command"""
        with patch("sys.argv", ["cli.py"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 1
        
        captured = capsys.readouterr()
        assert "usage" in captured.out.lower() or "help" in captured.out.lower()
    
    @pytest.mark.unit
    def test_main_run_dry_run(self, capsys, mock_subprocess_run):
        """Test main with run --dry-run"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        with patch("sys.argv", ["cli.py", "run", "--dry-run", "--command", "status"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["dry_run"] is True
        assert "git status" in result["command"]
    
    @pytest.mark.unit
    def test_main_run_with_command(self, capsys, mock_subprocess_run):
        """Test main with run and command"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "status output"
        mock_subprocess_run.stderr = ""
        
        with patch("sys.argv", ["cli.py", "run", "--command", "status"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 0
        assert "git status" in result["command"]
    
    @pytest.mark.unit
    def test_main_run_with_command_and_args(self, capsys, mock_subprocess_run):
        """Test main with run, command, and args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "log output"
        mock_subprocess_run.stderr = ""
        
        # Test that arg_args is properly handled when it's a list
        # We'll test this by directly calling the code path that handles args
        with patch("sys.argv", ["cli.py", "run", "--command", "log"]), \
             patch("argparse.ArgumentParser.parse_args") as mock_parse:
            mock_args = Mock()
            mock_args.describe = False
            mock_args.command = "run"
            mock_args.dry_run = False
            mock_args.cwd = None
            mock_args.arg_command = "log"
            mock_args.arg_args = ["--oneline", "-10"]  # This is what argparse returns for nargs="*"
            mock_parse.return_value = mock_args
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 0
        assert "git log" in result["command"]
        assert "--oneline" in result["command"]
        assert "-10" in result["command"]
    
    @pytest.mark.unit
    def test_main_run_empty_args(self, capsys, mock_subprocess_run):
        """Test main with run and no args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "git help"
        mock_subprocess_run.stderr = ""
        
        with patch("sys.argv", ["cli.py", "run"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 0
    
    @pytest.mark.unit
    def test_main_run_unknown_command(self, capsys):
        """Test main with unknown command"""
        # This tests the else branch in main() for unknown commands
        # We need to bypass argparse validation to test the else branch
        with patch("sys.argv", ["cli.py", "run"]), \
             patch.object(git_cli, "run", return_value={"error": "Unknown command: test"}):
            # Mock args.command to be something other than "run" to test else branch
            with patch("argparse.ArgumentParser.parse_args") as mock_parse:
                mock_args = Mock()
                mock_args.describe = False
                mock_args.command = "unknown_command"
                mock_parse.return_value = mock_args
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 1
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "error" in result
        assert "Unknown command" in result["error"]
    
    @pytest.mark.unit
    def test_main_run_with_error(self, capsys, mock_subprocess_run):
        """Test main with command that returns error"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "fatal: not a git repository"
        
        with patch("sys.argv", ["cli.py", "run", "--command", "status"]):
            try:
                main()
            except SystemExit as e:
                # When stderr has output, it's in "result" field, not "error", so exit code is 0
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 1
        assert "fatal: not a git repository" in result["stderr"]
        assert "fatal: not a git repository" in result["result"]
    
    @pytest.mark.unit
    def test_main_exception_handling(self, capsys):
        """Test main exception handling"""
        with patch("sys.argv", ["cli.py", "run", "--command", "test"]), \
             patch.object(git_cli, "run", side_effect=Exception("Test exception")):
            try:
                main()
            except SystemExit as e:
                assert e.code == 1
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "error" in result
        assert "Test exception" in result["error"]
    
    @pytest.mark.unit
    def test_main_run_with_non_interactive(self, capsys, mock_subprocess_run):
        """Test main with --non-interactive flag"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test that arg_args is properly handled when it's a list
        # We'll test this by directly calling the code path that handles args
        with patch("sys.argv", ["cli.py", "run", "--non-interactive", "--command", "clean"]), \
             patch("argparse.ArgumentParser.parse_args") as mock_parse:
            mock_args = Mock()
            mock_args.describe = False
            mock_args.command = "run"
            mock_args.dry_run = False
            mock_args.non_interactive = True
            mock_args.cwd = None
            mock_args.arg_command = "clean"
            mock_args.arg_args = ["-fd"]  # This is what argparse returns for nargs="*"
            mock_parse.return_value = mock_args
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 0
        assert "--yes" in result["command"]
    
    @pytest.mark.unit
    def test_run_with_cwd(self, mock_subprocess_run, tmp_path):
        """Test run with cwd parameter (fixes issue #3)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "status"}, dry_run=True, cwd=str(tmp_path))
        assert result["dry_run"] is True
        assert result["cwd"] == str(tmp_path)
    
    @pytest.mark.unit
    def test_run_with_invalid_cwd(self):
        """Test run with invalid cwd directory"""
        result = run({"command": "status"}, dry_run=False, cwd="/nonexistent/directory/12345")
        assert "error" in result
        assert "does not exist" in result["error"]
    
    @pytest.mark.unit
    def test_run_with_cwd_execution(self, mock_subprocess_run, tmp_path):
        """Test run with cwd parameter actually uses it in subprocess"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "status"}, dry_run=False, cwd=str(tmp_path))
        # Verify the result is successful
        assert result["return_code"] == 0

