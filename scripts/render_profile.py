"""Generate self-contained SVGs. The daily job renders only the heatmap."""
from datetime import date, timedelta
from html import escape
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
BG, BORDER, TEXT, MUTED, GREEN, CYAN = "#0d1117", "#30363d", "#e6edf3", "#919ba8", "#56d38a", "#72d5e8"
FONT = "Consolas, 'Liberation Mono', monospace"


def text(x, y, value, size=12, color=TEXT, extra=""):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" {extra}>{escape(str(value))}</text>'


def frame(w, h, title, description):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" font-family="{FONT}">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<style>@keyframes reveal{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}.reveal{animation:reveal .45s both}@media(prefers-reduced-motion:reduce){.reveal{animation:none}.scan{display:none}}</style>',
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
            f'<path d="M1 36H{w-1}" stroke="{BORDER}"/>',
            *[f'<circle cx="{20+i*16}" cy="18" r="4" fill="{c}"/>' for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])],
            text(w-17, 22, title, 10, MUTED, 'text-anchor="end"')]


def write(name, parts):
    (ROOT / name).write_text("\n".join(parts + ["</svg>"]) + "\n", encoding="utf-8")
    print(f"Rendered {name}")


def heatmap(profile):
    data = json.loads((ROOT / "data/contributions.json").read_text())
    days, stats = data["days"], data["stats"]
    if data["username"] != profile["username"]:
        raise ValueError("Contribution data belongs to a different account")
    first = date.fromisoformat(days[0]["date"])
    start = first - timedelta(days=(first.weekday()+1) % 7)
    p = frame(860, 278, "activity.log", f"{stats['total']} GitHub contributions; updated {data['generated_at']}")
    p += [text(24, 66, f"{profile['username']}@github", 13, GREEN), text(836, 66, "LAST 12 MONTHS", 10, MUTED, 'text-anchor="end"')]
    palette = ["#1b222b", "#0e4429", "#006d32", "#26a641", "#56d38a"]
    month_seen = set()
    for day in days:
        d = date.fromisoformat(day["date"])
        col, row = divmod((d-start).days, 7)
        x, y = 48+col*14.8, 99+row*14.8
        if (d.year, d.month) not in month_seen and d.day <= 7:
            month_seen.add((d.year, d.month))
            p.append(text(x, 89, d.strftime("%b"), 9, MUTED))
        p.append(f'<rect class="reveal" x="{x:.1f}" y="{y:.1f}" width="11.5" height="11.5" rx="2" fill="{palette[day["level"]]}" style="animation-delay:{col*.018+row*.035:.3f}s"><title>{day["date"]}: {day["count"]} contributions</title></rect>')
    for r, label in [(1,"Mon"), (3,"Wed"), (5,"Fri")]:
        p.append(text(18, 108+r*14.8, label, 8, MUTED))
    p += [text(24, 222, f"{stats['total']:,} contributions", 14, GREEN), text(24, 249, f"{stats['active_days']} active days  /  current streak {stats['current_streak']}d  /  longest {stats['longest_streak']}d", 10, MUTED),
          text(836, 249, f"updated {data['generated_at'][:10]} UTC", 9, MUTED, 'text-anchor="end"'), text(706, 220, "Less", 9, MUTED)]
    for i, color in enumerate(palette):
        p.append(f'<rect x="{737+i*14}" y="211" width="10" height="10" rx="2" fill="{color}"/>')
    p.append(text(810, 220, "More", 9, MUTED))
    write("contrib-heatmap.svg", p)


def info(profile):
    p = frame(490, 390, "profile.conf", "Antonio Potenza: industrial data and automation, education, tools and current focus")
    p += [text(23, 68, profile["name"], 23), text(23, 94, profile["title"], 14, CYAN), text(23, 116, profile["subtitle"], 12, MUTED), f'<path d="M23 135H467" stroke="{BORDER}"/>']
    rows = [("Study", profile["study"]), ("At", profile["education"]), ("Focus", profile["focus"][0]), ("", profile["focus"][1]), ("Stack", profile["stack"][0]), ("", profile["stack"][1]), ("Build", "Industrial monitoring platforms"), ("Explore", "Simulation & predictive maintenance")]
    for i, (label, value) in enumerate(rows):
        p += [f'<g class="reveal" style="animation-delay:{.22+i*.15:.2f}s">', text(23, 162+i*24, label, 11, GREEN), text(83, 162+i*24, value, 11), '</g>']
    p += [f'<path d="M23 354H467" stroke="{BORDER}"/>', text(23, 377, "$ turning machine data into insights", 11, MUTED)]
    write("info-card.svg", p)


def portrait(profile):
    from PIL import Image, ImageDraw, ImageEnhance, ImageOps
    image = Image.open(ROOT / "avatar.png").convert("RGB").resize((460, 460))
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).polygon([(154,95),(164,48),(194,22),(248,12),(289,23),(321,41),(340,77),(332,101),(323,116),(320,146),(305,171),(340,180),(379,192),(402,229),(411,295),(72,295),(79,234),(119,199),(175,174),(163,147)], fill=255)
    image = Image.composite(image, Image.new("RGB", image.size, "white"), mask).crop((66,5,417,300))
    gray = ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(1.3)
    cols, rows = 90, 42
    gray = gray.resize((cols, rows), Image.Resampling.LANCZOS)
    ramp = " .:-=+*#%@"
    lines = ["".join(ramp[min(9, int((1-gray.getpixel((x,y))/255)*10))] for x in range(cols)) for y in range(rows)]
    p = frame(370, 390, "portrait.sh", "Monochrome ASCII rendering of Antonio's GitHub avatar")
    for y, line in enumerate(lines):
        p.append(text(20, 55+y*6.7, line, 6.3, "#c9d1d9", 'xml:space="preserve" textLength="330" lengthAdjust="spacingAndGlyphs"'))
    # Base art remains visible when animation is unavailable.
    p += [f'<rect class="scan" x="19" y="44" width="332" height="0" fill="{BG}"><animate attributeName="y" from="44" to="331" dur="3.6s" fill="freeze"/><animate attributeName="height" from="286" to="0" dur="3.6s" fill="freeze"/></rect>',
          f'<path d="M20 354H350" stroke="{BORDER}"/>', text(20, 377, "$ whoami", 11, GREEN), text(86, 377, profile["name"], 11)]
    write("antonio-ascii.svg", p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--heatmap-only", action="store_true")
    args = parser.parse_args()
    profile = json.loads((ROOT / "profile.json").read_text())
    heatmap(profile)
    if not args.heatmap_only:
        info(profile)
        portrait(profile)


if __name__ == "__main__":
    main()
