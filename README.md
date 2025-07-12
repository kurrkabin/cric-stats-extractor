# 🏏 Cricket Stats Extractor - Excel & Google Sheets

Standalone solutions for extracting cricket statistics directly from ESPN scorecard HTML in Excel and Google Sheets.

## ✨ What You Get

- **Excel Workbook** with VBA macros for HTML processing
- **Google Sheets** with Google Apps Script for cloud-based extraction
- **Direct HTML pasting** - no external tools needed
- **Two-column format** - Stat | Value layout as requested
- **One-click extraction** - paste HTML and get instant stats

## 🎯 How It Works

1. **Get ESPN HTML**: Go to cricket scorecard → Ctrl+U → Copy all
2. **Paste in Cell A1**: Open your Excel/Google Sheets → Paste HTML
3. **Extract Stats**: Click button (Excel) or menu (Google Sheets)
4. **View Results**: Stats appear in columns D-E automatically

## 📊 Solutions Available

### Excel Solution
- **VBA Macros** for HTML parsing
- **Offline processing** - works without internet
- **Macro buttons** for one-click extraction
- **Professional formatting** with borders

### Google Sheets Solution
- **Google Apps Script** for cloud processing
- **Custom menu** integration
- **Formula support** - `=EXTRACT_CRICKET_STATS(A1)`
- **Mobile compatible** - works on phones/tablets

## � Quick Start

### Excel Setup
1. Create new Excel workbook (.xlsm)
2. Enable macros in Trust Center
3. Add VBA code from `Cricket_Stats_Extractor.xlsx`
4. Save and test with ESPN HTML

### Google Sheets Setup
1. Create new Google Sheets document
2. Go to Extensions → Apps Script
3. Paste code from `Google_Sheets_Cricket_Stats.gs`
4. Authorize and test with ESPN HTML

## � Template Layout

```
   A              B              C              D              E
1  [ESPN HTML]                                  Stat           Value
2                                               Highest...     Player (123) – Team
3                                               Top Batter-A   Player (95)
4                                               Top Batter-B   Player (87)
5                                               Total Fours    Team A 45 : 38 Team B
6                                               Most Sixes     Team A 12 : 8 Team B
7                                               Run Outs       Team B 3 : 1 Team A
```

## 📁 Files

- **`Cricket_Stats_Extractor.xlsx`** - Excel VBA code
- **`Google_Sheets_Cricket_Stats.gs`** - Google Apps Script code
- **`EXCEL_GOOGLE_SHEETS_GUIDE.md`** - Complete setup guide
- **`Cricket_Stats_Template.md`** - Ready-to-use template
- **`Test_Cricket_Matches.ipynb`** - Original Jupyter notebook (alternative)

## 🚀 Example Output

| Stat | Value |
|------|-------|
| Highest Individual Score | Kohli (183) – India |
| Top Batter – India | Kohli (183) |
| Top Batter – Australia | Smith (131) |
| Total Match Fours | India 87 : 65 Australia |
| Most Match Sixes | India 12 : 8 Australia |
| Most Run Outs (by bowling side) | Australia 2 : 1 India |

## 📖 Documentation

- **[Complete Setup Guide](EXCEL_GOOGLE_SHEETS_GUIDE.md)** - Step-by-step instructions
- **[Ready-to-Use Template](Cricket_Stats_Template.md)** - Quick start template
- **[Original Notebook](Test_Cricket_Matches.ipynb)** - Jupyter alternative

## 🔧 Features

✅ **Paste HTML directly** in cell A1
✅ **Automatic extraction** with one click/menu
✅ **Two-column output** (Stat | Value)
✅ **Professional formatting** with borders
✅ **Error handling** with clear messages
✅ **Multiple match support** in same sheet
✅ **Works offline** (Excel) or **cloud-based** (Google Sheets)

## 📞 Support

Common issues and solutions in the [troubleshooting section](EXCEL_GOOGLE_SHEETS_GUIDE.md#troubleshooting).

---

*Standalone Excel and Google Sheets solutions for cricket stats extraction* 🏏
