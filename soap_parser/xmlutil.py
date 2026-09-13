"""Helpers for SOAP/OAM XML trees."""

from __future__ import annotations

from typing import Iterator, Optional
from xml.etree.ElementTree import Element


def local_name(tag: Optional[str]) -> str:
    if not tag:
        return ""
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def find_child(node: Element, name: str) -> Optional[Element]:
    for child in list(node):
        if local_name(child.tag) == name:
            return child
    return None


def iter_local(node: Element, name: str) -> Iterator[Element]:
    for el in node.iter():
        if local_name(el.tag) == name:
            yield el
