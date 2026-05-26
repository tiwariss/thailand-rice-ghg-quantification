"""
Parse OAE Thailand rice PDFs → clean CSV
Handles split-number artifacts from PDF rendering.

Input:  resources/data/OAE (20XX) [Main|Dry] Season.pdf
Output: output/data/oae_provincial_rice_2022_2024.csv

Run from project root: python code/parse_rice_pdfs.py
"""

import pdfplumber
import pandas as pd
import re
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))

sys.stdout.reconfigure(encoding="utf-8")

# ── Province name → English (77 provinces) ───────────────────────────────────
PROVINCE_EN = {
    "เชียงราย": "Chiang Rai", "พะเยา": "Phayao", "ลําปาง": "Lampang",
    "ล าปาง": "Lampang", "ลำปาง": "Lampang",
    "ลําพูน": "Lamphun", "ล าพูน": "Lamphun", "ลำพูน": "Lamphun",
    "เชียงใหม่": "Chiang Mai", "แม่ฮ่องสอน": "Mae Hong Son",
    "ตาก": "Tak", "กําแพงเพชร": "Kamphaeng Phet",
    "ก าแพงเพชร": "Kamphaeng Phet", "กำแพงเพชร": "Kamphaeng Phet",
    "สุโขทัย": "Sukhothai", "แพร่": "Phrae", "น่าน": "Nan",
    "อุตรดิตถ์": "Uttaradit", "พิษณุโลก": "Phitsanulok",
    "พิจิตร": "Phichit", "เพชรบูรณ์": "Phetchabun",
    "หนองคาย": "Nong Khai", "หนองบัวลําภู": "Nong Bua Lamphu",
    "หนองบัวล าภู": "Nong Bua Lamphu", "หนองบัวลำภู": "Nong Bua Lamphu",
    "อุดรธานี": "Udon Thani", "เลย": "Loei", "สกลนคร": "Sakon Nakhon",
    "นครพนม": "Nakhon Phanom", "มุกดาหาร": "Mukdahan",
    "ยโสธร": "Yasothon", "อํานาจเจริญ": "Amnat Charoen",
    "อ านาจเจริญ": "Amnat Charoen", "อำนาจเจริญ": "Amnat Charoen",
    "อุบลราชธานี": "Ubon Ratchathani", "ศรีสะเกษ": "Si Sa Ket",
    "สุรินทร์": "Surin", "บุรีรัมย์": "Buri Ram",
    "มหาสารคาม": "Maha Sarakham", "ร้อยเอ็ด": "Roi Et",
    "กาฬสินธุ์": "Kalasin", "ขอนแก่น": "Khon Kaen",
    "ชัยภูมิ": "Chaiyaphum", "นครราชสีมา": "Nakhon Ratchasima",
    "สระบุรี": "Saraburi", "ลพบุรี": "Lopburi",
    "สิงห์บุรี": "Sing Buri", "ชัยนาท": "Chai Nat",
    "สุพรรณบุรี": "Suphan Buri", "อ่างทอง": "Ang Thong",
    "พระนครศรีอยุธยา": "Phra Nakhon Si Ayutthaya",
    "นครสวรรค์": "Nakhon Sawan", "อุทัยธานี": "Uthai Thani",
    "กําแพงเพชร": "Kamphaeng Phet", "พิษณุโลก": "Phitsanulok",
    "นนทบุรี": "Nonthaburi", "ปทุมธานี": "Pathum Thani",
    "กรุงเทพมหานคร": "Bangkok", "นครปฐม": "Nakhon Pathom",
    "สมุทรสาคร": "Samut Sakhon", "สมุทรสงคราม": "Samut Songkhram",
    "สมุทรปราการ": "Samut Prakan", "ราชบุรี": "Ratchaburi",
    "กาญจนบุรี": "Kanchanaburi", "เพชรบุรี": "Phetchaburi",
    "ประจวบคีรีขันธ์": "Prachuap Khiri Khan", "ฉะเชิงเทรา": "Chachoengsao",
    "ปราจีนบุรี": "Prachin Buri", "นครนายก": "Nakhon Nayok",
    "สระแก้ว": "Sa Kaeo", "ชลบุรี": "Chon Buri",
    "ระยอง": "Rayong", "จันทบุรี": "Chanthaburi",
    "ตราด": "Trat", "ชุมพร": "Chumphon",
    "ระนอง": "Ranong", "สุราษฎร์ธานี": "Surat Thani",
    "พังงา": "Phang Nga", "ภูเก็ต": "Phuket",
    "กระบี่": "Krabi", "ตรัง": "Trang",
    "นครศรีธรรมราช": "Nakhon Si Thammarat", "พัทลุง": "Phatthalung",
    "สงขลา": "Songkhla", "สตูล": "Satun",
    "ปัตตานี": "Pattani", "ยะลา": "Yala",
    "นราธิวาส": "Narathiwat", "บึงกาฬ": "Bueng Kan",
    "วังทอง": "Wang Thong",
    # ── Tone-mark-stripped variants (PDF encoding drops diacritics) ──
    "กาฬสินธุ": "Kalasin", "กาฬสนิ": "Kalasin", "กาฬสนิ ธุ": "Kalasin",
    "ขอนแกน": "Khon Kaen",
    "นครสวรรค": "Nakhon Sawan",
    "นาน": "Nan",
    "บุรีรัมย": "Buri Ram", "บุรรี ัมย": "Buri Ram",
    "ปตตานี": "Pattani",
    "ประจวบคีรีขันธ": "Prachuap Khiri Khan",
    "ประจวบครี ีขันธ": "Prachuap Khiri Khan",
    "ประจวบคีรขี ันธ": "Prachuap Khiri Khan",
    "รอยเอ็ด": "Roi Et",
    "สระแกว": "Sa Kaeo",
    "สิงหบุรี": "Sing Buri",
    "สุราษฎรธานี": "Surat Thani",
    "สุรินทร": "Surin", "สุรนิ ทร": "Surin",
    "หนองบัวลาํ ภู": "Nong Bua Lamphu", "หนองบัวล": "Nong Bua Lamphu",
    "อยุธยา": "Phra Nakhon Si Ayutthaya",
    "อางทอง": "Ang Thong",
    "อุตรดิตถ": "Uttaradit",
    "เชียงใหม": "Chiang Mai",
    "เพชรบูรณ": "Phetchabun",
    "แพร": "Phrae",
    "แมฮองสอน": "Mae Hong Son", "แมฮอ งสอน": "Mae Hong Son",
    "ศรีสะเกษ": "Si Sa Ket", "ศรสี ะเกษ": "Si Sa Ket",
    "นครศรีธรรมราช": "Nakhon Si Thammarat", "นครศรธี รรมราช": "Nakhon Si Thammarat",
    "พัทลงุ": "Phatthalung",
}

# Rows to skip (national/region totals, headers)
SKIP_NAMES = {
    "รวมทั้งประเทศ", "ภาคเหนือ", "ภาคตะวันออกเฉียงเหนือ",
    "ภาคกลาง", "ภาคใต้", "ภาคใต", "ประเทศ/ภาค/จังหวัด",
    "ประเทศ/ภาค", "/จังหวัด", "ก", "ล", "อ", "ภาคใต",
}

# ── Number reconstruction ─────────────────────────────────────────────────────
def clean_number(s: str) -> float | None:
    """Remove spaces, Thai private-use chars, then parse."""
    s = re.sub(r"[-\s]", "", s)
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def merge_number_tokens(tokens: list[str]) -> list[float]:
    """
    Merge split number fragments back into 5 values:
      area_planted, area_harvested, production, yield_planted, yield_harvested

    Split pattern: '6 2,838,047' → tokens ['6', '2,838,047']
    Rules:
      - single digit followed by token starting with digit or ',' → merge
    """
    merged = []
    i = 0
    while i < len(tokens):
        tok = tokens[i].strip()
        if not tok:
            i += 1
            continue
        # peek next token for merge
        if (i + 1 < len(tokens) and
                re.fullmatch(r"\d", tok) and
                re.match(r"[,\d]", tokens[i + 1].strip())):
            merged.append(tok + tokens[i + 1].strip())
            i += 2
        else:
            merged.append(tok)
            i += 1

    nums = []
    for m in merged:
        v = clean_number(m)
        if v is not None:
            nums.append(v)
    return nums


# ── PDF parser ────────────────────────────────────────────────────────────────
def parse_pdf(path: str, year_be: int, season: str) -> list[dict]:
    """Extract province-level rows from one OAE PDF."""
    rows = []
    year_ce = year_be - 543

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            # Try table extraction first (works on cleaner PDFs)
            tables = page.extract_tables()
            if tables and len(tables[0]) > 4:
                for row in tables[0]:
                    if row[0] is None:
                        continue
                    name = row[0].replace("\n", "").strip()
                    if name in SKIP_NAMES or not name:
                        continue
                    # collect numeric cells
                    num_tokens = [str(c or "") for c in row[1:]]
                    nums = merge_number_tokens(num_tokens)
                    if len(nums) >= 4:
                        rows.append(_make_row(name, nums, year_be, year_ce, season, path))
                continue  # done with this page via table method

            # Fallback: word-position grouping
            words = page.extract_words()
            if not words:
                continue

            # Group words by y-line (tolerance 4px)
            lines: dict[int, list] = {}
            for w in words:
                y = round(w["top"] / 4) * 4
                lines.setdefault(y, []).append(w)

            for y_key in sorted(lines):
                line_words = sorted(lines[y_key], key=lambda w: w["x0"])
                tokens = [w["text"] for w in line_words]
                if not tokens:
                    continue
                name = tokens[0].strip()
                if name in SKIP_NAMES or not name or re.fullmatch(r"[\d,. ]+", name):
                    continue
                # must start with Thai char
                if not re.match(r"[฀-๿]", name):
                    continue
                nums = merge_number_tokens(tokens[1:])
                if len(nums) >= 4:
                    rows.append(_make_row(name, nums, year_be, year_ce, season, path))

    return rows


def _make_row(name, nums, year_be, year_ce, season, path):
    # Normalise private-use Thai chars in name
    clean_name = re.sub(r"[-]", "", name).strip()
    eng = PROVINCE_EN.get(clean_name, clean_name)
    return {
        "year_BE":          year_be,
        "year_CE":          year_ce,
        "season":           season,
        "province_th":      clean_name,
        "province_en":      eng,
        "area_planted_rai": nums[0] if len(nums) > 0 else None,
        "area_harvested_rai": nums[1] if len(nums) > 1 else None,
        "production_ton":   nums[2] if len(nums) > 2 else None,
        "yield_planted_kg_rai": nums[3] if len(nums) > 3 else None,
        "yield_harvested_kg_rai": nums[4] if len(nums) > 4 else None,
        "source_file":      path,
    }


# ── Run all files ─────────────────────────────────────────────────────────────
PDF_DIR = os.path.join(_HERE, "..", "resources", "data")

FILES = [
    ("OAE (2022) Main Season.pdf", 2565, "main"),
    ("OAE (2023) Main Season.pdf", 2566, "main"),
    ("OAE (2024) Main Season.pdf", 2567, "main"),
    ("OAE (2022) Dry Season.pdf",  2565, "dry"),
    ("OAE (2023) Dry Season.pdf",  2566, "dry"),
    ("OAE (2024) Dry Season.pdf",  2567, "dry"),
    ("OAE (2025) Dry Season.pdf",  2568, "dry"),
]

all_rows = []
for fname, yr, season in FILES:
    fpath = f"{PDF_DIR}/{fname}"
    print(f"Parsing {fname} ...", end=" ")
    try:
        r = parse_pdf(fpath, yr, season)
        print(f"{len(r)} rows")
        all_rows.extend(r)
    except Exception as e:
        print(f"ERROR: {e}")

df = pd.DataFrame(all_rows)

# Convert rai → hectares (1 ha = 6.25 rai)
df["area_harvested_ha"] = df["area_harvested_rai"] / 6.25

# Drop fragments and header re-rows
df = df[df["area_harvested_rai"] > 100].copy()
df = df[df["province_th"].str.len() >= 3].copy()
df = df.drop_duplicates(subset=["year_BE", "season", "province_th"])
df = df.sort_values(["year_BE", "season", "province_th"]).reset_index(drop=True)

out_path = os.path.join(_HERE, "..", "resources", "clean", "oae_provincial_rice_2022_2024.csv")
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"\nSaved {len(df)} rows → {out_path}")
print(df[["year_CE", "season", "province_en", "area_harvested_ha", "production_ton"]].head(15).to_string())
