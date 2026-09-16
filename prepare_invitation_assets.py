"""Embed the supplied card and verified Telegram QR into the single-file invitation."""

import base64
import io
import re
from pathlib import Path

from PIL import Image
import zxingcpp


def image_uri(path, size, image_format, **options):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format=image_format, **options)
    mime = "image/png" if image_format == "PNG" else "image/webp"
    return "data:" + mime + ";base64," + base64.b64encode(output.getvalue()).decode("ascii"), image


card_uri, _ = image_uri(
    "uploads/787027db-1811-4e56-82d6-ea84344c5bf9.jpg",
    (1024, 628), "WEBP", quality=90, method=6
)
qr_uri, qr = image_uri("uploads/newQRcodeTelegram.png", (640, 640), "PNG", optimize=True)
expected = "https://t.me/+eiml8r0MzA02YWM6"
for width in (640, 280, 224):
    decoded = zxingcpp.read_barcodes(qr.resize((width, width), Image.Resampling.LANCZOS))
    assert any(result.text == expected for result in decoded), f"QR failed at {width}px"

path = Path("outputs/taklifnoma.html")
html = path.read_text(encoding="utf-8")
for element_id, uri in (("gift-card-image", card_uri), ("wedding-qr-image", qr_uri)):
    pattern = rf'(<img\b[^>]*\bid="{element_id}"[^>]*\bsrc=")[^"]*(")'
    html, count = re.subn(pattern, lambda match: match[1] + uri + match[2], html)
    assert count == 1, f"Expected one image: {element_id}"
assert "__GIFT_CARD_IMAGE__" not in html and "__WEDDING_QR_IMAGE__" not in html
path.write_text(html, encoding="utf-8")
Path("outputs/taklifnoma-code.txt").write_text(html, encoding="utf-8")
print("Embedded both supplied images. Telegram QR verified at 640, 280, and 224 pixels.")
