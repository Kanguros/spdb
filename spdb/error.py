class SPDBError(Exception):
    """Base exception for SPDB operations."""

    pass


class ModelLoadError(SPDBError):
    """Raised when model loading fails."""

    pass
