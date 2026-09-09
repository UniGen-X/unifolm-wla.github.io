#!/usr/bin/env python3
"""Export the benchmark table in index.html as a scalable SVG and a 2x PNG."""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "index.html"
OUTPUT_DIR = ROOT / "assets" / "benchmark"
SVG_PATH = OUTPUT_DIR / "embodied-reasoning-benchmark-zh.svg"
PNG_PATH = OUTPUT_DIR / "embodied-reasoning-benchmark-zh-2x.png"

METRICS = [
    "RoboVQA", "Ego-Plan2", "RefSpatial-Bench", "Where2Place",
    "Pixmo-Point", "BLINK", "CV-Bench", "EmbSpatial",
    "RoboSpatial", "SAT", "VSI-Bench", "VSR",
    "ERQA", "RealWorldQA", "MME", "MMMU_VAL",
]


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_tbody = False
        self.row = None
        self.cell = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        if tag == "tbody":
            self.in_tbody = True
        elif self.in_tbody and tag == "tr":
            self.row = {"classes": classes, "cells": []}
        elif self.in_tbody and tag == "td":
            self.cell = {
                "classes": classes,
                "zh": attrs.get("data-i18n-zh"),
                "text": [],
            }

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            text = re.sub(r"\s+", " ", "".join(self.cell["text"])).strip()
            self.cell["text"] = self.cell["zh"] or text
            self.row["cells"].append(self.cell)
            self.cell = None
        elif tag == "tr" and self.in_tbody and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif tag == "tbody":
            self.in_tbody = False

    def handle_data(self, data):
        if self.cell is not None:
            self.cell["text"].append(data)


def parse_table():
    source = SOURCE.read_text(encoding="utf-8")
    match = re.search(
        r'<div class="benchmark"[^>]*>(.*?)<section class="drp-root"',
        source,
        re.S,
    )
    if not match:
        raise RuntimeError("Benchmark table not found in index.html")
    block = match.group(1)
    parser = TableParser()
    parser.feed(block)
    rows = parser.rows
    if len(rows) != 24:
        raise RuntimeError(f"Expected 24 benchmark rows, found {len(rows)}")
    for row in rows:
        if len(row["cells"]) != 18:
            model = row["cells"][0]["text"] if row["cells"] else "unknown"
            raise RuntimeError(f"{model}: expected 18 cells, found {len(row['cells'])}")

    notes_match = re.search(r'<div class="benchmark-notes">(.*?)</div>', block, re.S)
    notes = []
    if notes_match:
        notes = [
            html.unescape(value)
            for value in re.findall(r'data-i18n-zh="([^"]+)"', notes_match.group(1))
        ]
    return rows, notes


def svg_text(x, y, value, *, size=16, weight=400, anchor="middle", fill="#27312d"):
    safe = html.escape(value)
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{safe}</text>'
    )


def export_svg(rows, notes):
    margin = 48
    model_w = 310
    open_w = 90
    metric_w = 170
    title_h = 104
    group_h = 46
    header_h = 68
    row_h = 52
    notes_h = 34 + len(notes) * 28
    table_w = model_w + open_w + len(METRICS) * metric_w
    width = table_w + margin * 2
    height = title_h + group_h + header_h + len(rows) * row_h + notes_h + margin
    table_y = title_h
    data_y = table_y + group_h + header_h

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<linearGradient id="sota" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#F96765"/>',
        '<stop offset="52%" stop-color="#F28B55"/>',
        '<stop offset="100%" stop-color="#E8B84F"/>',
        "</linearGradient>",
        '<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">',
        '<feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#17221d" flood-opacity=".10"/>',
        "</filter>",
        "</defs>",
        '<rect width="100%" height="100%" fill="#F4F5F0"/>',
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Noto Sans CJK SC,Arial,sans-serif">',
        svg_text(margin, 58, "具身推理评测结果", size=32, weight=700, anchor="start", fill="#101613"),
        svg_text(width - margin, 56, "24 MODELS · 16 BENCHMARKS", size=14, weight=650, anchor="end", fill="#68746F"),
        f'<g filter="url(#shadow)">',
        f'<rect x="{margin}" y="{table_y}" width="{table_w}" height="{group_h + header_h + len(rows) * row_h}" rx="16" fill="#FFFFFF"/>',
    ]

    x_model = margin
    x_open = x_model + model_w
    x_metrics = x_open + open_w
    full_header_h = group_h + header_h
    header_fill = "#EEF1ED"
    line = "#CBD2CE"

    out += [
        f'<rect x="{x_model}" y="{table_y}" width="{model_w}" height="{full_header_h}" fill="{header_fill}"/>',
        f'<rect x="{x_open}" y="{table_y}" width="{open_w}" height="{full_header_h}" fill="{header_fill}"/>',
        f'<rect x="{x_metrics}" y="{table_y}" width="{metric_w * 13}" height="{group_h}" fill="{header_fill}"/>',
        f'<rect x="{x_metrics + metric_w * 13}" y="{table_y}" width="{metric_w * 3}" height="{group_h}" fill="{header_fill}"/>',
        svg_text(x_model + 16, table_y + full_header_h / 2 + 6, "模型", size=18, weight=700, anchor="start", fill="#101613"),
        svg_text(x_open + open_w / 2, table_y + full_header_h / 2 + 6, "开源", size=18, weight=700, fill="#101613"),
        svg_text(x_metrics + metric_w * 6.5, table_y + 30, "空间理解", size=18, weight=700, fill="#101613"),
        svg_text(x_metrics + metric_w * 14.5, table_y + 30, "多模态理解", size=18, weight=700, fill="#101613"),
    ]

    metric_y = table_y + group_h
    for index, metric in enumerate(METRICS):
        x = x_metrics + index * metric_w
        out.append(f'<rect x="{x}" y="{metric_y}" width="{metric_w}" height="{header_h}" fill="{header_fill}"/>')
        out.append(svg_text(x + metric_w / 2, metric_y + 41, metric.upper(), size=13, weight=700, fill="#35423D"))

    for row_index, row in enumerate(rows):
        y = data_y + row_index * row_h
        is_featured = "featured-row" in row["classes"]
        base_fill = "#FBFCFA" if row_index % 2 else "#FFFFFF"
        for cell_index, cell in enumerate(row["cells"]):
            if cell_index == 0:
                x, cell_w = x_model, model_w
            elif cell_index == 1:
                x, cell_w = x_open, open_w
            else:
                x, cell_w = x_metrics + (cell_index - 2) * metric_w, metric_w
            is_sota = "score-best" in cell["classes"]
            fill = "url(#sota)" if is_sota else ("#FBA5A4" if is_featured else base_fill)
            stroke = "#D7A940" if is_sota else line
            stroke_w = 1.5 if is_sota else 1
            out.append(
                f'<rect x="{x}" y="{y}" width="{cell_w}" height="{row_h}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"/>'
            )
            text_fill = "#17100F" if (is_sota or is_featured or "score-new" in cell["classes"]) else "#35423D"
            weight = 800 if (cell_index == 0 or is_sota or "score-new" in cell["classes"]) else 450
            anchor = "start" if cell_index == 0 else "middle"
            text_x = x + 14 if cell_index == 0 else x + cell_w / 2
            out.append(svg_text(text_x, y + 33, cell["text"], size=16, weight=weight, anchor=anchor, fill=text_fill))
        if "group-start" in row["classes"]:
            out.append(f'<line x1="{margin}" y1="{y}" x2="{margin + table_w}" y2="{y}" stroke="#87938E" stroke-width="2"/>')

    out += [
        f'<rect x="{margin}" y="{table_y}" width="{table_w}" height="{group_h + header_h + len(rows) * row_h}" rx="16" fill="none" stroke="{line}" stroke-width="1.5"/>',
        "</g>",
    ]

    notes_y = data_y + len(rows) * row_h + 34
    for index, note in enumerate(notes):
        out.append(svg_text(margin, notes_y + index * 28, note, size=14, weight=450, anchor="start", fill="#68746F"))
    out += ["</g>", "</svg>"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text("\n".join(out), encoding="utf-8")
    return width, height


def export_png(rows, notes, width, height):
    scale = 2
    margin = 48
    model_w = 310
    open_w = 90
    metric_w = 170
    title_h = 104
    group_h = 46
    header_h = 68
    row_h = 52
    table_w = model_w + open_w + len(METRICS) * metric_w
    table_y = title_h
    data_y = table_y + group_h + header_h

    def sc(value):
        return int(round(value * scale))

    regular_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    bold_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    fonts = {}

    def font(size, bold=False):
        key = (size, bold)
        if key not in fonts:
            fonts[key] = ImageFont.truetype(bold_path if bold else regular_path, sc(size))
        return fonts[key]

    image = Image.new("RGB", (sc(width), sc(height)), "#F4F5F0")
    draw = ImageDraw.Draw(image)

    def rectangle(box, fill, outline=None, line_width=1, radius=0):
        scaled = tuple(sc(value) for value in box)
        if radius:
            draw.rounded_rectangle(
                scaled,
                radius=sc(radius),
                fill=fill,
                outline=outline,
                width=sc(line_width),
            )
        else:
            draw.rectangle(scaled, fill=fill, outline=outline, width=sc(line_width))

    def label(x, y, value, *, size=16, bold=False, fill="#27312D", anchor="mm"):
        draw.text(
            (sc(x), sc(y)),
            value,
            font=font(size, bold),
            fill=fill,
            anchor=anchor,
        )

    def gradient_cell(box):
        x0, y0, x1, y1 = (sc(value) for value in box)
        cell_w = max(1, x1 - x0)
        cell_h = max(1, y1 - y0)
        colors = ((249, 103, 101), (242, 139, 85), (232, 184, 79))
        gradient = Image.new("RGB", (cell_w, cell_h))
        pixels = gradient.load()
        for x in range(cell_w):
            t = x / max(1, cell_w - 1)
            if t <= 0.52:
                local = t / 0.52
                start, end = colors[0], colors[1]
            else:
                local = (t - 0.52) / 0.48
                start, end = colors[1], colors[2]
            color = tuple(round(a + (b - a) * local) for a, b in zip(start, end))
            for y in range(cell_h):
                pixels[x, y] = color
        image.paste(gradient, (x0, y0))
        draw.rectangle((x0, y0, x1, y1), outline="#D7A940", width=sc(1.5))

    label(margin, 58, "具身推理评测结果", size=32, bold=True, fill="#101613", anchor="lm")
    label(width - margin, 56, "24 MODELS · 16 BENCHMARKS", size=14, bold=True, fill="#68746F", anchor="rm")

    x_model = margin
    x_open = x_model + model_w
    x_metrics = x_open + open_w
    full_header_h = group_h + header_h
    header_fill = "#EEF1ED"
    line = "#CBD2CE"
    rectangle(
        (margin, table_y, margin + table_w, table_y + full_header_h + len(rows) * row_h),
        "#FFFFFF",
        outline=line,
        line_width=1,
        radius=16,
    )
    rectangle((x_model, table_y, x_model + model_w, table_y + full_header_h), header_fill)
    rectangle((x_open, table_y, x_open + open_w, table_y + full_header_h), header_fill)
    rectangle((x_metrics, table_y, x_metrics + metric_w * 13, table_y + group_h), header_fill)
    rectangle((x_metrics + metric_w * 13, table_y, x_metrics + metric_w * 16, table_y + group_h), header_fill)
    label(x_model + 16, table_y + full_header_h / 2, "模型", size=18, bold=True, fill="#101613", anchor="lm")
    label(x_open + open_w / 2, table_y + full_header_h / 2, "开源", size=18, bold=True, fill="#101613")
    label(x_metrics + metric_w * 6.5, table_y + group_h / 2, "空间理解", size=18, bold=True, fill="#101613")
    label(x_metrics + metric_w * 14.5, table_y + group_h / 2, "多模态理解", size=18, bold=True, fill="#101613")

    metric_y = table_y + group_h
    for index, metric in enumerate(METRICS):
        x = x_metrics + index * metric_w
        rectangle((x, metric_y, x + metric_w, metric_y + header_h), header_fill, outline=line)
        label(x + metric_w / 2, metric_y + header_h / 2, metric.upper(), size=13, bold=True, fill="#35423D")

    for row_index, row in enumerate(rows):
        y = data_y + row_index * row_h
        is_featured = "featured-row" in row["classes"]
        base_fill = "#FBFCFA" if row_index % 2 else "#FFFFFF"
        for cell_index, cell in enumerate(row["cells"]):
            if cell_index == 0:
                x, cell_w = x_model, model_w
            elif cell_index == 1:
                x, cell_w = x_open, open_w
            else:
                x, cell_w = x_metrics + (cell_index - 2) * metric_w, metric_w
            is_sota = "score-best" in cell["classes"]
            box = (x, y, x + cell_w, y + row_h)
            if is_sota:
                gradient_cell(box)
            else:
                fill = "#FBA5A4" if is_featured else base_fill
                rectangle(box, fill, outline=line)
            text_fill = "#17100F" if (is_sota or is_featured or "score-new" in cell["classes"]) else "#35423D"
            is_bold = cell_index == 0 or is_sota or "score-new" in cell["classes"]
            if cell_index == 0:
                label(x + 14, y + row_h / 2, cell["text"], size=16, bold=is_bold, fill=text_fill, anchor="lm")
            else:
                label(x + cell_w / 2, y + row_h / 2, cell["text"], size=16, bold=is_bold, fill=text_fill)
        if "group-start" in row["classes"]:
            draw.line(
                (sc(margin), sc(y), sc(margin + table_w), sc(y)),
                fill="#87938E",
                width=sc(2),
            )

    notes_y = data_y + len(rows) * row_h + 34
    for index, note in enumerate(notes):
        label(margin, notes_y + index * 28, note, size=14, fill="#68746F", anchor="lm")

    image.save(PNG_PATH, format="PNG", optimize=True)


def main():
    rows, notes = parse_table()
    width, height = export_svg(rows, notes)
    export_png(rows, notes, width, height)
    print(f"SVG: {SVG_PATH}")
    print(f"PNG: {PNG_PATH}")
    print(f"Rows: {len(rows)}, metrics per row: {len(METRICS)}")


if __name__ == "__main__":
    main()
