"""Prepare the cartoon's ASCII portrait and subset licensed Google Fonts locally."""
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from PIL import Image, ImageEnhance, ImageOps
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = [
    ("ofl/instrumentserif/InstrumentSerif-Regular.ttf", "serif.woff", None),
    ("ofl/instrumentserif/InstrumentSerif-Italic.ttf", "serif-italic.woff", None),
    ("ofl/geist/Geist%5Bwght%5D.ttf", "sans.woff", 400),
    ("ofl/geist/Geist%5Bwght%5D.ttf", "sans-bold.woff", 600),
    ("ofl/geistmono/GeistMono%5Bwght%5D.ttf", "mono.woff", 400),
]


def main():
    (ROOT / "fonts").mkdir(exist_ok=True)
    for source, name, weight in FONTS:
        with urlopen("https://raw.githubusercontent.com/google/fonts/main/" + source, timeout=30) as response:
            font = TTFont(BytesIO(response.read()))
        if weight:
            font = instantiateVariableFont(font, {"wght": weight}, inplace=True)
        options = subset.Options()
        options.flavor = "woff"
        sub = subset.Subsetter(options=options)
        sub.populate(unicodes=list(range(32,256)) + [0x2197,0x2192,0x2022,0x2013,0x2014,0x2019])
        sub.subset(font)
        font.flavor = "woff"
        font.save(ROOT / "fonts" / name)
    portrait = Image.open(ROOT / "assets/antonio-cartoon.png").convert("RGBA")
    # Face and hair only. The generated image has a real alpha channel.
    w, h = portrait.size
    portrait = portrait.crop((int(w*.245),0,int(w*.785),int(h*.67)))
    paper = Image.new("RGBA", portrait.size, "white")
    paper.alpha_composite(portrait)
    gray = ImageEnhance.Contrast(ImageOps.grayscale(paper)).enhance(1.35)
    cols = 150
    rows = round(cols * gray.height / gray.width * .49)
    gray = gray.resize((cols, rows), Image.Resampling.LANCZOS)
    ramp = " .:-=+*#%@"
    lines = [''.join(ramp[min(9,int((1-gray.getpixel((x,y))/255)**1.35*10))] for x in range(cols)) for y in range(rows)]
    (ROOT / "data/portrait-ascii.txt").write_text('\n'.join(lines)+'\n', encoding="utf-8")
    print(f"Prepared five font subsets and {cols} x {rows} ASCII portrait")


if __name__ == '__main__':
    main()
