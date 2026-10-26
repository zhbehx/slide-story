"""生成 PPT 叙事大纲 的社交预览图（GitHub Social Preview，1280×640）。

用法：python market/make_preview.py
依赖：Pillow（pip install pillow），中文字体用系统自带的微软雅黑。
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
BG = (11, 15, 23)
INK = (248, 250, 252)
MUTED = (100, 116, 139)
DIM = (148, 163, 184)
ACCENT = (239, 68, 68)
GOOD = (34, 197, 94)
CARD = (17, 24, 39)
CARD_LINE = (31, 41, 59)

FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"

SPEC = {
    "title": 'PPT 叙事大纲',
    "sub": 'slide-story · Agent Skill',
    "desc": '先定结论 · 三个论点 · 判断句标题',
    "big": '0',
    "arrow": '100',
    "big_note": '废页大纲改成决策稿，实测得分',
    "tags": 'MIT · 零依赖 · 中文优先',
}

OUT = Path(__file__).resolve().parent / "social-preview.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def main() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    for i in range(160):
        alpha = int(10 - i / 20)
        if alpha > 0:
            d.line([(0, i), (W, i)], fill=(30, 41, 59))

    d.rectangle([64, 96, 72, 158], fill=ACCENT)
    d.text((104, 92), SPEC["title"], font=font(76, True), fill=INK)
    d.text((104, 196), SPEC["sub"], font=font(32), fill=MUTED)
    d.text((104, 288), SPEC["desc"], font=font(36), fill=DIM)

    d.rounded_rectangle([812, 214, 1216, 462], radius=20, fill=CARD, outline=CARD_LINE, width=2)
    d.text((856, 248), SPEC["big"], font=font(72, True), fill=MUTED)
    d.text((856, 330), "→ " + SPEC["arrow"], font=font(72, True), fill=GOOD)
    d.text((860, 418), SPEC["big_note"], font=font(24), fill=DIM)

    d.line([(104, 520), (1216, 520)], fill=(30, 41, 59))
    d.text((104, 552), SPEC["tags"], font=font(28), fill=(71, 85, 105))

    img.save(OUT)
    print(f"已生成 {OUT}")


if __name__ == "__main__":
    main()
