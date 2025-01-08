from src.exceptions import AppException


class DatabaseNotFoundException(AppException):
    def __init__(self, database: str):
        super().__init__(f"Database '{database}' not found.")
