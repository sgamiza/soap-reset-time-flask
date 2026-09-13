from soap_parser.sample_log import build_sample_soap_log

if __name__ == "__main__":
    from pathlib import Path

    dest = Path(__file__).with_name("soap_log.xml")
    dest.write_text(build_sample_soap_log(), encoding="utf-8")
    print("wrote", dest)
