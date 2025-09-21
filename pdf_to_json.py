import fitz           # PyMuPDF
import pdfplumber     # For tables
import re
import json
import os


# Helper regex patterns

NUM_HEADING = re.compile(r"^\d+(\.\d+)*\s")        # 1. or 1.1 style headings
FIGURE_RE = re.compile(r"^\s*(Figure|Fig\.)\s*\d+", re.I)


# Detect headings from font size or numbering

def detect_headings(lines):
    """
    Given spans with font size, detect headings.
    Returns [(y, level, text), ...]
    """
    if not lines:
        return []
    sizes = sorted({round(l["avg_size"], 2) for l in lines}, reverse=True)
    size2rank = {s: i+1 for i, s in enumerate(sizes)}
    heads = []
    for ln in lines:
        txt = ln["text"]
        lvl = None
        if NUM_HEADING.match(txt):
            lvl = 1 + txt.split()[0].count(".")
            lvl = min(lvl, 2)
        else:
            r = size2rank.get(round(ln["avg_size"],2), 99)
            if r == 1: lvl = 1
            elif r == 2: lvl = 2
        if lvl in (1,2):
            heads.append((ln["bbox"][1], lvl, txt))
    heads.sort(key=lambda x: x[0])
    return heads


# Extract spans from PyMuPDF

def get_lines(page):
    out = []
    d = page.get_text("dict")
    for b in d.get("blocks", []):
        if b.get("type", 0) != 0:
            continue
        for l in b.get("lines", []):
            spans = l.get("spans", [])
            if not spans:
                continue
            txt = "".join(s.get("text","") for s in spans).strip()
            if not txt:
                continue
            avg_size = sum(s.get("size", 0) for s in spans)/len(spans)
            bbox = tuple(l.get("bbox", (0,0,0,0)))
            out.append({"text": txt, "bbox": bbox, "avg_size": avg_size})
    return out

def build_section_map(lines):
    anchors = []
    heads = detect_headings(lines)
    current_sec, current_sub = None, None
    for (y, lvl, title) in heads:
        if lvl == 1:
            current_sec, current_sub = title, None
        elif lvl == 2:
            current_sub = title
        anchors.append((y, current_sec, current_sub))
    if not anchors:
        anchors = [(0, None, None)]
    return anchors

def nearest_section(anchors, y):
    last = (None, None)
    for (ay, sec, sub) in anchors:
        if y >= ay:
            last = (sec, sub)
        else:
            break
    return last


# Table extract with pdfplumber

def extract_tables(pdfplumb_page, section, sub_section):
    blocks = []
    tables = pdfplumb_page.extract_tables()
    for tb in tables:
        blocks.append({
            "type": "table",
            "section": section,
            "sub_section": sub_section,
            "description": None,
            "table_data": tb
        })
    return blocks


# Main function

def pdf_to_json(pdf_path, out_json="output.json"):
    doc = fitz.open(pdf_path)
    plumber_doc = pdfplumber.open(pdf_path)
    result = {"meta": {"source_pdf": os.path.basename(pdf_path)}, "pages": []}

    for pidx in range(len(doc)):
        page = doc[pidx]
        plumb_page = plumber_doc.pages[pidx]
        lines = get_lines(page)
        anchors = build_section_map(lines)

        page_obj = {"page_number": pidx+1, "content": []}

        
        for ln in lines:
            txt = ln["text"]
            y = ln["bbox"][1]
            section, subsec = nearest_section(anchors, y)

            # Chart detection (by caption)
            if FIGURE_RE.match(txt):
                page_obj["content"].append({
                    "type": "chart",
                    "section": section,
                    "sub_section": subsec,
                    "description": txt,
                    "table_data": None,
                    "image_name": None
                })
            else:
                page_obj["content"].append({
                    "type": "paragraph",
                    "section": section,
                    "sub_section": subsec,
                    "text": txt
                })

        # Tables
        tables = extract_tables(plumb_page, section=None, sub_section=None)
        page_obj["content"].extend(tables)

        # Links
        links = page.get_links()
        if links:
            for l in links:
                page_obj["content"].append({
                    "type": "link",
                    "section": None,
                    "sub_section": None,
                    "uri": l.get("uri"),
                    "from": l.get("from")
                })

        result["pages"].append(page_obj)

    plumber_doc.close()
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


# Run 

if __name__ == "__main__":
    pdf_path = "/content/[Fund Factsheet - May]360ONE-MF-May 2025.pdf.pdf"
    data = pdf_to_json(pdf_path, "factsheet_output.json")
    print("JSON written to factsheet_output.json")
