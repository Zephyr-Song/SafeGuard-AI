import re, json, sys
html = open("_cgpt_share.html", encoding="utf-8").read()
# find client-bootstrap json
m = re.search(r'<script type="application/json" id="client-bootstrap">(.*?)</script>', html, re.S)
print("client-bootstrap found:", bool(m))
if not m:
    sys.exit(1)
data = json.loads(m.group(1))
# Recursively collect text from anything that looks like message content
def walk(o, path=""):
    if isinstance(o, dict):
        for k,v in o.items():
            yield from walk(v, path+"/"+str(k))
    elif isinstance(o, list):
        for i,v in enumerate(o):
            yield from walk(v, path+f"[{i}]")
    elif isinstance(o, str):
        yield (path, o)
# Find nodes mentioning our topic
hits = []
for path, txt in walk(data):
    if len(txt) > 30 and ("SafeBARS" in txt or "Ethical" in txt or "two future" in txt.lower() or "role swap" in txt.lower() or "condition" in txt.lower() or "visualization" in txt.lower() or "participant" in txt.lower()):
        hits.append((path, txt))
print("topic hits:", len(hits))
for path, txt in hits[:200]:
    print("\n==== PATH:", path, "====")
    print(txt[:1500])
