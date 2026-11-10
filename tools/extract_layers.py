"""Extract a few layers from Cura G-code files into small JSON files (data/layers_*.json),
so the paper's figures can be redrawn without the 40 MB G-code files.

Each record: extrusion segments [x0, y0, x1, y1] grouped by kind:
  part   - the model's own walls/skin/infill
  tower  - Hybrid Supports towers (;MESH:HybridTower...)
  cap    - Hybrid Supports interface cap (;MESH:HybridCap...)
  support - Cura's own support (;TYPE:SUPPORT...)

Usage: python3 extract_layers.py OUT.json GCODE Z [Z ...]
Copyright Matthew Armstrong (https://github.com/The-Dorkknight). PolyForm Noncommercial 1.0.0. No warranty.
"""
import json
import re
import sys


def extract(path, zs, tol=0.11):
    want = {round(z, 2): {"part": [], "tower": [], "cap": [], "support": []} for z in zs}
    x = y = z = 0.0
    e = 0.0
    rel = False
    mesh, typ = "", ""
    for line in open(path, errors="replace"):
        if line.startswith(";MESH:"):
            mesh = line[6:].strip()
            continue
        if line.startswith(";TYPE:"):
            typ = line[6:].strip()
            continue
        if line.startswith("M83"):
            rel = True
        elif line.startswith("M82"):
            rel = False
        if line.startswith("G92"):
            m = re.search(r"E(-?[\d.]+)", line)
            if m:
                e = float(m.group(1))
            continue
        if not line.startswith(("G0", "G1")):
            continue
        d = {k: float(v) for k, v in re.findall(r"([XYZE])(-?[\d.]+)", line.split(";")[0])}
        nx, ny, nz = d.get("X", x), d.get("Y", y), d.get("Z", z)
        ext = False
        if "E" in d:
            de = d["E"] if rel else d["E"] - e
            if not rel:
                e = d["E"]
            ext = de > 0 and ("X" in d or "Y" in d)
        if ext:
            for k, rec in want.items():
                if abs(nz - k) < tol:
                    kind = ("tower" if mesh.startswith("HybridTower") else "cap" if mesh.startswith("HybridCap")
                            else "support" if typ.startswith("SUPPORT") else "part")
                    rec[kind].append([round(x, 2), round(y, 2), round(nx, 2), round(ny, 2)])
        x, y, z = nx, ny, nz
    return {str(k): v for k, v in want.items()}


if __name__ == "__main__":
    out, g, *zs = sys.argv[1:]
    data = extract(g, [float(v) for v in zs])
    json.dump(data, open(out, "w"), separators=(",", ":"))
    for k, v in data.items():
        print(out, k, {kk: len(vv) for kk, vv in v.items()})
