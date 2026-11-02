"""Cek isi repo sebelum di-upload: python validate.py"""
import json, pathlib, re, sys

root = pathlib.Path(__file__).parent
index = json.loads((root / "index.json").read_text(encoding="utf-8"))
errors, warnings = [], []
REQUIRED = ["id", "title", "artist", "audioId", "BackgroundImage", "AlbumImage"]
STAMP = re.compile(r"^\[(\d+):(\d+(?:\.\d+)?)\]")

ids = [s.get("id") for s in index]
for dup in {i for i in ids if ids.count(i) > 1}:
    errors.append(f"id ganda: {dup}")

for s in index:
    sid = s.get("id", "?")
    for key in REQUIRED:
        if not s.get(key):
            errors.append(f"[{sid}] field '{key}' kosong")
    if not re.fullmatch(r"[a-z0-9-]+", str(sid)):
        errors.append(f"[{sid}] id hanya boleh huruf kecil, angka, dan tanda hubung")
    f = root / "lyrics" / f"{sid}.lrc"
    if not f.exists():
        errors.append(f"[{sid}] file lyrics/{sid}.lrc tidak ada")
        continue
    last, count = -1.0, 0
    for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        m = STAMP.match(line)
        if not m:
            continue
        t = int(m.group(1)) * 60 + float(m.group(2))
        count += 1
        if t < last:
            warnings.append(f"[{sid}] baris {n}: waktu mundur ({t} < {last})")
        last = t
    if count == 0:
        errors.append(f"[{sid}] tidak ada baris lirik bertimestamp")

for f in (root / "lyrics").glob("*.lrc"):
    if f.stem not in ids:
        warnings.append(f"lyrics/{f.name} tidak ada di index.json")

for w in warnings: print("PERINGATAN:", w)
for e in errors: print("ERROR:", e)
print(f"{len(index)} lagu, {len(errors)} error, {len(warnings)} peringatan")
sys.exit(1 if errors else 0)
