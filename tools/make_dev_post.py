"""Write docs/DEV_POST.md: the paper with absolute image links and DEV front matter, ready to paste into dev.to.

    python3 tools/make_dev_post.py

Copyright Matthew Armstrong (https://github.com/The-Dorkknight). PolyForm Noncommercial 1.0.0. No warranty.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/The-Dorkknight/putting-plastic-on-a-pedestal/main/"
BLOB = "https://github.com/The-Dorkknight/putting-plastic-on-a-pedestal/blob/main/"
TAGS = "cura-plugin, support-structures, filament-saving, defensive-publication"   # the repo's four topics, same order

md = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
md = re.sub(r"<!--.*?-->\n*", "", md, flags=re.S)
md = re.sub(r"!\[[^\]]*\]\(docs/images/cover\.jpg\)\n*", "", md)            # DEV shows it as the cover image
md = re.sub(r"^# .*\n", "", md, count=1, flags=re.M)                        # DEV shows the title
md = re.sub(r"\]\((docs/images/[^)]+)\)", lambda m: "](" + RAW + m.group(1) + ")", md)
md = re.sub(r"\]\((?!https?:|#)([^)]+)\)", lambda m: "](" + BLOB + m.group(1) + ")", md)
front = f"""---
title: "Putting Plastic on a Pedestal: experimental methods of plastic waste reduction for 3D printing"
published: false
tags: {TAGS}
cover_image: {RAW}docs/images/cover.jpg
canonical_url: https://github.com/The-Dorkknight/putting-plastic-on-a-pedestal
---

"""
open(os.path.join(ROOT, "docs", "DEV_POST.md"), "w", encoding="utf-8").write(front + md.lstrip())
print("wrote docs/DEV_POST.md")
