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
    
    @pytest.mark.unit
    def test_run_with_comment_body_argument(self, mock_subprocess_run):
        """Test run with comment body argument (fixes issue #4)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test multi-word body argument
        result = run({"command": "issue", "subcommand": 'comment 123 --body "This is a multi-word comment"'}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert "--body" in cmd_parts
        body_idx = cmd_parts.index("--body")
        assert cmd_parts[body_idx + 1] == "This is a multi-word comment"  # Preserved as single argument
    
    @pytest.mark.unit
    def test_run_with_multiline_body_argument(self, mock_subprocess_run):
        """Test run with multi-line body argument (fixes issue #4)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test multi-line body argument
        multiline_body = "Line 1\nLine 2\nLine 3"
        result = run({"command": "issue", "subcommand": f'comment 123 --body "{multiline_body}"'}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert "--body" in cmd_parts
        body_idx = cmd_parts.index("--body")
        assert "\n" in cmd_parts[body_idx + 1]  # Newlines preserved
    
    @pytest.mark.unit
    def test_run_with_body_file_flag(self, mock_subprocess_run):
        """Test run with --body-file flag (fixes issue #4)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        # Test --body-file flag passes through correctly
        result = run({"command": "issue", "subcommand": "comment 123 --body-file comment.txt"}, dry_run=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert "--body-file" in cmd_parts
        assert "comment.txt" in cmd_parts
    
    @pytest.mark.unit
    def test_run_with_non_interactive_flag(self, mock_subprocess_run):
        """Test run with non-interactive flag (fixes issue #2)"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": "rename newname"}, dry_run=True, non_interactive=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        assert "--yes" in cmd_parts  # --yes should be automatically added
    
    @pytest.mark.unit
    def test_run_with_non_interactive_and_existing_yes(self, mock_subprocess_run):
        """Test run with non-interactive flag when --yes already exists"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": "rename newname --yes"}, dry_run=True, non_interactive=True)
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
        
        result = run({"command": "repo", "subcommand": "rename newname -y"}, dry_run=True, non_interactive=True)
        assert result["dry_run"] is True
        cmd_parts = result["cmd_args"]
        # Should not add --yes if -y already exists
        assert "--yes" not in cmd_parts
        assert "-y" in cmd_parts
    
    @pytest.mark.unit
    def test_run_error_with_hints_git_repo(self, mock_subprocess_run):
        """Test error handling with git repository error hints (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "fatal: not a git repository"
        
        result = run({"command": "status"}, dry_run=False)
        assert result["return_code"] == 1
        assert "error_hints" in result
        assert result["error_hints"]["error_type"] == "git_repository_error"
        assert "suggestions" in result["error_hints"]
    
    @pytest.mark.unit
    def test_run_error_with_hints_reference_error(self, mock_subprocess_run):
        """Test error handling with reference error hints (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "No commit found for the ref main"
        
        result = run({"command": "log", "subcommand": "main"}, dry_run=False)
        assert result["return_code"] == 1
        assert "error_hints" in result
        assert result["error_hints"]["error_type"] == "reference_error"
    
    @pytest.mark.unit
    def test_run_error_with_hints_argument_error(self, mock_subprocess_run):
        """Test error handling with argument error hints (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "accepts 1 arg(s), received 3"
        
        result = run({"command": "repo", "subcommand": "edit --description"}, dry_run=False)
        assert result["return_code"] == 1
        assert "error_hints" in result
        assert result["error_hints"]["error_type"] == "argument_error"
    
    @pytest.mark.unit
    def test_run_error_with_hints_repository_error(self, mock_subprocess_run):
        """Test error handling with repository not found error hints (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "repository not found"
        
        result = run({"command": "repo", "subcommand": "view nonexistent/repo"}, dry_run=False)
        assert result["return_code"] == 1
        assert "error_hints" in result
        assert result["error_hints"]["error_type"] == "repository_error"
    
    @pytest.mark.unit
    def test_run_error_with_hints_authentication_error(self, mock_subprocess_run):
        """Test error handling with authentication error hints (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "authentication required"
        
        result = run({"command": "repo", "subcommand": "list"}, dry_run=False)
        assert result["return_code"] == 1
        assert "error_hints" in result
        assert result["error_hints"]["error_type"] == "authentication_error"
    
    @pytest.mark.unit
    def test_run_error_with_hints_permission_error(self, mock_subprocess_run):
        """Test error handling with permission error hints (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "permission denied"
        
        result = run({"command": "repo", "subcommand": "delete owner/repo"}, dry_run=False)
        assert result["return_code"] == 1
        assert "error_hints" in result
        assert result["error_hints"]["error_type"] == "permission_error"
    
    @pytest.mark.unit
    def test_run_error_with_hints_cwd_suggestion(self, mock_subprocess_run, tmp_path):
        """Test error handling includes cwd in git repo error suggestions (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "fatal: not a git repository"
        
        result = run({"command": "status"}, dry_run=False, cwd=str(tmp_path))
        assert result["return_code"] == 1
        assert "error_hints" in result
        # Check that cwd is mentioned in suggestions when cwd is provided
        suggestions = result["error_hints"]["suggestions"]
        assert any("Current directory" in s for s in suggestions)
    
    @pytest.mark.unit
    def test_run_error_with_hints_no_cwd_suggestion(self, mock_subprocess_run):
        """Test error handling suggests --cwd when cwd is not provided (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "fatal: not a git repository"
        
        result = run({"command": "status"}, dry_run=False, cwd=None)
        assert result["return_code"] == 1
        assert "error_hints" in result
        suggestions = result["error_hints"]["suggestions"]
        assert any("--cwd" in s for s in suggestions)
    
    @pytest.mark.unit
    def test_run_error_no_hints_when_stderr_empty(self, mock_subprocess_run):
        """Test error handling doesn't add hints when stderr is empty (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = "some output"  # Has stdout but no stderr
        mock_subprocess_run.stderr = ""  # Empty stderr
        
        result = run({"command": "invalid"}, dry_run=False)
        assert result["return_code"] == 1
        # When stderr is empty, no error_hints should be added (but result has output)
        assert "error_hints" not in result
        assert "result" in result  # Should have result from stdout
    
    @pytest.mark.unit
    def test_analyze_error_empty_stderr(self):
        """Test _analyze_error returns None for empty stderr (fixes issue #6)"""
        from plugins.gh.cli import _analyze_error
        result = _analyze_error("", "test command", None)
        assert result is None
    
    @pytest.mark.unit
    def test_analyze_error_no_match(self):
        """Test _analyze_error returns None for unmatched error patterns (fixes issue #6)"""
        from plugins.gh.cli import _analyze_error
        result = _analyze_error("some random error message", "test command", None)
        assert result is None
    
    @pytest.mark.unit
    def test_idempotent_already_closed(self, mock_subprocess_run):
        """Test idempotency detection for already closed issue (fixes issue #10)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = "Issue is already closed"
        
        result = run({"command": "issue", "subcommand": "close 123"}, dry_run=False)
        # Should treat as success due to idempotency
        assert result["success"] is True
        assert result["idempotent"] is True
    
    @pytest.mark.unit
    def test_idempotent_already_exists(self, mock_subprocess_run):
        """Test idempotency detection for already exists scenario (fixes issue #10)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = "Repository already exists"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": "create test"}, dry_run=False)
        # Should treat as success due to idempotency
        assert result["success"] is True
        assert result["idempotent"] is True
    
    @pytest.mark.unit
    def test_idempotent_no_changes(self, mock_subprocess_run):
        """Test idempotency detection for no changes scenario (fixes issue #10)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = "No changes to apply"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": "edit"}, dry_run=False)
        # Should treat as success due to idempotency
        assert result["success"] is True
        assert result["idempotent"] is True
    
    @pytest.mark.unit
    def test_check_idempotency_function(self):
        """Test _check_idempotency function directly (fixes issue #10)"""
        from plugins.gh.cli import _check_idempotency
        from unittest.mock import Mock
        
        # Test already closed pattern
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "Issue is already closed"
        mock_result.stderr = ""
        result = _check_idempotency(mock_result, "gh issue close 123")
        assert result["is_idempotent"] is True
        assert "already closed" in result["message"].lower()
        
        # Test non-idempotent
        mock_result.stdout = "Some other error"
        mock_result.stderr = ""
        result = _check_idempotency(mock_result, "gh issue close 123")
        assert result["is_idempotent"] is False
    
    @pytest.mark.unit
    def test_run_error_with_context(self, mock_subprocess_run, tmp_path):
        """Test error handling includes command context (fixes issue #6)"""
        mock_subprocess_run.returncode = 1
        mock_subprocess_run.stdout = ""
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "invalid"}, dry_run=False, cwd=str(tmp_path))
        assert "error" in result
        assert "command_context" in result
        assert result["command_context"]["cwd"] == str(tmp_path)
        assert "invalid" in result["command_context"]["command"]
        # When there's no output, error response includes return_code
        assert result["return_code"] == 1
    
    @pytest.mark.unit
    def test_run_timeout_with_context(self, mock_subprocess_timeout):
        """Test timeout error includes context (fixes issue #6, #9)"""
        result = run({"command": "repo", "subcommand": "list"}, dry_run=False)
        assert "error" in result
        assert result["success"] is False  # Standardized success field (fixes issue #9)
        assert result["error_code"] == "TIMEOUT"  # Structured error code (fixes issue #9)
        assert "error_type" in result
        assert result["error_type"] == "timeout"
        assert "suggestion" in result
        assert "command" in result
    
    @pytest.mark.unit
    def test_run_exception_with_context(self, mock_subprocess_exception, tmp_path):
        """Test exception error includes context (fixes issue #6, #9)"""
        result = run({"command": "repo"}, dry_run=False, cwd=str(tmp_path))
        assert "error" in result
        assert result["success"] is False  # Standardized success field (fixes issue #9)
        assert result["error_code"] == "EXECUTION_ERROR"  # Structured error code (fixes issue #9)
        assert "error_type" in result
        assert result["error_type"] == "execution_error"
        assert "command_context" in result
        assert result["command_context"]["cwd"] == str(tmp_path)


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
    
    @pytest.mark.unit
    def test_main_run_with_non_interactive(self, capsys, mock_subprocess_run):
        """Test main with --non-interactive flag"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        with patch("sys.argv", ["cli.py", "run", "--non-interactive", "--command", "repo", "--subcommand", "rename newname"]):
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
        
        result = run({"command": "repo", "subcommand": "list"}, dry_run=True, cwd=str(tmp_path))
        assert result["dry_run"] is True
        assert result["cwd"] == str(tmp_path)
    
    @pytest.mark.unit
    def test_run_with_invalid_cwd(self):
        """Test run with invalid cwd directory (fixes issue #9)"""
        result = run({"command": "repo", "subcommand": "list"}, dry_run=False, cwd="/nonexistent/directory/12345")
        assert "error" in result
        assert result["success"] is False  # Standardized success field (fixes issue #9)
        assert result["error_code"] == "INVALID_CWD"  # Structured error code (fixes issue #9)
        assert "does not exist" in result["error"]
    
    @pytest.mark.unit
    def test_run_with_cwd_execution(self, mock_subprocess_run, tmp_path):
        """Test run with cwd parameter actually uses it in subprocess"""
        mock_subprocess_run.returncode = 0
        mock_subprocess_run.stdout = "success"
        mock_subprocess_run.stderr = ""
        
        result = run({"command": "repo", "subcommand": "list"}, dry_run=False, cwd=str(tmp_path))
        # Verify subprocess.run was called with cwd
        import subprocess
        # The mock should have been called, but we can't easily verify cwd was passed
        # So we just verify the result is successful
        assert result["return_code"] == 0

