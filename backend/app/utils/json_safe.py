from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic.type_adapter import TypeAdapter


T = TypeVar("T")


@dataclass(frozen=True)
class JsonParseResult:
    ok: bool
    value: Any | None
    error: str | None = None


def safe_json_loads(raw: str | bytes) -> JsonParseResult:
    """
    Parse JSON defensively.

    - Prefer orjson when installed
    - Fall back to stdlib json
    - Never raises; returns JsonParseResult
    """
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except Exception:
            return JsonParseResult(ok=False, value=None, error="Input bytes are not valid utf-8")

    try:
        import orjson  # type: ignore

        return JsonParseResult(ok=True, value=orjson.loads(raw))
    except ModuleNotFoundError:
        pass
    except Exception as e:
        return JsonParseResult(ok=False, value=None, error=f"Invalid JSON (orjson): {e}")

    try:
        return JsonParseResult(ok=True, value=json.loads(raw))
    except Exception as e:
        return JsonParseResult(ok=False, value=None, error=f"Invalid JSON (json): {e}")


def safe_parse(value: Any, as_type: type[T] | Any) -> tuple[T | None, str | None]:
    """
    Safe parse using Pydantic TypeAdapter.

    Returns (parsed, error) and never raises.
    """
    try:
        adapter = TypeAdapter(as_type)
        return adapter.validate_python(value), None
    except Exception as e:
        return None, str(e)


def safe_parse_model(value: Any, model_type: type[BaseModel]) -> tuple[BaseModel | None, str | None]:
    parsed, err = safe_parse(value, model_type)
    return parsed, err

