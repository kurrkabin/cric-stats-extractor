import streamlit as st
from bs4 import BeautifulSoup

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
        elif {"bowling", "w", "econ"}.issubset(heads):
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
        heads  = [th.get_text(strip=True).lower() for th in tbl.find_all("th")]
        r_idx  = heads.index("r") if "r" in heads else 3
        w_idx  = heads.index("w") if "w" in heads else 4

        for row in tbl.find_all("tr")[1:]:
            tds = row.find_all("td")
            if len(tds) <= max(r_idx, w_idx):
                continue
            name = tds[0].get_text(strip=True).split("(")[0].strip()
            try:
                runs = int(tds[r_idx].get_text(strip=True))
                wkts = int(tds[w_idx].get_text(strip=True))
            except ValueError:
                continue
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
if st.button("Extract Stats"):
    if html.strip():
        st.markdown(extract(html), unsafe_allow_html=True)
    else:
        st.warning("❗ Please paste the HTML first.")
