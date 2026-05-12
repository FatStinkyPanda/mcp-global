#!/usr/bin/env python3
"""
MCP Virtual Environment Manager
Automatically detects, creates, and enforces Python 3.11.x virtual environment usage.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class VenvManager:
    """Manages Python 3.11.x virtual environment for MCP projects."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.venv_path = self.project_root / ".venv"
        self.venv_config = self.project_root / ".mcp" / "venv_config.json"
        self.required_version = (3, 11)
        self.fallback_to_current = True  # Allow using current Python if 3.11 not found

    def find_python_311(self) -> str | None:
        """Find Python 3.11.x executable."""
        candidates = [
            "python3.11",
            "python311",
            "python3",
            "python",
        ]

        # Also check common installation paths
        if sys.platform == "win32":
            candidates.extend([
                r"C:\Python311\python.exe",
                r"C:\Program Files\Python311\python.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe"),
            ])
        else:
            candidates.extend([
                "/usr/bin/python3.11",
                "/usr/local/bin/python3.11",
                os.path.expanduser("~/.pyenv/versions/3.11.*/bin/python"),
            ])

        for candidate in candidates:
            try:
                result = subprocess.run(
                    [candidate, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version_str = result.stdout.strip()
                    if "Python 3.11" in version_str:
                        return candidate
                    # Check actual version
                    version_output = subprocess.run(
                        [candidate, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if version_output.returncode == 0:
                        major, minor = map(int, version_output.stdout.strip().split('.'))
                        if (major, minor) == self.required_version:
                            return candidate
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                continue

        return None

    def check_venv_exists(self) -> bool:
        """Check if virtual environment exists and is valid."""
        if not self.venv_path.exists():
            return False

        # Check for python executable
        if sys.platform == "win32":
            python_exe = self.venv_path / "Scripts" / "python.exe"
        else:
            python_exe = self.venv_path / "bin" / "python"

        if not python_exe.exists():
            return False

        # Verify it's Python 3.11.x
        try:
            result = subprocess.run(
                [str(python_exe), "-c",
                 "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                major, minor = map(int, result.stdout.strip().split('.'))
                return (major, minor) == self.required_version
        except Exception:
            pass

        return False

    def create_venv(self) -> bool:
        """Create Python 3.11.x virtual environment."""
        python_311 = self.find_python_311()

        if not python_311:
            if self.fallback_to_current:
                print("[MCP VENV WARN] Python 3.11.x not found!")
                print("[MCP VENV] Falling back to current Python version...")
                # Use current Python
                python_311 = sys.executable
                print(f"[MCP VENV] Using: {python_311} (version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})")
            else:
                print("[MCP VENV ERROR] Python 3.11.x not found on system!")
                print("Please install Python 3.11.x from python.org")
                return False

        print(f"[MCP VENV] Creating virtual environment with {python_311}...")

        try:
            # Remove existing venv if corrupted
            if self.venv_path.exists():
                import shutil
                shutil.rmtree(self.venv_path)

            # Create new venv
            subprocess.run(
                [python_311, "-m", "venv", str(self.venv_path)],
                check=True,
                timeout=60
            )

            print(f"[MCP VENV] [OK] Virtual environment created: {self.venv_path}")

            # Upgrade pip
            self._run_in_venv(["python", "-m", "pip", "install", "--upgrade", "pip"])

            # Install basic requirements if they exist
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                print("[MCP VENV] Installing requirements.txt...")
                self._run_in_venv(["pip", "install", "-r", "requirements.txt"])

            # Save config
            self._save_config(python_311)

            return True

        except subprocess.CalledProcessError as e:
            print(f"[MCP VENV ERROR] Failed to create venv: {e}")
            return False
        except Exception as e:
            print(f"[MCP VENV ERROR] Unexpected error: {e}")
            return False

    def _run_in_venv(self, command: list) -> subprocess.CompletedProcess:
        """Run command in virtual environment."""
        if sys.platform == "win32":
            python_exe = self.venv_path / "Scripts" / "python.exe"
            pip_exe = self.venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = self.venv_path / "bin" / "python"
            pip_exe = self.venv_path / "bin" / "pip"

        # Replace python/pip in command with venv executables
        if command[0] == "python":
            command[0] = str(python_exe)
        elif command[0] == "pip":
            command[0] = str(pip_exe)

        return subprocess.run(command, check=True, timeout=300)

    def _save_config(self, python_path: str):
        """Save venv configuration."""
        self.venv_config.parent.mkdir(exist_ok=True)

        config = {
            "venv_path": str(self.venv_path),
            "python_version": f"{self.required_version[0]}.{self.required_version[1]}",
            "python_executable": python_path,
            "created_at": subprocess.run(
                ["date", "-Iseconds"],
                capture_output=True,
                text=True
            ).stdout.strip() if sys.platform != "win32" else None
        }

        with open(self.venv_config, 'w') as f:
            json.dump(config, f, indent=2)

    def ensure_venv(self) -> bool:
        """Ensure virtual environment exists and is ready."""
        if self.check_venv_exists():
            print(f"[MCP VENV] [OK] Virtual environment ready: {self.venv_path}")
            return True

        print("[MCP VENV] Virtual environment not found or invalid")
        return self.create_venv()

    def get_venv_python(self) -> str:
        """Get path to venv Python executable."""
        if sys.platform == "win32":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")

    def activate_venv_command(self) -> str:
        """Get command to activate venv in shell."""
        if sys.platform == "win32":
            return f".venv\\Scripts\\activate"
        else:
            return "source .venv/bin/activate"

    def check_in_venv(self) -> bool:
        """Check if currently running in the venv."""
        return (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Virtual Environment Manager")
    parser.add_argument("command", choices=["check", "create", "ensure", "info"],
                       help="Command to execute")
    parser.add_argument("--project-root", default=".",
                       help="Project root directory")

    args = parser.parse_args()

    manager = VenvManager(args.project_root)

    if args.command == "check":
        exists = manager.check_venv_exists()
        print(f"Virtual environment exists: {exists}")
        sys.exit(0 if exists else 1)

    elif args.command == "create":
        success = manager.create_venv()
        sys.exit(0 if success else 1)

    elif args.command == "ensure":
        success = manager.ensure_venv()
        sys.exit(0 if success else 1)

    elif args.command == "info":
        print(f"Project root: {manager.project_root}")
        print(f"Venv path: {manager.venv_path}")
        print(f"Venv exists: {manager.check_venv_exists()}")
        print(f"Currently in venv: {manager.check_in_venv()}")
        if manager.check_venv_exists():
            print(f"Python executable: {manager.get_venv_python()}")
            print(f"Activate command: {manager.activate_venv_command()}")


if __name__ == "__main__":
    main()
