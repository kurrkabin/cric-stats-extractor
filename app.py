import streamlit as st
from bs4 import BeautifulSoup
import re
import io, csv


st.set_page_config(layout="wide")
st.title("Cricket Scorecard Extractor 🏏")
st.markdown(
    "Paste the **full** HTML source (Ctrl‑U → Ctrl‑A → Ctrl‑C) of an ESPNcricinfo "
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

        for row in tbl.find_all("tr")[1:]:
            tds = row.find_all("td")
            if len(tds) < 7:
                continue
            name = tds[0].get_text(strip=True).split("(")[0].strip()
            try:
                runs = int(tds[2].get_text(strip=True))
                _4s  = int(tds[5].get_text(strip=True))
                _6s  = int(tds[6].get_text(strip=True))
            except ValueError:
                continue

            fours[bat_t] += _4s
            sixes[bat_t] += _6s
            batter_team[name] = bat_t
            top_all[name] = max(runs, top_all.get(name, 0))

            # ── choose top batter(s) for this team ──────────
            if runs > best_r:
                best_r, best_names = runs, [name]   # new leader
            elif runs == best_r:
                best_names.append(name)             # tie → add

            # count run‑outs credited to bowling side
            if "run out" in " ".join(td.get_text(strip=True).lower() for td in row):
                runouts[bowl_t] += 1

        top_bat[bat_t] = (best_names, best_r)

    # ── bowling tables ───────────────────────────────────────
    bowl_stats = {t: [] for t in teams}
    for i, tbl in enumerate(bowl_tbls):
        bowl_t = teams[1 - (i % 2)]
        heads = [th.get_text(" ", strip=True).lower().replace("\xa0", " ") for th in tbl.find_all("th")]

        def _find_idx(options, default=None):
            for o in options:
                if o in heads:
                    return heads.index(o)
            return default

        # accept “r” or “runs”, and “w/wk/wkts/wickets”
        r_idx = _find_idx(("r", "runs"), 3)
        w_idx = _find_idx(("w", "wk", "wkts", "wickets"), 4)

        for row in tbl.find_all("tr")[1:]:
            tds = row.find_all("td")
            if len(tds) <= max(r_idx, w_idx):
                continue

            # bowler name (skip Extras/Total rows)
            name = tds[0].get_text(" ", strip=True).split("(")[0].strip()
            if not name or name.lower().startswith(("extras", "total")):
                continue

            # tolerant numeric parsing (handles dashes/extra text)
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
        # many wickets first, then fewest runs
        lst.sort(key=lambda x: (-x[1], x[2]))
        top_w = lst[0][1]
        best_r = min(r for _, w, r in lst if w == top_w)
        return [f"{n} ({w})" for n, w, r in lst if w == top_w and r == best_r]

    top_bowl = {t: best_bowler(bowl_stats[t]) for t in teams}

    # ── highest individual score overall ─────────────────────
    hi_name, hi_runs = max(top_all.items(), key=lambda x: x[1])
    hi_team = batter_team.get(hi_name, "Unknown")

    # ── assemble markdown ────────────────────────────────────
    md = "\n".join([
        f"### {m_title}",
        "",
        f"🏅 Highest Individual Score: {hi_name} ({hi_runs}) – {hi_team}  ",
        "",
        f"4️⃣ Total Match Fours: {nice_line(teams[0], fours[teams[0]], teams[1], fours[teams[1]])}  ",
        f"6️⃣ Total Match Sixes: {nice_line(teams[0], sixes[teams[0]], teams[1], sixes[teams[1]])}  ",
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
