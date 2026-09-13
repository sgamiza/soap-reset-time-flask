"""Synthetic SOAP OAM lines for tests and the public sample log."""

from __future__ import annotations

FROM_BTS = "BTS_OM_SAMPLE"
TO_RU = "/RMOD_L_1/RU_L_1"
FROM_RU = "/RMOD_L_1/RU_L_1"
TO_BTS = "BTS_OM_SAMPLE"


def soap_line(timestamp: str, from_: str, to_: str, body: str) -> str:
    # Real logs look like: <timestamp value=2021-06-17T03:16:48Z/><SOAP-ENV:Envelope...
    stamp = timestamp.rstrip("/")
    if not stamp.endswith("Z"):
        stamp += "Z"
    return (
        "<timestamp value=%s/>"
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">'
        "<SOAP-ENV:Header><from>%s</from><to>%s</to></SOAP-ENV:Header>"
        "<SOAP-ENV:Body>%s</SOAP-ENV:Body>"
        "</SOAP-ENV:Envelope>"
        % (stamp, from_, to_, body)
    )


def _mo(class_name: str, dist_name: str, operation: str, parameters: str) -> str:
    return (
        '<managedObject class="%s" distName="%s">'
        "<operation>%s</operation>%s"
        "</managedObject>" % (class_name, dist_name, operation, parameters)
    )


def _param(name: str, new_value: str, prev_value: str = "") -> str:
    return (
        "<parameter><parameterName>%s</parameterName>"
        "<newValue>%s</newValue><prevValue>%s</prevValue></parameter>"
        % (name, new_value, prev_value)
    )


def build_sample_soap_log() -> str:
    """Cover every default timing rule with stable, non-lab identifiers."""
    lines = [
        soap_line(
            "2021-06-17T03:16:48Z",
            FROM_BTS,
            TO_RU,
            "<moduleReadyAck><moduleType>RRH</moduleType></moduleReadyAck>",
        ),
        soap_line(
            "2021-06-17T03:17:10Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo("PtpStatus", "ptpStatus", "update_parm", _param("lockState", "LOCKED")),
        ),
        soap_line(
            "2021-06-17T03:17:20Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo(
                "Synchronization",
                "synchronization",
                "update_parm",
                _param("state", "LOCKED", "FREERUN"),
            ),
        ),
        soap_line(
            "2021-06-17T03:18:00Z",
            FROM_BTS,
            TO_RU,
            "<modifyParameterReq>%s</modifyParameterReq>"
            % _mo("TxArrayCarrier", "NR-1", "create_mo", _param("active", "FALSE")),
        ),
        soap_line(
            "2021-06-17T03:18:05Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo(
                "TxArrayCarrier",
                "NR-1",
                "create_mo",
                _param("active", "FALSE") + _param("subscribe", "TRUE"),
            ),
        ),
        soap_line(
            "2021-06-17T03:18:10Z",
            FROM_BTS,
            TO_RU,
            "<modifyParameterReq>%s</modifyParameterReq>"
            % _mo("TxArrayCarrier", "NR-1", "update_parm", _param("active", "TRUE")),
        ),
        soap_line(
            "2021-06-17T03:18:12Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo(
                "TxArrayCarrier",
                "NR-1",
                "update_parm",
                _param("active", "TRUE", "FALSE"),
            ),
        ),
        soap_line(
            "2021-06-17T03:18:20Z",
            FROM_BTS,
            TO_RU,
            "<modifyParameterReq>%s</modifyParameterReq>"
            % _mo("RxArrayCarrier", "NR-1", "create_mo", _param("active", "FALSE")),
        ),
        soap_line(
            "2021-06-17T03:18:26Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo(
                "RxArrayCarrier",
                "NR-1",
                "create_mo",
                _param("active", "FALSE") + _param("subscribe", "TRUE"),
            ),
        ),
        soap_line(
            "2021-06-17T03:18:30Z",
            FROM_BTS,
            TO_RU,
            "<modifyParameterReq>%s</modifyParameterReq>"
            % _mo("RxArrayCarrier", "NR-1", "update_parm", _param("active", "TRUE")),
        ),
        soap_line(
            "2021-06-17T03:18:33Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo(
                "RxArrayCarrier",
                "NR-1",
                "update_parm",
                _param("active", "TRUE", "FALSE"),
            ),
        ),
        soap_line(
            "2021-06-17T03:19:00Z",
            FROM_BTS,
            TO_RU,
            "<modifyParameterReq>%s</modifyParameterReq>"
            % _mo("TxArrayCarrier", "NR-1", "update_parm", _param("active", "FALSE")),
        ),
        soap_line(
            "2021-06-17T03:19:04Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo(
                "TxArrayCarrier",
                "NR-1",
                "update_parm",
                _param("state", "DISABLED", "READY") + _param("active", "FALSE", "TRUE"),
            ),
        ),
        soap_line(
            "2021-06-17T03:19:10Z",
            FROM_BTS,
            TO_RU,
            "<modifyParameterReq>%s</modifyParameterReq>"
            % _mo("RxArrayCarrier", "NR-1", "update_parm", _param("active", "FALSE")),
        ),
        soap_line(
            "2021-06-17T03:19:15Z",
            FROM_RU,
            TO_BTS,
            "<parValueChangeInd>%s<status>OK</status></parValueChangeInd>"
            % _mo(
                "RxArrayCarrier",
                "NR-1",
                "update_parm",
                _param("state", "DISABLED", "READY") + _param("active", "FALSE", "TRUE"),
            ),
        ),
    ]
    return "\n".join(lines) + "\n"
