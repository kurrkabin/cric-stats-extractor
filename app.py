import json
import csv
import io
import re
from pathlib import Path

import streamlit as st
from bs4 import BeautifulSoup


st.set_page_config(layout="wide")
st.title("Cricket Scorecard Extractor 🏏")
st.markdown(
    "Paste the **full** HTML source (Ctrl-U → Ctrl-A → Ctrl-C) of an ESPNcricinfo "
    "scorecard, then click **Extract Stats**."
)

html = st.text_area("HTML source:", height=400)

# Optional: only changes how teams are DISPLAYED.
# It does NOT change which team receives each stat.
swap_display_order = st.checkbox(
    "Swap displayed team order only",
    value=False,
)

# ── tiny helpers ──────────────────────────────────────────────
bold = lambda t: f"**{t}**"

def nice_line(l_team, l_val, r_team, r_val):
    left, right = f"{l_team} {l_val}", f"{r_val} {r_team}"
    if l_val > r_val:
        left = bold(left)
    elif r_val > l_val:
        right = bold(right)
    return f"{left} : {right}"

def squash(text):
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())

def dedupe_keep_order(items):
    out = []
    seen = set()
    for item in items:
        item = (item or "").strip()
        key = squash(item)
        if item and key and key not in seen:
            seen.add(key)
            out.append(item)
    return out

def extract_title_teams(title_text):
    if not title_text:
        return []
    m = re.search(r"^\s*(.+?)\s+vs\.?\s+(.+?)(?:,|\s+-|$)", title_text, re.I)
    if not m:
        return []
    return dedupe_keep_order([m.group(1).strip(), m.group(2).strip()])

def extract_structured_teams(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        raw_json = script.string or script.get_text(" ", strip=True)
        if not raw_json:
            continue

        try:
            data = json.loads(raw_json)
        except Exception:
            continue

        payloads = data if isinstance(data, list) else [data]
        for payload in payloads:
            if not isinstance(payload, dict):
                continue

            items = payload.get("@graph", [payload])
            for item in items:
                if not isinstance(item, dict):
                    continue

                if item.get("@type") == "SportsEvent":
                    home = ((item.get("homeTeam") or {}).get("name") or "").strip()
                    away = ((item.get("awayTeam") or {}).get("name") or "").strip()
                    teams = dedupe_keep_order([home, away])
                    if len(teams) == 2:
                        return teams
    return []

def clean_innings_team(text):
    text = (text or "").strip()
    m = re.search(r"^(.+?)\s+(?:\d+(?:st|nd|rd|th)\s+)?innings\b", text, re.I)
    if not m:
        return None
    team = m.group(1).strip(" :-|")
    team = re.sub(r"\s+", " ", team).strip()
    return team or None

def extract_innings_heading_teams(soup):
    found = []
    for tag in soup.find_all(["h2", "h3", "h4", "h5", "h6", "span", "div", "strong", "p"]):
        team = clean_innings_team(tag.get_text(" ", strip=True))
        if team:
            found.append(team)
    return dedupe_keep_order(found)

def extract_legacy_teams(soup):
    found = []
    for span in soup.select("span.ds-text-title-xs.ds-font-bold.ds-capitalize"):
        team = clean_innings_team(span.get_text(" ", strip=True))
        if team:
            found.append(team)
    return dedupe_keep_order(found)

def best_match_team(text, teams):
    raw = squash(text)
    if not raw:
        return None

    best_team = None
    best_score = 0

    for team in teams:
        team_key = squash(team)
        if not team_key:
            continue

        if raw == team_key:
            return team

        if raw in team_key or team_key in raw:
            score = min(len(raw), len(team_key))
            if score > best_score:
                best_team = team
                best_score = score

    return best_team

def find_table_batting_team(tbl, teams):
    for prev in tbl.find_all_previous(limit=120):
        if not getattr(prev, "name", None):
            continue

        text = prev.get_text(" ", strip=True)
        if not text or "innings" not in text.lower():
            continue

        raw_team = clean_innings_team(text)
        if not raw_team:
            continue

        matched = best_match_team(raw_team, teams)
        if matched:
            return matched

    return None

def other_team(team, teams):
    for t in teams:
        if t != team:
            return t
    return None

# ── main extractor ────────────────────────────────────────────
def extract(raw, swap_display=False):
    soup = BeautifulSoup(raw, "html.parser")

    title_tag = soup.find("h1") or soup.find("title")
    m_title = title_tag.get_text(" ", strip=True) if title_tag else "Match Summary"

    title_teams = extract_title_teams(m_title)
    structured_teams = extract_structured_teams(soup)
    innings_teams = extract_innings_heading_teams(soup)
    legacy_teams = extract_legacy_teams(soup)

    # Prefer innings headings first because they are closest to the actual batting tables.
    teams = []
    for candidate_list in (innings_teams, structured_teams, legacy_teams, title_teams):
        if len(candidate_list) >= 2:
            teams = candidate_list[:2]
            break

    if len(teams) < 2:
        return "❌ Could not detect both teams."

    display_teams = teams[::-1] if swap_display else teams[:]

    # ── split batting / bowling tables ───────────────────────
    bat_tbls, bowl_tbls = [], []
    for tbl in soup.find_all("table"):
        heads = [th.get_text(" ", strip=True).lower().replace("\xa0", " ") for th in tbl.find_all("th")]
        if {"batting", "4s", "6s"}.issubset(set(heads)):
            bat_tbls.append(tbl)
        elif "bowling" in heads and any(h in heads for h in ("w", "wk", "wkts", "wickets")):
            bowl_tbls.append(tbl)

    fours = {t: 0 for t in teams}
    sixes = {t: 0 for t in teams}
    runouts = {t: 0 for t in teams}

    top_bat = {t: (["N/A"], 0) for t in teams}
    best_overall_name = "N/A"
    best_overall_runs = 0
    best_overall_team = "Unknown"

    # ── batting tables ───────────────────────────────────────
    for i, tbl in enumerate(bat_tbls):
        bat_t = find_table_batting_team(tbl, teams) or teams[i % 2]
        bowl_t = other_team(bat_t, teams)

        best_r = 0
        best_names = []

        for row in tbl.find_all("tr")[1:]:
            tds = row.find_all("td")
            if len(tds) < 7:
                continue

            name = tds[0].get_text(" ", strip=True).split("(")[0].strip()
            if not name or name.lower().startswith(("extras", "total", "did not bat", "fall of wickets")):
                continue

            try:
                runs = int(tds[2].get_text(strip=True))
                _4s = int(tds[5].get_text(strip=True))
                _6s = int(tds[6].get_text(strip=True))
            except ValueError:
                continue

            fours[bat_t] += _4s
            sixes[bat_t] += _6s

            if runs > best_overall_runs:
                best_overall_name = name
                best_overall_runs = runs
                best_overall_team = bat_t

            if runs > best_r:
                best_r = runs
                best_names = [name]
            elif runs == best_r:
                best_names.append(name)

            row_text = " ".join(td.get_text(" ", strip=True).lower() for td in tds)
            if bowl_t and "run out" in row_text:
                runouts[bowl_t] += 1

        if best_names:
            top_bat[bat_t] = (best_names, best_r)

    # ── bowling tables ───────────────────────────────────────
    bowl_stats = {t: [] for t in teams}
    for i, tbl in enumerate(bowl_tbls):
        batting_team_for_section = find_table_batting_team(tbl, teams) or teams[i % 2]
        bowl_t = other_team(batting_team_for_section, teams)

        if not bowl_t:
            continue

        heads = [th.get_text(" ", strip=True).lower().replace("\xa0", " ") for th in tbl.find_all("th")]

        def _find_idx(options, default=None):
            for o in options:
                if o in heads:
                    return heads.index(o)
            return default

        r_idx = _find_idx(("r", "runs"), 3)
        w_idx = _find_idx(("w", "wk", "wkts", "wickets"), 4)

        for row in tbl.find_all("tr")[1:]:
            tds = row.find_all("td")
            if r_idx is None or w_idx is None or len(tds) <= max(r_idx, w_idx):
                continue

            name = tds[0].get_text(" ", strip=True).split("(")[0].strip()
            if not name or name.lower().startswith(("extras", "total")):
                continue

            runs_txt = tds[r_idx].get_text(strip=True)
            wkts_txt = tds[w_idx].get_text(strip=True)

            m_r = re.search(r"\d+", runs_txt)
            m_w = re.search(r"\d+", wkts_txt)

            runs = int(m_r.group()) if m_r else 0
            wkts = int(m_w.group()) if m_w else 0

            bowl_stats[bowl_t].append((name, wkts, runs))

    def best_bowler(lst):
        if not lst:
            return ["No wickets"]
        lst = sorted(lst, key=lambda x: (-x[1], x[2], x[0].lower()))
        top_w = lst[0][1]
        if top_w == 0:
            return ["No wickets"]
        best_r = min(r for _, w, r in lst if w == top_w)
        return [f"{n} ({w})" for n, w, r in lst if w == top_w and r == best_r]

    top_bowl = {t: best_bowler(bowl_stats[t]) for t in teams}

    left_team, right_team = display_teams[0], display_teams[1]

    # ── assemble markdown ────────────────────────────────────
    md = "\n".join([
        f"### {m_title}",
        "",
        f"🏅 Highest Individual Score: {best_overall_name} ({best_overall_runs}) – {best_overall_team}  ",
        "",
        f"4️⃣ Total Match Fours: {nice_line(left_team, fours[left_team], right_team, fours[right_team])}  ",
        f"6️⃣ Total Match Sixes: {nice_line(left_team, sixes[left_team], right_team, sixes[right_team])}  ",
        "",
        f"🏏 Top Batter – {left_team}: {', '.join(top_bat[left_team][0])} ({top_bat[left_team][1]})  ",
        f"🏏 Top Batter – {right_team}: {', '.join(top_bat[right_team][0])} ({top_bat[right_team][1]})  ",
        "",
        f"⚾ Top Bowler – {left_team}: {', '.join(top_bowl[left_team])}  ",
        f"⚾ Top Bowler – {right_team}: {', '.join(top_bowl[right_team])}  ",
        "",
        f"🏃 Most Run Outs (by bowling side): {nice_line(left_team, runouts[left_team], right_team, runouts[right_team])}  ",
    ])
    return md

# ── run button ──────────────────────────────────────────────
if st.button("Extract Stats"):
    if html.strip():
        res = extract(html, swap_display=swap_display_order)
        st.markdown(res, unsafe_allow_html=True)

        # CSV export (self-contained)
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

        # Usage counter
        try:
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
            total_uses = st.session_state.get("_session_count", 0) + 1
            st.session_state["_session_count"] = total_uses

        st.caption(f"Used {total_uses} times.")
    else:
        st.warning("❗ Please paste the HTML first.")
