from soap_parser.config_loader import load_parser_config
from soap_parser.sample_log import build_sample_soap_log
from soap_parser.timings import get_times_from_log, measure_timings, messages_from_text


EXPECTED = {
    "PTP sync time between RU and DU": 22,
    "Radio data path sync time": 32,
    "Tx Carrier setup time in radio": 5,
    "Tx Carrier activate time in radio": 2,
    "Rx Carrier setup time in radio": 6,
    "Rx Carrier activate time in radio": 3,
    "Tx Carrier deactivate time in radio": 4,
    "Rx Carrier deactivate time in radio": 5,
}


def test_sample_timings():
    results = measure_timings(messages_from_text(build_sample_soap_log()), load_parser_config())
    got = {item.label: item.seconds for item in results}
    assert got == EXPECTED
    assert all(item.column for item in results)


def test_robot_keyword_shape(tmp_path):
    soap = tmp_path / "soap_log.xml"
    soap.write_text(build_sample_soap_log(), encoding="utf-8")
    rows = get_times_from_log(str(soap))
    assert isinstance(rows, list)
    assert rows[0] == {"PTP sync time between RU and DU": 22}


def test_missing_end_is_none():
    config = {
        "only start": {
            "column": "ptp_sync",
            "start": {"xml_tag_name": "moduleReadyAck", "msg_from": "BTS", "msg_to": "RU"},
            "end": {"xml_tag_name": "managedObject", "xml_tag_attrib": {"class": "MissingClass"}},
        }
    }
    results = measure_timings(messages_from_text(build_sample_soap_log()), config)
    assert results[0].seconds is None
