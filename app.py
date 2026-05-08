import streamlit as st
from bs4 import BeautifulSoup
import json
import re
import io, csv
from pathlib import Path


st.set_page_config(layout="wide")
st.title("Cricket Scorecard Extractor 🏏")
st.markdown(
    "Paste the **full** HTML source (Ctrl‑U → Ctrl‑A → Ctrl‑C) of an ESPNcricinfo "
    "scorecard, then click **Extract Stats**."
)

html = st.text_area("HTML source:", height=400)

# ── tiny helpers ──────────────────────────────────────────────
bold = lambda t: f"**{t}**"
def nice_line(l_team, l_val, r_team, r_val):
    left, right = f"{l_team} {l_val}", f"{r_val} {r_team}"
    if l_val > r_val:      left  = bold(left)
    elif r_val > l_val:    right = bold(right)
    return f"{left} : {right}"


def clean_team_name(text):
    """Normalize a candidate team name scraped from ESPNcricinfo markup/JSON."""
    if not text:
        return ""

    name = re.sub(r"\s+", " ", str(text)).strip()
    name = re.sub(r"\s+Innings\s*$", "", name, flags=re.I).strip()
    name = re.sub(r"\s+Men\s*$", "", name, flags=re.I).strip()

    if not name or len(name) > 60:
        return ""

    lowered = name.lower()
    blocked = {
        "batting",
        "bowling",
        "extras",
        "full scorecard",
        "innings",
        "match summary",
        "scorecard",
        "total",
    }
    if lowered in blocked or any(ch in name for ch in "{}<>[]"):
        return ""

    return name


def add_team(teams, candidate):
    name = clean_team_name(candidate)
    if name and name not in teams:
        teams.append(name)


def extract_json_objects(raw, soup):
    """Return JSON blobs embedded in ESPNcricinfo's Ctrl+U page source."""
    json_objects = []

    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data and next_data.string:
        json_objects.append(next_data.string)

    for script in soup.find_all("script"):
        text = script.string or script.get_text()
        if text and text.lstrip().startswith("{") and text not in json_objects:
            json_objects.append(text)

    parsed = []
    for obj in json_objects:
        try:
            parsed.append(json.loads(obj))
        except json.JSONDecodeError:
            continue
    return parsed


def detect_teams(raw, soup):
    """Detect the two scorecard teams from rendered HTML or embedded Next.js JSON."""
    teams = []

    # Rendered ESPN scorecards often expose headings as visible span text.
    for span in soup.select("span.ds-text-title-xs.ds-font-bold.ds-capitalize"):
        add_team(teams, span.get_text(strip=True))

    # Ctrl+U source can include innings headings even when the exact CSS selector changes.
    innings_re = re.compile(r"^(.+?)\s+Innings$", re.I)
    for tag in soup.find_all(string=innings_re):
        match = innings_re.match(tag.strip())
        if match:
            add_team(teams, match.group(1))
        if len(teams) >= 2:
            return teams[:2]

    # Newer ESPNcricinfo pages keep the canonical data in __NEXT_DATA__. Walk only
    # team-shaped objects/keys so player names are not mistaken for team names.
    def walk(obj, parent_key=""):
        if len(teams) >= 2:
            return
        if isinstance(obj, dict):
            for key in ("team", "inningTeam", "homeTeam", "awayTeam", "team1", "team2"):
                value = obj.get(key)
                if isinstance(value, dict):
                    add_team(teams, value.get("longName") or value.get("name") or value.get("displayName"))
                elif isinstance(value, str) and key != "team":
                    add_team(teams, value)
                if len(teams) >= 2:
                    return

            for key in ("teamName", "teamDisplayName", "teamLongName"):
                add_team(teams, obj.get(key))
                if len(teams) >= 2:
                    return

            if parent_key in {"teams", "team", "inningTeam", "homeTeam", "awayTeam", "team1", "team2"}:
                add_team(teams, obj.get("longName") or obj.get("name") or obj.get("displayName"))
                if len(teams) >= 2:
                    return

            for key, value in obj.items():
                walk(value, key)
                if len(teams) >= 2:
                    return
        elif isinstance(obj, list):
            for item in obj:
                walk(item, parent_key)
                if len(teams) >= 2:
                    return

    for data in extract_json_objects(raw, soup):
        walk(data)
        if len(teams) >= 2:
            return teams[:2]

    # Last resort for escaped JSON in script bundles: look for team-name keys.
    for pattern in (
        r'"teamName"\s*:\s*"([^"]+)"',
        r'"teamDisplayName"\s*:\s*"([^"]+)"',
        r'"longName"\s*:\s*"([^"]+)"',
    ):
        for match in re.finditer(pattern, raw):
            add_team(teams, match.group(1))
            if len(teams) >= 2:
                return teams[:2]

    return teams[:2]

# ── main extractor ────────────────────────────────────────────
def extract(raw):
    soup = BeautifulSoup(raw, "html.parser")

    title_tag = soup.find("h1") or soup.find("title")
    m_title   = title_tag.get_text(" ", strip=True) if title_tag else "Match Summary"

    # ── teams ────────────────────────────────────────────────
    teams = []
    for span in soup.select("span.ds-text-title-xs.ds-font-bold.ds-capitalize"):
        t = span.get_text(strip=True).replace(" Innings", "")
        if t and t not in teams:
            teams.append(t)
    teams = detect_teams(raw, soup)
    if len(teams) < 2:
        return "❌ Could not detect both teams."

    # ── split batting / bowling tables ───────────────────────
    bat_tbls, bowl_tbls = [], []
    for tbl in soup.find_all("table"):
        heads = [th.get_text(strip=True).lower() for th in tbl.find_all("th")]
        if {"batting", "4s", "6s"}.issubset(heads):
            bat_tbls.append(tbl)
        elif "bowling" in heads and any(h in heads for h in ("w", "wk", "wkts", "wickets")):

            bowl_tbls.append(tbl)

    fours   = {t: 0 for t in teams}
    sixes   = {t: 0 for t in teams}
    runouts = {t: 0 for t in teams}

    top_bat, top_all, batter_team = {}, {}, {}

    # ── batting tables ───────────────────────────────────────
    for i, tbl in enumerate(bat_tbls):
        bat_t, bowl_t = teams[i % 2], teams[1 - (i % 2)]

        best_r = 0
        best_names = []                   # ← track *all* batters with best_r
@@ -147,62 +273,59 @@ def extract(raw):
        f"🏅 Highest Individual Score: {hi_name} ({hi_runs}) – {hi_team}  ",
        "",
        f"4️⃣ Total Match Fours: {nice_line(teams[0], fours[teams[0]], teams[1], fours[teams[1]])}  ",
        f"6️⃣ Total Match Sixes: {nice_line(teams[0], sixes[teams[0]], teams[1], sixes[teams[1]])}  ",
        "",
        f"🏏 Top Batter – {teams[0]}: {', '.join(top_bat[teams[0]][0])} "
        f"({top_bat[teams[0]][1]})  ",
        f"🏏 Top Batter – {teams[1]}: {', '.join(top_bat[teams[1]][0])} "
        f"({top_bat[teams[1]][1]})  ",
        "",
        f"⚾ Top Bowler – {teams[0]}: {', '.join(top_bowl[teams[0]])}  ",
        f"⚾ Top Bowler – {teams[1]}: {', '.join(top_bowl[teams[1]])}  ",
        "",
        f"🏃 Most Run Outs (by bowling side): "
        f"{nice_line(teams[0], runouts[teams[0]], teams[1], runouts[teams[1]])}  ",
    ])
    return md

# ── run button ──────────────────────────────────────────────
if st.button("Extract Stats"):
    if html.strip():
        res = extract(html)  # store the result once
        st.markdown(res, unsafe_allow_html=True)

        # CSV export (self-contained)
        import io, csv
        match_title = res.splitlines()[0].lstrip("# ").strip() if res else "Match Summary"
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["match", "output"])
        writer.writerow([match_title, res])
        csv_bytes = buf.getvalue().encode("utf-8-sig")

        st.download_button(
            label="Download CSV of this result",
            data=csv_bytes,
            file_name="scorecard_extract.csv",
            mime="text/csv",
        )

        # Subtle usage counter (placed at the very end of the block)
        try:
            import json
            from pathlib import Path
            COUNTER_FILE = Path("usage_count.json")
            data = {}
            if COUNTER_FILE.exists():
                try:
                    data = json.loads(COUNTER_FILE.read_text() or "{}")
                except Exception:
                    data = {}
            total_uses = int(data.get("count", 0)) + 1
            data["count"] = total_uses
            COUNTER_FILE.write_text(json.dumps(data))
        except Exception:
            # Fallback: per-session count only (doesn't persist across restarts)
            total_uses = st.session_state.get("_session_count", 0) + 1
            st.session_state["_session_count"] = total_uses

        st.caption(f"Used {total_uses} times.")
    else:
        st.warning("❗ Please paste the HTML first.")
