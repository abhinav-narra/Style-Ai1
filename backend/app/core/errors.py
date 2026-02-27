from __future__ import annotations


class AppError(Exception):
    """Base application error (safe to log)."""


class DependencyMissingError(AppError):
    def __init__(self, dependency: str, hint: str | None = None):
        self.dependency = dependency
        self.hint = hint
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.hint:
            return f"Missing dependency: {self.dependency}. {self.hint}"
        return f"Missing dependency: {self.dependency}"


class InvalidInputError(AppError):
    pass

