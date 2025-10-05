**Cricket Scorecard Extractor 🏏
**
Turn messy ESPNcricinfo scorecards into clean, audited summaries in seconds.

What it does:
Paste the full HTML source of an ESPNcricinfo match page → get a structured summary:

**Highest individual score (with player & team)
**
**Top batters per team (ties handled)
**
**Top bowlers per team (most wickets, then fewest runs)
**
**Total 4s/6s by team
**
**Run-out count credited to the bowling side
**
**One-click CSV export (+ optional usage logging)
**
This solves a common Ops/Risk/Data pain: “We need quick, consistent, auditable summaries from raw scorecards—no manual formatting.”

**Why this matters (for Sports Ops / Risk / Automation)
**
Consistency → fewer settling disputes. Rules baked into code (tie rules, wicket/run ordering).

Speed multiplier. Works with any ESPNcricinfo scorecard, no custom mappings needed.


Quick Demo (60s)

Open the Streamlit app.

On a scorecard page press Ctrl+U → Ctrl+A → Ctrl+C (copy page source).

Paste into the textbox → Extract Stats.

Review summary → Download CSV.

Example output (Markdown):
