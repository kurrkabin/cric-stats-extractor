# 🏏 Cricket Stats Extractor - Ready-to-Use Template

## Excel Template Layout

```
   A              B              C              D              E
1  [ESPN HTML]                                  Stat           Value
2                                               Highest...     Player (123) – Team
3                                               Top Batter-A   Player (95)
4                                               Top Batter-B   Player (87)
5                                               Total Fours    Team A 45 : 38 Team B
6                                               Most Sixes     Team A 12 : 8 Team B
7                                               Run Outs       Team B 3 : 1 Team A
8  
9  [Extract Stats Button]  [Clear Data Button]
```

## Google Sheets Template Layout

```
   A              B              C              D              E
1  [ESPN HTML]                                  Stat           Value
2                                               Highest...     Player (123) – Team
3                                               Top Batter-A   Player (95)
4                                               Top Batter-B   Player (87)
5                                               Total Fours    Team A 45 : 38 Team B
6                                               Most Sixes     Team A 12 : 8 Team B
7                                               Run Outs       Team B 3 : 1 Team A
8  
9  Menu: 🏏 Cricket Stats → Extract Stats | Clear Data
```

## Quick Setup - Excel

1. **Open Excel** and create new workbook
2. **Enable macros**: File → Options → Trust Center → Trust Center Settings → Macro Settings → Enable all macros
3. **Open VBA Editor**: Alt + F11
4. **Insert Module**: Insert → Module
5. **Paste the VBA code** from `Cricket_Stats_Extractor.xlsx`
6. **Save as .xlsm** file
7. **Add buttons** (optional):
   - Developer tab → Insert → Button
   - Draw button in cell A9
   - Assign macro: `ExtractCricketStats`
   - Add another button for `ClearData`

## Quick Setup - Google Sheets

1. **Open Google Sheets** and create new spreadsheet
2. **Access Apps Script**: Extensions → Apps Script
3. **Clear default code** and paste code from `Google_Sheets_Cricket_Stats.gs`
4. **Save script**: Ctrl + S
5. **Authorize**: Run any function once to authorize
6. **Return to spreadsheet** - you'll see "🏏 Cricket Stats" menu

## Usage Instructions

### Step 1: Get ESPN HTML
- Go to ESPN cricket scorecard page
- Press `Ctrl+U` (View Page Source)
- Select all (`Ctrl+A`) and copy (`Ctrl+C`)

### Step 2: Paste in Cell A1
- Click cell A1 in your Excel/Google Sheets
- Paste the HTML content (`Ctrl+V`)

### Step 3: Extract Stats
**Excel:** Click "Extract Stats" button or press Alt+F8 → Run ExtractCricketStats
**Google Sheets:** Use menu "🏏 Cricket Stats" → "Extract Stats"

### Step 4: View Results
- Stats appear in columns D-E
- Two-column format: Stat | Value
- Automatically formatted with borders

## Example Result

| Stat | Value |
|------|-------|
| Highest Individual Score | Kohli (183) – India |
| Top Batter – India | Kohli (183) |
| Top Batter – Australia | Smith (131) |
| Total Match Fours | India 87 : 65 Australia |
| Most Match Sixes | India 12 : 8 Australia |
| Most Run Outs (by bowling side) | Australia 2 : 1 India |

## Multiple Matches

For multiple matches, use different sections:

```
   A              B              C              D              E
1  [Match 1 HTML]                               Match 1 Stats   
2                                               
7                                               
8  
9  [Match 2 HTML]                               Match 2 Stats
10                                              
15                                              
```

## Troubleshooting Quick Fixes

**Excel:**
- If macros don't work: File → Options → Trust Center → Enable macros
- If "Object error": Save as .xlsm file
- If permission denied: Run Excel as administrator

**Google Sheets:**
- If script won't run: Extensions → Apps Script → Authorize
- If no menu appears: Refresh the page after adding script
- If formula doesn't work: Use `=EXTRACT_CRICKET_STATS(A1)` exactly

## Features Summary

✅ **Paste HTML directly** in cell A1
✅ **Automatic extraction** with one click/menu
✅ **Two-column output** (Stat | Value)
✅ **Professional formatting** with borders
✅ **Error handling** with clear messages
✅ **Multiple match support** in same sheet
✅ **Works offline** (Excel) or **cloud-based** (Google Sheets)

## File Downloads

- `Cricket_Stats_Extractor.xlsx` - Excel VBA code
- `Google_Sheets_Cricket_Stats.gs` - Google Apps Script code
- `EXCEL_GOOGLE_SHEETS_GUIDE.md` - Complete setup guide

*Ready to extract cricket stats directly in your spreadsheet! 🏏*