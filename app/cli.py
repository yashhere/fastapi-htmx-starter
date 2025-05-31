import subprocess
import sys


def serve_command():
    """Start the development server."""
    print("Starting development server...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        check=True,
    )


def test_command():
    """Run tests."""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest"], check=True)


def lint_command():
    """Lint the code."""
    print("Linting code...")
    subprocess.run([sys.executable, "-m", "ruff", "check", "app/"], check=True)
    subprocess.run([sys.executable, "-m", "mypy", "app/"], check=True)


def format_command():
    """Format the code."""
    print("Formatting code...")
    subprocess.run([sys.executable, "-m", "black", "app/"], check=True)
    subprocess.run([sys.executable, "-m", "ruff", "check", "--fix", "app/"], check=True)
    subprocess.run([sys.executable, "-m", "isort", "app/"], check=True)


def check_types_command():
    """Check types with mypy."""
    print("Checking types...")
    subprocess.run([sys.executable, "-m", "mypy", "app/"], check=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "serve":
            serve_command()
        elif command == "test":
            test_command()
        elif command == "lint":
            lint_command()
        elif command == "format":
            format_command()
        elif command == "check-types":
            check_types_command()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        print("Available commands: serve, test, lint, format, check-types")
        sys.exit(1)
