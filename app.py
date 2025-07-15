import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="Cricket Stats Extractor", layout="centered")
st.title("🏏 Cricket Stats Extractor")
st.markdown("_Paste the full HTML source (Ctrl+U, then Ctrl+A, Ctrl+C) from an ESPNcricinfo scorecard._")

raw_html = st.text_area("Paste HTML here:", height=350)
run = st.button("Extract Stats")

def bold(text):
    return f"**{text}**"

def nice_line(left_team, left_val, right_team, right_val):
    left = f"{left_team} {left_val}"
    right = f"{right_val} {right_team}"
    if left_val > right_val:
        left = bold(left)
    elif right_val > left_val:
        right = bold(right)
    return f"{left} : {right}"

def extract_cricket_stats(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    title_tag = soup.find("h1") or soup.find("title")
    match_title = title_tag.get_text(" ", strip=True) if title_tag else "Match Summary"
    teams = []
    for span in soup.select("span.ds-text-title-xs.ds-font-bold.ds-capitalize"):
        t = span.get_text(strip=True).replace(" Innings", "")
        if t and t not in teams:
            teams.append(t)
    if len(teams) < 2:
        return "❌ Could not detect both teams."

    bats, bowls = [], []
    for tbl in soup.find_all("table"):
        heads = [th.get_text(strip=True).lower() for th in tbl.find_all("th")]
        if {"batting", "4s", "6s"}.issubset(heads):
            bats.append(tbl)
        elif {"bowling", "w", "econ"}.issubset(heads):
            bowls.append(tbl)

    fours = {t: 0 for t in teams}
    sixes = {t: 0 for t in teams}
    runouts = {t: 0 for t in teams}
    batter_team, top_bat, top_all = {}, {}, {}

    for i, tbl in enumerate(bats):
        bat_t, bowl_t = teams[i % 2], teams[1 - (i % 2)]
        best_n, best_r = "", 0

        for row in tbl.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 7:
                continue
            name = cols[0].get_text(strip=True).split("(")[0].strip()
            try:
                runs = int(cols[2].get_text(strip=True))
                _4 = int(cols[5].get_text(strip=True))
                _6 = int(cols[6].get_text(strip=True))
            except ValueError:
                continue

            fours[bat_t] += _4
            sixes[bat_t] += _6
            batter_team[name] = bat_t
            top_all[name] = max(runs, top_all.get(name, 0))

            if runs > best_r:
                best_n, best_r = name, runs

            if "run out" in " ".join(td.get_text(strip=True).lower() for td in row):
                runouts[bowl_t] += 1

        top_bat[bat_t] = (best_n, best_r)

    # highest individual batter
    hi_name, hi_runs = max(top_all.items(), key=lambda x: x[1])
    hi_team = batter_team.get(hi_name, "Unknown")

    lines = [
        f"### {match_title}",
        "",
        f"🏅 Highest Individual Score: {hi_name} ({hi_runs}) – {hi_team}",
        "",
        f"4️⃣ Total Match Fours: {nice_line(teams[0], fours[teams[0]], teams[1], fours[teams[1]])}",
        f"6️⃣ Total Match Sixes: {nice_line(teams[0], sixes[teams[0]], teams[1], sixes[teams[1]])}",
        "",
        f"🏏 Top Batter – {teams[0]}: {top_bat.get(teams[0], ('N/A',0))[0]} ({top_bat.get(teams[0], ('',0))[1]})",
        f"🏏 Top Batter – {teams[1]}: {top_bat.get(teams[1], ('N/A',0))[0]} ({top_bat.get(teams[1], ('',0))[1]})",
        "",
        f"🏃 Most Run Outs (by bowling side): {nice_line(teams[0], runouts[teams[0]], teams[1], runouts[teams[1]])}",
    ]
    return "\n".join(lines)

if run:
    if not raw_html.strip():
        st.error("❗ Please paste the HTML first.")
    else:
        stats = extract_cricket_stats(raw_html)
        if stats.startswith("❌"):
            st.error(stats)
        else:
            st.markdown(stats)
