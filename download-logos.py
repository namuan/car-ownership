#!/usr/bin/env python3
"""Download car brand logos from Wikipedia to car-logos/.
Single script — handles multiple Wikipedia title attempts and known file names."""
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

OUTDIR = Path(__file__).parent / "car-logos"
OUTDIR.mkdir(exist_ok=True)

# (filename, [Wikipedia page titles to try], [known logo file names])
BRANDS = [
    ("Volkswagen",      ["Volkswagen"]),
    ("Skoda",           ["Škoda Auto"]),
    ("SEAT",            ["SEAT"]),
    ("CUPRA",           ["Cupra (marque)"]),
    ("Audi",            ["Audi", "Audi AG"]),
    ("Porsche",         ["Porsche"]),
    ("Bentley",         ["Bentley"]),
    ("Lamborghini",     ["Lamborghini"]),
    ("Ducati",          ["Ducati"]),
    ("Jeep",            ["Jeep"]),
    ("Ram",             ["Ram Trucks", "Ram (marque)"],
                         ["File:Ram_Trucks_logo.svg", "File:Ram logo.svg"]),
    ("Peugeot",         ["Peugeot"],
                         ["File:Peugeot_Logo.svg"]),
    ("FIAT",            ["Fiat", "Fiat Automobiles"],
                         ["File:Fiat_Automobiles_logo.svg"]),
    ("Chrysler",        ["Chrysler", "Chrysler (brand)"]),
    ("Dodge",           ["Dodge", "Dodge (automobile)"]),
    ("Citroen",         ["Citroën"]),
    ("Opel",            ["Opel"]),
    ("Vauxhall",        ["Vauxhall Motors", "Vauxhall (car)"]),
    ("Alfa_Romeo",      ["Alfa Romeo"]),
    ("DS_Automobiles",  ["DS Automobiles"]),
    ("Lancia",          ["Lancia", "Lancia (company)"]),
    ("Abarth",          ["Abarth", "Abarth & C. S.p.A."],
                         ["File:Abarth_logo.svg", "File:Abarth logo.svg"]),
    ("Maserati",        ["Maserati"]),
    ("Toyota",          ["Toyota"]),
    ("Lexus",           ["Lexus"]),
    ("Daihatsu",        ["Daihatsu"]),
    ("Hino",            ["Hino Motors"]),
    ("Subaru",          ["Subaru"]),
    ("Mazda",           ["Mazda"]),
    ("Renault",         ["Renault"]),
    ("Dacia",           ["Dacia", "Automobile Dacia", "Dacia (car)"]),
    ("Alpine",          ["Alpine (automobile)", "Alpine (car)"],
                         ["File:Alpine_(automobile)_logo.svg"]),
    ("Nissan",          ["Nissan"]),
    ("Infiniti",        ["Infiniti"]),
    ("Mitsubishi",      ["Mitsubishi Motors"]),
    ("Hyundai",         ["Hyundai Motor Company"]),
    ("Kia",             ["Kia"]),
    ("Genesis",         ["Genesis Motor"]),
    ("Geely_Auto",      ["Geely", "Geely Auto"]),
    ("Zeekr",           ["Zeekr"],
                         ["File:Zeekr_logo.svg"]),
    ("Lynk_and_Co",     ["Lynk & Co"],
                         ["File:Lynk & Co logo.svg"]),
    ("Volvo_Cars",      ["Volvo Cars"]),
    ("Polestar",        ["Polestar"]),
    ("Lotus",           ["Lotus Cars"]),
    ("Smart",           ["Smart (marque)"]),
    ("Chevrolet",       ["Chevrolet"]),
    ("GMC",             ["GMC (automobile)", "GMC (marque)"]),
    ("Cadillac",        ["Cadillac", "Cadillac Motor Car Division"],
                         ["File:Cadillac_logo.svg"]),
    ("Ford",            ["Ford Motor Company"]),
    ("Lincoln",         ["Lincoln Motor Company"]),
    ("Jaguar",          ["Jaguar Cars"]),
    ("Land_Rover",      ["Land Rover", "Land Rover (car)"]),
    ("Tesla",           ["Tesla, Inc."]),
    ("BYD",             ["BYD Auto"]),
    ("BMW",             ["BMW"]),
    ("MINI",            ["Mini (marque)"]),
    ("Rolls_Royce",     ["Rolls-Royce Motor Cars"]),
]

API_BASE = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "CarLogosDownloader/1.0"}


def api_get(params, retries=3):
    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep((attempt + 1) * 4)
                continue
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return None
    return None


def get_logo_from_page(page_title):
    """Try to get a logo URL from a Wikipedia page."""
    # Pass 1: pageimages (infobox image)
    data = api_get({
        "action": "query", "titles": page_title,
        "prop": "pageimages", "format": "json",
        "pithumbsize": "400", "origin": "*",
    })
    if data:
        pages = data.get("query", {}).get("pages", {})
        for pid, pinfo in pages.items():
            if pid != "-1" and "thumbnail" in pinfo:
                return pinfo["thumbnail"]["source"]

    # Pass 2: search images for logo files
    data = api_get({
        "action": "query", "titles": page_title,
        "prop": "images", "format": "json",
        "imlimit": "20", "origin": "*",
    })
    if not data:
        return None

    pages = data.get("query", {}).get("pages", {})
    candidates = []
    for pid, pinfo in pages.items():
        for img in pinfo.get("images", []):
            t = img.get("title", "")
            if any(k in t.lower() for k in ["logo", "brand", "emblem", "wordmark"]):
                candidates.insert(0, t)
            elif t.lower().startswith("file:") and t.lower().endswith((".svg", ".png")):
                if not any(k in t.lower() for k in ["icon", "flag", "map", "chart", "photo", "building"]):
                    candidates.append(t)

    for ct in candidates[:5]:
        data = api_get({
            "action": "query", "titles": ct,
            "prop": "imageinfo", "iiprop": "url",
            "format": "json", "origin": "*",
        })
        if data:
            pages3 = data.get("query", {}).get("pages", {})
            for pid, pinfo in pages3.items():
                ii = pinfo.get("imageinfo", [])
                if ii:
                    return ii[0]["url"]
    return None


def get_logo_from_file(file_title):
    """Get image URL from a known Wikipedia file name."""
    data = api_get({
        "action": "query", "titles": file_title,
        "prop": "imageinfo", "iiprop": "url",
        "format": "json", "origin": "*",
    })
    if data:
        pages = data.get("query", {}).get("pages", {})
        for pid, pinfo in pages.items():
            if pid == "-1":
                continue
            ii = pinfo.get("imageinfo", [])
            if ii:
                return ii[0]["url"]
    return None


def download_file(url, path):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = resp.read()
                if len(data) < 2000:
                    return False
                path.write_bytes(data)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(5)
                continue
            return False
        except Exception:
            if attempt < 2:
                time.sleep(3)
                continue
            return False
    return False


ok = 0
fail = 0
skipped = 0
existing = {f.stem for f in OUTDIR.iterdir() if f.stat().st_size >= 2000}

# Clean up any leftover tiny placeholders
for f in OUTDIR.iterdir():
    if f.stat().st_size < 2000:
        f.unlink()

print(f"Downloading {len(BRANDS)} car brand logos to {OUTDIR} ...\n")

for entry in BRANDS:
    name = entry[0]
    page_titles = entry[1]
    known_files = entry[2] if len(entry) > 2 else []

    if name in existing:
        print(f"  {name:<22} ⊘ already downloaded, skip")
        skipped += 1
        continue

    print(f"  {name:<22}", end=" ", flush=True)

    img_url = None

    # Pass 1: try each Wikipedia page title
    for title in page_titles:
        img_url = get_logo_from_page(title)
        if img_url:
            break
        time.sleep(0.8)

    # Pass 2: try known file names
    if not img_url:
        for ft in known_files:
            img_url = get_logo_from_file(ft)
            if img_url:
                break
            time.sleep(1)

    if not img_url:
        print("✗ no logo found")
        fail += 1
        time.sleep(1.5)
        continue

    # Download
    ext = img_url.rsplit(".", 1)[-1].split("?")[0]
    if ext not in ("svg", "png", "jpg", "jpeg", "gif", "webp"):
        ext = "png"
    out_path = OUTDIR / f"{name}.{ext}"

    try:
        success = download_file(img_url, out_path)
        if success:
            size = out_path.stat().st_size
            print(f"✓ {ext} ({size:,} bytes)")
            ok += 1
        else:
            print("✗ too small / invalid")
            out_path.unlink(missing_ok=True)
            fail += 1
    except Exception as e:
        print(f"✗ {e}")
        out_path.unlink(missing_ok=True)
        fail += 1

    time.sleep(2)

print(f"\nDone: {ok} downloaded, {skipped} skipped, {fail} failed (out of {len(BRANDS)})")
print(f"Logos in: {OUTDIR}")
files = sorted(OUTDIR.iterdir())
for f in files:
    print(f"  {f.name} ({f.stat().st_size:,} bytes)")
