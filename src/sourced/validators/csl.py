"""CSL XML title validation. PRE-render: checks a static fact about the template.

A style.md file declares its CSL provenance (`CSL title: <name>`), and the
matching CSL XML file at templates/styles/<name>/<file>.csl has a <title>
element. This validator confirms they agree — silent edition drift (e.g.,
upstream CSL repository updates Chicago 17 → 18) gets caught here.
"""
from __future__ import annotations
from pathlib import Path
from xml.etree import ElementTree as ET

from . import Finding


# CSL is XML with a default namespace: http://purl.org/net/xbiblio/csl
_CSL_NS = {"csl": "http://purl.org/net/xbiblio/csl"}


def validate_csl_title(
    csl_path: Path,
    declared_title: str,
    style_name: str,
) -> list[Finding]:
    """Compare CSL XML <info><title> against style.md's declared title."""
    if not csl_path.exists():
        return [Finding(
            rule="csl-file-missing",
            location=str(csl_path),
            severity="error",
            message=f"CSL file declared by style '{style_name}' does not exist on disk.",
            fix_hint=f"vendor the CSL file at {csl_path}, or update style.md provenance.",
        )]

    try:
        tree = ET.parse(csl_path)
    except ET.ParseError as e:
        return [Finding(
            rule="csl-parse-error",
            location=str(csl_path),
            severity="error",
            message=f"CSL file is not valid XML: {e}",
        )]

    root = tree.getroot()
    title_elem = root.find("csl:info/csl:title", _CSL_NS)
    if title_elem is None or title_elem.text is None:
        return [Finding(
            rule="csl-title-missing",
            location=str(csl_path),
            severity="error",
            message="CSL file has no <info><title> element.",
            fix_hint="check the CSL file is the right edition; the upstream repository "
                     "may have moved this style to a different filename.",
        )]

    actual = title_elem.text.strip()
    if actual != declared_title:
        return [Finding(
            rule="csl-title-mismatch",
            location=str(csl_path),
            severity="error",
            message=(
                f"style '{style_name}' declares CSL title "
                f"{declared_title!r} but the CSL file's <title> is {actual!r} — "
                "silent edition drift. The vendored CSL file may have been "
                "replaced by a different edition's upstream version."
            ),
            fix_hint=f"either update style.md's `CSL title:` to {actual!r}, "
                     f"or replace {csl_path} with the correct edition.",
        )]

    return []
