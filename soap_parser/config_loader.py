"""Load timing-rule JSON shipped with the project."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "soap_parser_config.json"


def load_parser_config(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    candidates = []
    if path:
        candidates.append(Path(path))
    env_path = os.environ.get("SOAP_PARSER_CONFIG")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(DEFAULT_CONFIG)
    candidates.append(Path.cwd() / "soap_parser_config.json")
    for candidate in candidates:
        if candidate.is_file():
            with candidate.open(encoding="utf-8") as handle:
                return json.load(handle)
    raise FileNotFoundError("soap_parser_config.json")
