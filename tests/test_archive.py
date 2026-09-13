import gzip
import zipfile
from pathlib import Path

import pytest

from soap_parser.archive import load_soap_text
from soap_parser.sample_log import build_sample_soap_log


def test_load_xml_file(tmp_path):
    path = tmp_path / "soap_log.xml"
    path.write_text(build_sample_soap_log(), encoding="utf-8")
    assert "moduleReadyAck" in load_soap_text(path)


def test_load_directory(tmp_path):
    (tmp_path / "soap_log.xml").write_text(build_sample_soap_log(), encoding="utf-8")
    assert "PtpStatus" in load_soap_text(tmp_path)


def test_nested_zip_and_gz(tmp_path):
    xml_name = "UnitOAM_SOAP_Log0.xml"
    gz_path = tmp_path / (xml_name + ".gz")
    with gzip.open(gz_path, "wb") as handle:
        handle.write(build_sample_soap_log().encode("utf-8"))
    inner_zip = tmp_path / "1011_UnitOAM_SOAP_Log.zip"
    with zipfile.ZipFile(inner_zip, "w") as zf:
        zf.write(gz_path, arcname="UnitOAM_SOAP_Log0.xml.gz")
    outer = tmp_path / "rflog_20210617_031648.zip"
    with zipfile.ZipFile(outer, "w") as zf:
        zf.write(inner_zip, arcname="1011_UnitOAM_SOAP_Log.zip")
    text = load_soap_text(outer)
    assert "TxArrayCarrier" in text


def test_zip_slip_ignored(tmp_path):
    evil = tmp_path / "rflog_20210617_031648.zip"
    with zipfile.ZipFile(evil, "w") as zf:
        zf.writestr("../escape.xml", "<bad/>")
        zf.writestr("soap_log.xml", build_sample_soap_log())
    text = load_soap_text(evil)
    assert "moduleReadyAck" in text
    assert not (tmp_path.parent / "escape.xml").exists()


def test_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_soap_text(tmp_path)
