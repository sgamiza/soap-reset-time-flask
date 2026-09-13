"""Discover SOAP OAM logs from xml / gz / nested zip without writing lab leftovers."""

from __future__ import annotations

import gzip
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Union

RFLOG_ZIP_RE = re.compile(r"rflog.*\d{6}\.zip$", re.IGNORECASE)
SOAP_XML_RE = re.compile(r"(soap_log|UnitOAM_SOAP.*Log\d+)\.xml$", re.IGNORECASE)
SOAP_GZ_RE = re.compile(r"UnitOAM_SOAP.*Log\d+\.xml\.gz$", re.IGNORECASE)
INNER_ZIP_NAMES = {"1011_UnitOAM_SOAP_Log.zip"}


def _is_unsafe_zip_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    return normalized.startswith("/") or ".." in Path(normalized).parts


def _basename(name: str) -> str:
    return Path(name.replace("\\", "/")).name


def is_soap_xml_name(name: str) -> bool:
    base = _basename(name)
    return bool(SOAP_XML_RE.search(base)) or base.lower() == "soap_log.xml"


def is_soap_gz_name(name: str) -> bool:
    return bool(SOAP_GZ_RE.search(_basename(name)))


def is_inner_soap_zip(name: str) -> bool:
    base = _basename(name)
    return base in INNER_ZIP_NAMES or ("SOAP" in base.upper() and base.lower().endswith(".zip"))


def read_gz_text(path: Union[str, Path]) -> str:
    with gzip.open(path, "rb") as handle:
        return handle.read().decode("utf-8", errors="replace")


def _extract_zip_members(zip_path: Path, dest: Path) -> None:
    with zipfile.ZipFile(zip_path) as src:
        for name in src.namelist():
            if _is_unsafe_zip_name(name):
                continue
            base = _basename(name)
            interesting = is_soap_xml_name(base) or is_soap_gz_name(base) or is_inner_soap_zip(name)
            if not interesting:
                continue
            src.extract(name, dest)
            extracted = dest / name
            if extracted.suffix.lower() == ".zip":
                _extract_zip_members(extracted, dest)


def _first_file(root: Path, predicate) -> Optional[Path]:
    matches = sorted(p for p in root.rglob("*") if p.is_file() and predicate(p.name))
    return matches[0] if matches else None


def load_soap_text(path: Union[str, Path]) -> str:
    """Return SOAP log text from an xml file, gz, zip, or a directory that contains one."""
    target = Path(path)
    if target.is_file():
        name = target.name
        if name.lower().endswith(".xml"):
            return target.read_text(encoding="utf-8", errors="replace")
        if name.lower().endswith(".gz"):
            return read_gz_text(target)
        if name.lower().endswith(".zip"):
            with tempfile.TemporaryDirectory(prefix="soap-log-") as tmp:
                tmp_path = Path(tmp)
                _extract_zip_members(target, tmp_path)
                xml_file = _first_file(tmp_path, is_soap_xml_name)
                if xml_file:
                    return xml_file.read_text(encoding="utf-8", errors="replace")
                gz_file = _first_file(tmp_path, is_soap_gz_name)
                if gz_file:
                    return read_gz_text(gz_file)
            raise FileNotFoundError("no SOAP xml/gz inside zip: %s" % target)
        raise ValueError("unsupported SOAP log file: %s" % target)

    if not target.is_dir():
        raise FileNotFoundError(path)

    xml_file = _first_file(target, is_soap_xml_name)
    if xml_file:
        return xml_file.read_text(encoding="utf-8", errors="replace")
    gz_file = _first_file(target, is_soap_gz_name)
    if gz_file:
        return read_gz_text(gz_file)
    for candidate in sorted(target.iterdir()):
        if candidate.is_file() and RFLOG_ZIP_RE.match(candidate.name):
            return load_soap_text(candidate)
    raise FileNotFoundError("rflog_xxxxxx.zip, UnitOAM SOAP xml, or soap_log.xml")
