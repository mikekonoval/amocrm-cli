class AmoCRMAPIError(Exception):
    def __init__(self, status: int, title: str, detail: str) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        super().__init__(f"[{status}] {title}: {detail}")


class EntityNotFoundError(AmoCRMAPIError):
    """Raised when the API returns 204 on a GET or single-resource PATCH."""

    def __init__(self, path: str) -> None:
        super().__init__(404, "Not Found", f"Entity not found at {path}")
        self.path = path
