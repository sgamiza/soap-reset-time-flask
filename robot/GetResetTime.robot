*** Settings ***
Library    ../soap_log_parser.py

*** Test Cases ***
Measure Sample SOAP Log
    ${soap_parser_result}=    Get Times From Log    ${CURDIR}${/}..${/}samples${/}soap_log.xml
    Log    ${soap_parser_result}
