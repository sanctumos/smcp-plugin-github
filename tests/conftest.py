"""
Pytest configuration and shared fixtures
"""
import json
import subprocess
from unittest.mock import MagicMock, Mock
import pytest


@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run for unit tests"""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "test output"
    mock_result.stderr = ""
    
    def mock_run(*args, **kwargs):
        return mock_result
    
    monkeypatch.setattr(subprocess, "run", mock_run)
    return mock_result


@pytest.fixture
def mock_subprocess_timeout(monkeypatch):
    """Mock subprocess.run to raise TimeoutExpired"""
    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=30)
    
    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def mock_subprocess_exception(monkeypatch):
    """Mock subprocess.run to raise a generic exception"""
    def mock_run(*args, **kwargs):
        raise Exception("Command execution failed")
    
    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def check_command_available():
    """Check if a command is available in the system"""
    def _check(cmd):
        try:
            subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                timeout=5,
                check=False
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    return _check

