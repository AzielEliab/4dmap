#!/usr/bin/env python3
"""Write a minimal PDF companion from docs/4DM-WP-1.0.md.

The markdown file remains canonical. This companion is a typeset note,
not a new authority. Author: Aziel Eliab. No invented DOI.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "4DM-WP-1.0.md"
OUT = ROOT / "docs" / "4DM-WP-1.0.pdf"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(text: str) -> bytes:
    lines = []
    for raw in text.splitlines():
        line = raw[:90]
        lines.append(line)
        if len(lines) >= 48:
            break
    y = 760
    cmds = ["BT", "/F1 10 Tf"]
    for line in lines:
        cmds.append(f"1 0 0 1 48 {y} Tm ({_escape(line)}) Tj")
        y -= 14
    cmds.append("ET")
    stream = "\n".join(cmds).encode("latin-1", "replace")
    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
    )
    objects.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode())
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(out)


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    OUT.write_bytes(build_pdf(text))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
