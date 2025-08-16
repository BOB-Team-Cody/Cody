"""File handling utilities."""

from pathlib import Path
from typing import List, Set
import os


# Default excluded directories and files
EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".pytest_cache",
    ".coverage",
    "build",
    "dist",
    ".tox",
    ".mypy_cache"
}

EXCLUDED_FILE_PATTERNS = {
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.egg-info"
}


def find_python_files(project_path: Path, max_files: int = 1000) -> List[Path]:
    """Find all Python files in the project directory.
    
    Args:
        project_path: Root path to search
        max_files: Maximum number of files to return
        
    Returns:
        List of Python file paths
    """
    python_files = []
    
    for py_file in project_path.rglob("*.py"):
        if is_excluded_file(py_file):
            continue
            
        # Check file size (skip very large files)
        try:
            if py_file.stat().st_size > 1024 * 1024:  # 1MB
                continue
        except OSError:
            continue
            
        python_files.append(py_file)
        
        # Limit the number of files to prevent memory issues
        if len(python_files) >= max_files:
            break
    
    return python_files


def is_excluded_file(file_path: Path) -> bool:
    """Check if a file should be excluded from analysis.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file should be excluded
    """
    # Check if any parent directory is excluded
    for part in file_path.parts:
        if part in EXCLUDED_DIRS:
            return True
    
    # Check filename patterns
    filename = file_path.name
    if filename.startswith('.'):
        return True
    
    # Check if it's a test file (optional exclusion)
    if 'test' in filename.lower() and filename.startswith('test_'):
        return False  # Include test files for now
    
    return False


def get_relative_path(file_path: Path, project_root: Path) -> Path:
    """Get relative path from project root.
    
    Args:
        file_path: Absolute file path
        project_root: Project root path
        
    Returns:
        Relative path
    """
    try:
        return file_path.relative_to(project_root)
    except ValueError:
        # If file is outside project root, return absolute path
        return file_path


def safe_read_file(file_path: Path, encoding: str = 'utf-8') -> str:
    """Safely read file content with fallback encodings.
    
    Args:
        file_path: Path to file
        encoding: Primary encoding to try
        
    Returns:
        File content as string
        
    Raises:
        UnicodeDecodeError: If file cannot be decoded
    """
    encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise UnicodeDecodeError(f"Could not decode {file_path} with any encoding")