#!/usr/bin/env python3
"""
Simple markdown-to-PDF renderer optimized for Japanese text and the
Module01_02_draft.md structure.
"""

import re
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
VENDOR_DIR = BASE_DIR / "vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.units import mm  # type: ignore
from reportlab.pdfbase import pdfmetrics  # type: ignore
from reportlab.pdfbase.cidfonts import UnicodeCIDFont  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore


TITLE_PATTERN = re.compile(r"^# (.+)")
H2_PATTERN = re.compile(r"^## (.+)")
H3_PATTERN = re.compile(r"^### (.+)")
LIST_PATTERN = re.compile(r"^(-|\d+\.) (.+)")


class PDFRenderer:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
        self.canvas = canvas.Canvas(str(output_path), pagesize=A4)
        self.width, self.height = A4
        self.margin_x = 20 * mm
        self.margin_y = 20 * mm
        self.cursor_y = self.height - self.margin_y

    def _new_page(self):
        self.canvas.showPage()
        self.canvas.setFont("HeiseiMin-W3", 11)
        self.cursor_y = self.height - self.margin_y

    def _ensure_space(self, required_height: float):
        if self.cursor_y - required_height < self.margin_y:
            self._new_page()

    def _draw_wrapped_text(
        self, text: str, font_size: int = 11, leading: int = 16, indent: float = 0.0
    ):
        self.canvas.setFont("HeiseiMin-W3", font_size)
        usable_width = self.width - 2 * self.margin_x - indent
        buffer = ""
        for char in text:
            candidate = buffer + char
            if pdfmetrics.stringWidth(candidate, "HeiseiMin-W3", font_size) <= usable_width:
                buffer = candidate
                continue
            if buffer:
                self._ensure_space(leading)
                self.canvas.drawString(self.margin_x + indent, self.cursor_y, buffer)
                self.cursor_y -= leading
            buffer = char if char != " " else ""
        if buffer:
            self._ensure_space(leading)
            self.canvas.drawString(self.margin_x + indent, self.cursor_y, buffer)
            self.cursor_y -= leading

    def render(self, lines: list[str]):
        self.canvas.setFont("HeiseiMin-W3", 11)
        for raw_line in lines:
            line = raw_line.rstrip("\n")
            if not line.strip():
                self.cursor_y -= 8
                continue

            if match := TITLE_PATTERN.match(line):
                text = match.group(1)
                self._ensure_space(40)
                self.canvas.setFont("HeiseiMin-W3", 22)
                self.canvas.drawString(self.margin_x, self.cursor_y, text)
                self.cursor_y -= 28
                continue

            if match := H2_PATTERN.match(line):
                text = match.group(1)
                self._ensure_space(32)
                self.canvas.setFont("HeiseiMin-W3", 16)
                self.canvas.drawString(self.margin_x, self.cursor_y, text)
                self.cursor_y -= 22
                self.cursor_y -= 4
                continue

            if match := H3_PATTERN.match(line):
                text = match.group(1)
                self._ensure_space(24)
                self.canvas.setFont("HeiseiMin-W3", 13)
                self.canvas.drawString(self.margin_x, self.cursor_y, text)
                self.cursor_y -= 18
                continue

            if match := LIST_PATTERN.match(line):
                bullet = match.group(1)
                text = match.group(2)
                bullet_text = "•" if bullet == "-" else f"{bullet}"
                self.canvas.setFont("HeiseiMin-W3", 11)
                self._ensure_space(16)
                self.canvas.drawString(self.margin_x, self.cursor_y, bullet_text)
                self._draw_wrapped_text(text, indent=14, font_size=11, leading=16)
                self.cursor_y -= 4
                continue

            if line.startswith("---"):
                self._ensure_space(20)
                self.canvas.setLineWidth(0.5)
                self.canvas.line(self.margin_x, self.cursor_y, self.width - self.margin_x, self.cursor_y)
                self.cursor_y -= 14
                continue

            self._draw_wrapped_text(line, font_size=11, leading=16)

        self.canvas.save()


def main():
    base_path = BASE_DIR
    source = base_path / "Module01_02_draft.md"
    if not source.exists():
        raise FileNotFoundError(f"{source} not found.")

    output = base_path / "Module01_02_preview.pdf"

    with source.open(encoding="utf-8") as f:
        lines = f.readlines()

    renderer = PDFRenderer(output)
    renderer.render(lines)
    print(f"PDF generated at: {output}")


if __name__ == "__main__":
    main()

