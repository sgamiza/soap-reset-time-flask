from importer.fix_output_xml import close_unclosed_tags
from importer.robot_output import parse_robot_output


def test_parse_sample_robot_output():
    report = parse_robot_output("samples/robot_output.xml")
    assert report["info"]["platform_name"] == "SAMPLE_RU"
    assert report["period"]["rru_reset_detected"] == 5
    assert report["period"]["rru_reset_enable"] == 40
    assert report["period"]["rru_reset_onair"] == 20
    assert report["period"]["rru_unLock_unLock"] == 3
    assert report["period"]["cell_unLock_onair"] == 10
    assert report["soap_results"][0]["PTP sync time between RU and DU"] == 22
    assert len(report["details"]) == 3


def test_keyword_not_found_is_zero(tmp_path):
    xml = tmp_path / "output.xml"
    xml.write_text(
        """<?xml version="1.0"?>
<robot>
  <suite>
    <test name="RU_Reset">
      <kw name="Something Else">
        <status status="PASS" starttime="20210617 03:16:48.000" endtime="20210617 03:16:49.000"/>
      </kw>
      <status status="PASS" starttime="20210617 03:16:48.000" endtime="20210617 03:16:49.000"/>
    </test>
    <status status="PASS" starttime="20210617 03:16:48.000" endtime="20210617 03:16:49.000"/>
  </suite>
</robot>
""",
        encoding="utf-8",
    )
    report = parse_robot_output(xml)
    assert report["period"]["rru_reset_detected"] == 0


def test_close_unclosed_tags():
    raw = '<robot>\n<suite>\n<test name="x">\n'
    fixed = close_unclosed_tags(raw, timeout_minutes=1)
    assert "</test>" in fixed
    assert "</suite>" in fixed
    assert "</robot>" in fixed
