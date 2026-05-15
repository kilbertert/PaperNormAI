"""Business exceptions for application layer."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} not found: {identifier}", code="NOT_FOUND")
        self.resource = resource
        self.identifier = identifier


class AccessDeniedError(AppException):
    """Access denied."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(f"Access denied to {resource}: {identifier}", code="ACCESS_DENIED")
        self.resource = resource
        self.identifier = identifier


class ValidationError(AppException):
    """Validation failed."""

    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")