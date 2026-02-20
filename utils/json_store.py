import json
from typing import Any, List


def append_jsonl(path, data: Any):
    """Append a JSON object as a single line."""
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")


def read_jsonl(path) -> List[Any]:
    """Read all JSON objects from a JSONL file."""
    items = []
    if not path.exists():
        return items

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except:
                pass
    return items
