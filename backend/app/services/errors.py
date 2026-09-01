"""Domain errors raised by services and mapped to user-friendly API responses."""


class CartivaError(Exception):
    """Base class. `message` is safe to show to end users."""

    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProductNotFound(CartivaError):
    status_code = 404


class InsufficientStock(CartivaError):
    status_code = 409


class UsageLimitReached(CartivaError):
    status_code = 402


class BundleNotPossible(CartivaError):
    status_code = 422


class InvalidRequest(CartivaError):
    status_code = 400
