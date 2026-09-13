"""Match SOAP header/body nodes against timing rules."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional
from xml.etree.ElementTree import Element

from soap_parser.xmlutil import find_child, iter_local, local_name


def find_in_header(xml_header: Element, msg_from: Optional[str] = None, msg_to: Optional[str] = None) -> bool:
    if not msg_from and not msg_to:
        return True
    msg_from = "" if msg_from is None else str(msg_from)
    msg_to = "" if msg_to is None else str(msg_to)
    from_node = find_child(xml_header, "from")
    to_node = find_child(xml_header, "to")
    from_text = (from_node.text or "") if from_node is not None else ""
    to_text = (to_node.text or "") if to_node is not None else ""
    if not from_text or not to_text:
        return False
    return msg_from in from_text and msg_to in to_text


def check_reply_status(body_node: Element, tag: str = "status", value: str = "OK") -> bool:
    for node in iter_local(body_node, tag):
        if node.text and node.text == value:
            return True
    return False


def walk_text(xml_node: Element, node_text: str) -> bool:
    for text in xml_node.itertext():
        if node_text == text:
            return True
    return False


def walk_tag(xml_node: Element, node_name: str) -> bool:
    for node in xml_node.iter():
        if local_name(node.tag) == node_name:
            return True
    return False


def get_check_list(xml_node: Element, contain_list: Iterable[str]) -> List[str]:
    found = []
    for contain in contain_list:
        if walk_text(xml_node, contain) or walk_tag(xml_node, contain):
            found.append(contain)
    return found


def find_body_contain(xml_node: Element, contain_list: Optional[List[str]]) -> bool:
    if not contain_list:
        return True
    return set(get_check_list(xml_node, contain_list)) == set(contain_list)


def find_body_not_contain(xml_node: Element, contain_list: Optional[List[str]]) -> bool:
    if not contain_list:
        return True
    return set(get_check_list(xml_node, contain_list)).isdisjoint(set(contain_list))


def find_body_parameter_change(
    managed_object_node: Element,
    parameterName: str,
    newValue: str,
    prevValue: Optional[str] = None,
) -> bool:
    if local_name(managed_object_node.tag) != "managedObject":
        raise ValueError("node must be managedObject")
    for parameter in list(managed_object_node):
        if local_name(parameter.tag) != "parameter":
            continue
        name_el = find_child(parameter, "parameterName")
        new_el = find_child(parameter, "newValue")
        prev_el = find_child(parameter, "prevValue")
        name_text = name_el.text if name_el is not None else None
        new_text = new_el.text if new_el is not None else None
        prev_text = prev_el.text if prev_el is not None else None
        if parameterName == name_text and newValue == new_text:
            if prevValue and prevValue != prev_text:
                continue
            return True
    return False


def find_body_attrib(xml_node: Element, expected: Optional[Dict[str, Any]] = None) -> bool:
    if not expected:
        return True
    attrib = xml_node.attrib
    for key, value in expected.items():
        if key not in attrib or value not in attrib[key]:
            return False
    return True


def find_in_body(
    xml_node: Element,
    xml_tag_name: str,
    xml_tag_attrib: Optional[Dict[str, Any]] = None,
    managed_parameter_change: Optional[Dict[str, Any]] = None,
    should_contain_list: Optional[List[str]] = None,
    should_not_contain_list: Optional[List[str]] = None,
    check_status: bool = False,
) -> bool:
    xml_tag_attrib = xml_tag_attrib or {}
    status_ok = check_reply_status(xml_node) if check_status else True
    for each_node in iter_local(xml_node, xml_tag_name):
        attrib_ok = find_body_attrib(each_node, xml_tag_attrib)
        contain_ok = find_body_contain(each_node, should_contain_list) and find_body_not_contain(
            each_node, should_not_contain_list
        )
        parameter_ok = True
        if managed_parameter_change and local_name(each_node.tag) == "managedObject":
            parameter_ok = find_body_parameter_change(each_node, **managed_parameter_change)
        elif managed_parameter_change:
            parameter_ok = False
        if attrib_ok and contain_ok and parameter_ok and status_ok:
            return True
    return False


def find_in_dom(
    xml_header: Element,
    xml_body: Element,
    xml_tag_name: str,
    msg_from: Optional[str] = None,
    msg_to: Optional[str] = None,
    xml_tag_attrib: Optional[Dict[str, Any]] = None,
    managed_parameter_change: Optional[Dict[str, Any]] = None,
    should_contain_list: Optional[List[str]] = None,
    should_not_contain_list: Optional[List[str]] = None,
    check_status: bool = False,
) -> bool:
    return find_in_header(xml_header, msg_from=msg_from, msg_to=msg_to) and find_in_body(
        xml_body,
        xml_tag_name=xml_tag_name,
        xml_tag_attrib=xml_tag_attrib,
        managed_parameter_change=managed_parameter_change,
        should_contain_list=should_contain_list,
        should_not_contain_list=should_not_contain_list,
        check_status=check_status,
    )
