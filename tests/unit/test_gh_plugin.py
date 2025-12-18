"""
Unit tests for gh plugin
"""
import json
import subprocess
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest

# Import the plugin module
import os
import importlib.util
plugin_path = os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "gh", "cli.py")
spec = importlib.util.spec_from_file_location("gh_cli", plugin_path)
gh_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gh_cli)
run = gh_cli.run
describe = gh_cli.describe
main = gh_cli.main


class TestGhRun:
    """Test the run() function"""
    
    @pytest.mark.unit
    def test_run_dry_run_empty_args(self):
        """Test dry run with empty args"""
        result = run({}, dry_run=True)
        assert result["dry_run"] is True
        assert result["command"] == "gh"
        assert "cmd_args" in result
        assert "args_received" in result
    
    @pytest.mark.unit
    def test_run_dry_run_with_command(self):
        """Test dry run with command"""
        result = run({"command": "repo"}, dry_run=True)
        assert result["dry_run"] is True
        assert result["command"] == "gh repo"
    
    @pytest.mark.unit
    def test_run_dry_run_with_command_and_subcommand(self):
        """Test dry run with command and subcommand"""
        result = run({"command": "repo", "subcommand": "list"}, dry_run=True)
        assert result["dry_run"] is True
        assert result["command"] == "gh repo list"
    
    @pytest.mark.unit
    def test_run_dry_run_with_spaced_command(self):
        """Test dry run with command containing spaces"""
        result = run({"command": "repo list owner"}, dry_run=True)
        assert result["dry_run"] is True
        assert "gh repo list owner" in result["command"]
    
    @pytest.mark.unit
    def test_run_dry_run_with_spaced_subcommand(self):
        """Test dry run with subcommand containing spaces"""
        result = run({"command": "repo", "subcommand": "list --limit 10"}, dry_run=True)
        assert result["dry_run"] is True
        assert "gh repo list --limit 10" in result["command"]
    
    @pytest.mark.unit
    def test_run_success_empty_args(self, mock_subprocess_run):
        """Test successful run with empty args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "GitHub CLI output"
        mock_subprocess_run.stderr = ""
        
        result = run({}, dry_run=False)
        assert result["return_code"] == 0
        assert result["command"] == "gh"
        assert "elapsed" in result
        assert result["stdout"] == "GitHub CLI output"
        assert result["result"] == "GitHub CLI output"
    
    @pytest.mark.unit
    def test_run_success_with_command(self, mock_subprocess_run):
        """Test successful run with command"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "repo list output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo"}, dry_run=False)
        assert result["return_code"] == 0
        assert result["command"] == "gh repo"
        assert result["result"] == "repo list output"
    
    @pytest.mark.unit
    def test_run_success_with_command_and_subcommand(self, mock_subprocess_run):
        """Test successful run with command and subcommand"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "list output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": "list"}, dry_run=False)
        assert result["return_code"] == 0
        assert result["command"] == "gh repo list"
        assert result["result"] == "list output"
    
    @pytest.mark.unit
    def test_run_success_empty_output(self, mock_subprocess_run):
        """Test successful run with empty output"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo"}, dry_run=False)
        assert result["return_code"] == 0
        assert result["result"] == "Command completed successfully"
    
    @pytest.mark.unit
    def test_run_failure_with_stderr(self, mock_subprocess_run):
        """Test failed run with stderr output"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "error: unknown command"
        
        result = run({"command": "invalid"}, dry_run=False)
        assert result["return_code"] == 1
        assert result["stderr"] == "error: unknown command"
        assert result["result"] == "error: unknown command"
        assert "error" not in result
    
    @pytest.mark.unit
    def test_run_failure_with_stdout_and_stderr(self, mock_subprocess_run):
        """Test failed run with both stdout and stderr"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = "some output"
        mock_subprocess_run.stderr = "error message"
        
        result = run({"command": "repo"}, dry_run=False)
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
        result = run({"command": "repo"}, dry_run=False)
        assert "error" in result
        assert "timed out" in result["error"]
    
    @pytest.mark.unit
    def test_run_exception(self, mock_subprocess_exception):
        """Test exception handling"""
        result = run({"command": "repo"}, dry_run=False)
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
        # None values are skipped, so command should just be "gh"
        assert result["command"] == "gh"
    
    @pytest.mark.unit
    def test_run_with_none_subcommand(self, mock_subprocess_run):
        """Test run with None subcommand (should be skipped)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": None}, dry_run=False)
        assert result["return_code"] == 0
        # None values are skipped, so command should be "gh repo"
        assert result["command"] == "gh repo"
    
    @pytest.mark.unit
    def test_run_with_non_string_command(self, mock_subprocess_run):
        """Test run with non-string command"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "output"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": 123}, dry_run=False)
        assert result["return_code"] == 0
        assert "gh 123" in result["command"]
    
    @pytest.mark.unit
    def test_run_with_quoted_multi_word_argument(self, mock_subprocess_run):
        """Test run with quoted multi-word argument (fixes issue #1)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test that quoted strings are preserved as single arguments
        result = run({"command": 'repo edit --description "Python SDK and tools"', "subcommand": None}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        # Should have: ["gh", "repo", "edit", "--description", "Python SDK and tools"]
        assert cmd_parts[0] == "gh"
        assert cmd_parts[1] == "repo"
        assert cmd_parts[2] == "edit"
        assert cmd_parts[3] == "--description"
        assert cmd_parts[4] == "Python SDK and tools"  # Quoted string preserved as single arg
    
    @pytest.mark.unit
    def test_run_with_unquoted_arguments(self, mock_subprocess_run):
        """Test run with unquoted arguments (backward compatibility)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test that unquoted arguments still work
        result = run({"command": "repo list --limit 10"}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert cmd_parts == ["gh", "repo", "list", "--limit", "10"]
    
    @pytest.mark.unit
    def test_run_with_mixed_quoted_unquoted(self, mock_subprocess_run):
        """Test run with mixed quoted and unquoted arguments"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test mixed scenario
        result = run({"command": 'repo edit --description "My Project" --homepage https://example.com'}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert "gh" in cmd_parts
        assert "repo" in cmd_parts
        assert "edit" in cmd_parts
        assert "--description" in cmd_parts
        assert "My Project" in cmd_parts  # Quoted string preserved
        assert "--homepage" in cmd_parts
        assert "https://example.com" in cmd_parts
    
    @pytest.mark.unit
    def test_run_with_quoted_subcommand(self, mock_subprocess_run):
        """Test run with quoted subcommand argument"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": 'edit --description "Test Description"'}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert cmd_parts[0] == "gh"
        assert cmd_parts[1] == "repo"
        assert cmd_parts[2] == "edit"
        assert cmd_parts[3] == "--description"
        assert cmd_parts[4] == "Test Description"  # Quoted string preserved


class TestGhDescribe:
    """Test the describe() function"""
    
    @pytest.mark.unit
    def test_describe_structure(self):
        """Test describe() returns correct structure"""
        result = describe()
        assert "plugin" in result
        assert "commands" in result
        assert result["plugin"]["name"] == "gh"
        assert result["plugin"]["version"] == "1.0.0"
        assert len(result["commands"]) == 1
        assert result["commands"][0]["name"] == "run"
    
    @pytest.mark.unit
    def test_describe_plugin_info(self):
        """Test describe() plugin information"""
        result = describe()
        plugin = result["plugin"]
        assert plugin["name"] == "gh"
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
        assert "subcommand" in param_names
        
        command_param = next(p for p in params if p["name"] == "command")
        assert command_param["type"] == "string"
        assert command_param["required"] is False
        
        subcommand_param = next(p for p in params if p["name"] == "subcommand")
        assert subcommand_param["type"] == "string"
        assert subcommand_param["required"] is False


class TestGhMain:
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
        assert output["plugin"]["name"] == "gh"
    
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
        
        with patch("sys.argv", ["cli.py", "run", "--dry-run", "--command", "repo"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["dry_run"] is True
        assert "gh repo" in result["command"]
    
    @pytest.mark.unit
    def test_main_run_with_command(self, capsys, mock_subprocess_run):
        """Test main with run and command"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "repo output"
        mock_subprocess_run.stderr = ""
        
        with patch("sys.argv", ["cli.py", "run", "--command", "repo"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 0
        assert "gh repo" in result["command"]
    
    @pytest.mark.unit
    def test_main_run_with_command_and_subcommand(self, capsys, mock_subprocess_run):
        """Test main with run, command, and subcommand"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "list output"
        mock_subprocess_run.stderr = ""
        
        with patch("sys.argv", ["cli.py", "run", "--command", "repo", "--subcommand", "list"]):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 0
        assert "gh repo list" in result["command"]
    
    @pytest.mark.unit
    def test_main_run_empty_args(self, capsys, mock_subprocess_run):
        """Test main with run and no args"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "gh help"
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
             patch.object(gh_cli, "run", return_value={"error": "Unknown command: test"}):
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
        mock_subprocess_run.stderr = "error message"
        
        with patch("sys.argv", ["cli.py", "run", "--command", "invalid"]):
            try:
                main()
            except SystemExit as e:
                # When stderr has output, it's in "result" field, not "error", so exit code is 0
                assert e.code == 0
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["return_code"] == 1
        assert "error message" in result["stderr"]
        assert "error message" in result["result"]
    
    @pytest.mark.unit
    def test_main_exception_handling(self, capsys):
        """Test main exception handling"""
        with patch("sys.argv", ["cli.py", "run", "--command", "test"]), \
             patch.object(gh_cli, "run", side_effect=Exception("Test exception")):
            try:
                main()
            except SystemExit as e:
                assert e.code == 1
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "error" in result
        assert "Test exception" in result["error"]

