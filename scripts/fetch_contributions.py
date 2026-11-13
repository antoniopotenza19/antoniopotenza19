"""Fetch GitHub's public calendar; preserve good data if parsing fails."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import json
import re
import time
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def parse_calendar(markup):
    soup = BeautifulSoup(markup, "html.parser")
    tips = {tip.get("for"): tip.get_text(" ", strip=True)
            for tip in soup.select("tool-tip[for]")}
    days = {}
    for cell in soup.select(".ContributionCalendar-day[data-date]"):
        day = date.fromisoformat(cell["data-date"]).isoformat()
        tip = tips.get(cell.get("id"), "")
        count = re.match(r"([\d,]+) contributions?\b", tip, re.I)
        if re.match(r"No contributions?\b", tip, re.I):
            value = 0
        elif count:
            value = int(count[1].replace(",", ""))
        else:
            raise ValueError(f"Missing contribution count for {day}: {tip!r}")
        level = int(cell.get("data-level", 0))
        if not 0 <= level <= 4:
            raise ValueError(f"Unexpected contribution level: {level}")
        days[day] = {"date": day, "count": value, "level": level}
    result = [days[key] for key in sorted(days)]
    if not 350 <= len(result) <= 371:
        raise ValueError(f"Expected a full calendar, received {len(result)} days")
    for a, b in zip(result, result[1:]):
        if date.fromisoformat(b["date"]) - date.fromisoformat(a["date"]) != timedelta(days=1):
            raise ValueError("Calendar contains a date gap")
    return result


def summarize(days):
    today = date.today().isoformat()
    days = [day for day in days if day["date"] <= today]
    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)
    recent = days[:-1] if days[-1]["date"] == today and not days[-1]["count"] else days
    current = 0
    for day in reversed(recent):
        if not day["count"]:
            break
        current += 1
    return {"total": sum(day["count"] for day in days),
            "active_days": sum(day["count"] > 0 for day in days),
            "current_streak": current, "longest_streak": longest}


def main():
    username = json.loads((ROOT / "profile.json").read_text())["username"]
    url = f"https://github.com/users/{username}/contributions"
    request = Request(url, headers={"User-Agent": "profile-art/1.0", "Accept-Language": "en-US"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                days = parse_calendar(response.read().decode("utf-8"))
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    data = {"username": username, "source": url,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stats": summarize(days), "days": days}
    target = ROOT / "data/contributions.json"
    target.parent.mkdir(exist_ok=True)
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temp.replace(target)
    print(f"Fetched {len(days)} days: {data['stats']['total']} contributions")


if __name__ == "__main__":
    main()
