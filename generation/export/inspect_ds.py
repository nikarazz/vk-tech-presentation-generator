from parser.parse_template import parse_template
import json

ds = parse_template("data/templates/template1.pptx")

print("=" * 60)
print("META")
print("=" * 60)
print(json.dumps(ds["meta"], indent=2, ensure_ascii=False))

print()
print("=" * 60)
print("PATTERNS")
print("=" * 60)
for pid, p in ds["patterns"].items():
    print(f"\n[{pid}]")
    print(f"  layout_ref: {p.get('layout_ref')}")
    print(f"  usage_count: {p.get('usage_count')}")
    print(f"  placeholders:")
    for ph in p.get("placeholders", []):
        print(f"    {ph}")

print()
print("=" * 60)
print("GRID")
print("=" * 60)
print(json.dumps(ds.get("grid", {}), indent=2, ensure_ascii=False))
