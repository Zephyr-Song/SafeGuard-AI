import os
import sys
from pathlib import Path
from PIL import Image

IMG_DIR = Path("D:/WorkBuddy/SafeGuard-AI-merge/static/safebars_mirror/img")
BACKUP_DIR = IMG_DIR / "_watermarked_originals"
BACKUP_DIR.mkdir(exist_ok=True)

# Crop bottom 80px.  The WorkBuddy/AI-generated watermark appears in the
# bottom-right corner; removing the bottom strip keeps the editorial subject
# intact while producing a clean, watermark-free image.
CROP_BOTTOM = 80

def process(path: Path) -> Path:
    im = Image.open(path)
    w, h = im.size
    if h <= CROP_BOTTOM:
        return path
    cropped = im.crop((0, 0, w, h - CROP_BOTTOM))
    # Save original to backup before overwriting.
    backup = BACKUP_DIR / path.name
    if not backup.exists():
        im.save(backup)
    cropped.save(path)
    return path

if __name__ == "__main__":
    for f in sorted(IMG_DIR.glob("*.png")):
        if f.parent.name == "_watermarked_originals":
            continue
        process(f)
        print(f"cropped {f.name}")
    print("done")
