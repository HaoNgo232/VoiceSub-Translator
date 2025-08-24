#!/usr/bin/env python3
"""
Test script to verify setup.sh functionality
"""

import os
import subprocess
import sys
from pathlib import Path

def test_setup_script_exists():
    """Test if setup.sh exists and is executable"""
    setup_path = Path("setup.sh")
    assert setup_path.exists(), "setup.sh does not exist"
    assert os.access(setup_path, os.X_OK), "setup.sh is not executable"
    print("✓ setup.sh exists and is executable")

def test_bash_syntax():
    """Test if setup.sh has valid bash syntax"""
    result = subprocess.run(["bash", "-n", "setup.sh"], capture_output=True, text=True)
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"
    print("✓ setup.sh has valid bash syntax")

def test_requirements_updated():
    """Test if requirements.txt contains the missing dependencies"""
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    required_packages = ["backoff", "redis", "openai", "python-dotenv"]
    for package in required_packages:
        assert package in content, f"Missing required package: {package}"
    
    print("✓ requirements.txt contains necessary dependencies")

def test_helper_scripts_creation():
    """Test if running setup.sh would create helper scripts"""
    # We can't run the full setup due to network limitations,
    # but we can verify the script contains the necessary creation commands
    with open("setup.sh", "r") as f:
        content = f.read()
    
    assert "run.sh" in content, "setup.sh doesn't create run.sh"
    assert "test_installation.sh" in content, "setup.sh doesn't create test_installation.sh"
    assert "update_dependencies.sh" in content, "setup.sh doesn't create update_dependencies.sh"
    
    print("✓ setup.sh contains helper script creation logic")

def test_gpu_detection():
    """Test if setup.sh contains GPU detection logic"""
    with open("setup.sh", "r") as f:
        content = f.read()
    
    assert "nvidia-smi" in content, "setup.sh doesn't check for NVIDIA GPU"
    assert "GPU_SUPPORT" in content, "setup.sh doesn't set GPU_SUPPORT variable"
    
    print("✓ setup.sh contains GPU detection logic")

def test_virtual_environment_setup():
    """Test if setup.sh contains virtual environment setup"""
    with open("setup.sh", "r") as f:
        content = f.read()
    
    assert "-m venv" in content, "setup.sh doesn't create virtual environment"
    assert "source" in content and "activate" in content, "setup.sh doesn't activate virtual environment"
    
    print("✓ setup.sh contains virtual environment setup logic")

def test_dependency_conflict_resolution():
    """Test if setup.sh contains dependency conflict resolution"""
    with open("setup.sh", "r") as f:
        content = f.read()
    
    assert "pip install --upgrade" in content, "setup.sh doesn't upgrade packages to resolve conflicts"
    assert "typing-extensions" in content, "setup.sh doesn't handle typing-extensions conflicts"
    
    print("✓ setup.sh contains dependency conflict resolution")

def main():
    """Run all tests"""
    print("Testing VoiceSub-Translator setup.sh functionality...")
    print("=" * 50)
    
    tests = [
        test_setup_script_exists,
        test_bash_syntax,
        test_requirements_updated,
        test_helper_scripts_creation,
        test_gpu_detection,
        test_virtual_environment_setup,
        test_dependency_conflict_resolution,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("🎉 All tests passed! Setup script is ready for use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup script.")
        return 1

if __name__ == "__main__":
    sys.exit(main())