# Python Skill — Quick-Start Reference

A one-page cheat sheet for the deep agent. Read `instructions.md` for the full workflow.

## Must-Follow Rules
| Rule | Do | Don't |
|------|----|-------|
| Typing | `def fn(x: int) -> str:` | Untyped signatures |
| Exceptions | `except ValueError:` | `except:` or `except Exception:` |
| Strings | f-strings | `%s` or `.format()` |
| Paths | `pathlib.Path` | `os.path.join` |
| Structured data | `dataclass` / Pydantic | Raw `dict` nesting |
| Style | PEP 8, snake_case, 4-space | camelCase, tabs |

## Minimal Correct Function Shape
```python
from typing import Any

def process(data: list[dict[str, Any]], limit: int = 10) -> list[str]:
    """One-line summary.

    Args:
        data: Input records.
        limit: Max items to return.

    Returns:
        List of processed strings.

    Raises:
        ValueError: If data is empty.
    """
    if not data:
        raise ValueError("data must not be empty")
    return [str(item) for item in data[:limit]]
```

## Decision Shortcuts
- **List of unknown items** → `list[T]`
- **Key-value mapping** → `dict[str, T]` or a `dataclass`
- **Optional field** → `T | None` (Python 3.10+)
- **I/O concurrency** → `async`/`await` + `httpx.AsyncClient`
- **CPU concurrency** → `multiprocessing` or `asyncio.to_thread`
- **Config / env** → `pydantic-settings` or `python-dotenv`

## Test Naming
`test_<function>_<scenario>` → e.g., `test_process_empty_data_raises_value_error`
