import json
import pathlib

dir = pathlib.Path(__file__).parent

__all__ = ["web_image_metadata"]

web_image_metadata = json.loads((dir / "web_image_metadata.json").read_text())
