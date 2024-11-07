import json
import pathlib

dir = pathlib.Path(__file__).parent

__all__ = ["search_onepiece"]

search_onepiece = json.loads((dir / "search_onepiece.json").read_text())
parse_onepiece = json.loads((dir / "parse_onepiece.json").read_text())
