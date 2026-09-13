from soap_parser.match import find_body_attrib, find_in_body, find_in_header, walk_tag
from soap_parser.sample_log import FROM_BTS, TO_RU, _mo, _param
from soap_parser.xml_messages import normalize_xml, parse_message
from soap_parser.sample_log import soap_line


def test_normalize_and_parse_header():
    line = soap_line(
            "2021-06-17T03:16:48Z",
        FROM_BTS,
        TO_RU,
        "<moduleReadyAck><moduleType>RRH</moduleType></moduleReadyAck>",
    )
    xml_time, header, body = parse_message(normalize_xml(line))
    assert xml_time == "2021-06-17 03:16:48"
    assert find_in_header(header, msg_from="BTS", msg_to="RU")
    assert not find_in_header(header, msg_from="RU", msg_to="BTS")


def test_walk_tag_matches_local_name():
    line = soap_line(
            "2021-06-17T03:16:48Z",
        FROM_BTS,
        TO_RU,
        "<moduleReadyAck><moduleType>RRH</moduleType></moduleReadyAck>",
    )
    _, _, body = parse_message(normalize_xml(line))
    assert walk_tag(body, "moduleReadyAck")
    assert not walk_tag(body, "managedObject")


def test_first_non_matching_managed_object_does_not_hide_later_match():
    body_xml = (
        "<wrapper>"
        + _mo("RxArrayCarrier", "NR-1", "update_parm", _param("active", "TRUE"))
        + _mo("TxArrayCarrier", "NR-1", "update_parm", _param("active", "TRUE"))
        + "</wrapper>"
    )
    line = soap_line("2021-06-17T03:18:10Z/", FROM_BTS, TO_RU, body_xml)
    _, _, body = parse_message(normalize_xml(line))
    assert find_in_body(
        body,
        "managedObject",
        xml_tag_attrib={"class": "TxArrayCarrier", "distName": "NR"},
        managed_parameter_change={"parameterName": "active", "newValue": "TRUE"},
        should_contain_list=["update_parm"],
    )


def test_find_body_attrib_substring():
    line = soap_line(
            "2021-06-17T03:18:00Z",
        FROM_BTS,
        TO_RU,
        "<modifyParameterReq>%s</modifyParameterReq>"
        % _mo("TxArrayCarrier", "NR-1", "create_mo", _param("active", "FALSE")),
    )
    _, _, body = parse_message(normalize_xml(line))
    from soap_parser.xmlutil import iter_local

    mo = next(iter_local(body, "managedObject"))
    assert find_body_attrib(mo, {"class": "TxArrayCarrier", "distName": "NR"})
    assert not find_body_attrib(mo, {"class": "RxArrayCarrier"})


def test_original_unquoted_timestamp():
    line = (
        "<timestamp value=2021-06-17T03:16:48Z/>"
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">'
        "<SOAP-ENV:Header><from>BTS_OM_SAMPLE</from><to>/RMOD_L_1/RU_L_1</to></SOAP-ENV:Header>"
        "<SOAP-ENV:Body><moduleReadyAck/></SOAP-ENV:Body></SOAP-ENV:Envelope>"
    )
    xml_time, header, _ = parse_message(normalize_xml(line))
    assert xml_time == "2021-06-17 03:16:48"
    assert find_in_header(header, msg_from="BTS", msg_to="RU")
