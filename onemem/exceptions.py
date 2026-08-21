"""oneMEM exception hierarchy."""


class OneMemError(Exception):
    """Base exception for all oneMEM errors."""


class ModelUnavailableError(OneMemError):
    """Raised when an LLM or embedding model is persistently unavailable."""


class EmbeddingDimensionMismatchError(OneMemError):
    """Raised when embedding dimensions disagree across config, provider, or DB."""


class EmbeddingBackendUnavailableError(OneMemError):
    """Raised when a configured embedding provider lacks a vector backend."""


class DuplicateEventError(OneMemError):
    """Raised internally when a duplicate event is detected."""


class DatabaseError(OneMemError):
    """Raised for unrecoverable database setup or schema errors."""


class SpendCeilingError(OneMemError):
    """Raised when a bulk extraction run's estimated token cost exceeds the ceiling."""
