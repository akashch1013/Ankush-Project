"""Readable JSON: short lists of numbers/strings stay on one line, so layout files
remain easy for people (and agents) to read and diff."""
from __future__ import annotations

import json
from pathlib import Path


def _inline(v) -> bool:
    return isinstance(v, list) and len(v) <= 8 and all(isinstance(x, (int, float, str, bool)) or x is None for x in v) \
        and len(json.dumps(v, ensure_ascii=False)) <= 90


def dumps(obj, indent: int = 2, _level: int = 0) -> str:
    pad = " " * (indent * (_level + 1))
    end = " " * (indent * _level)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = [f"{pad}{json.dumps(k, ensure_ascii=False)}: {dumps(v, indent, _level + 1)}" for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + end + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        if _inline(obj):
            return json.dumps(obj, ensure_ascii=False)
        items = [f"{pad}{dumps(v, indent, _level + 1)}" for v in obj]
        return "[\n" + ",\n".join(items) + "\n" + end + "]"
    return json.dumps(obj, ensure_ascii=False)


def write(path: Path, obj) -> None:
    Path(path).write_text(dumps(obj) + "\n", encoding="utf-8")


def read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
