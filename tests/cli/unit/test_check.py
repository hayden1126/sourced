import re
from sourced.commands.check import _check_python3


def test_check_python3_status_is_pass():
    result = _check_python3()
    assert result.status == "pass"


def test_check_python3_detail_matches_version_info():
    result = _check_python3()
    assert re.fullmatch(r"\d+\.\d+", result.detail or "")
