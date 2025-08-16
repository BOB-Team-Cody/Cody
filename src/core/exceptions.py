"""Custom exceptions for Code Weaver."""


class CodeWeaverError(Exception):
    """Base exception for Code Weaver."""
    pass


class AnalysisError(CodeWeaverError):
    """Raised when code analysis fails."""
    pass


class DatabaseError(CodeWeaverError):
    """Raised when database operations fail."""
    pass


class ConfigError(CodeWeaverError):
    """Raised when configuration is invalid."""
    pass


class FileProcessingError(CodeWeaverError):
    """Raised when file processing fails."""
    pass