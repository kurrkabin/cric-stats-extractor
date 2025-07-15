# 🏏 Cricket Stats Extractor - Excel & Google Sheets Guide

## Overview
This guide provides two standalone solutions for extracting cricket statistics directly from ESPN scorecard HTML:
1. **Excel Workbook** with VBA macros
2. **Google Sheets** with Google Apps Script

Simply paste the ESPN HTML and get your two-column stats instantly!

## 📊 Solution 1: Excel Workbook

### Setup Instructions

1. **Create New Excel Workbook**
   - Open Microsoft Excel
   - Create a new blank workbook
   - Save it as "Cricket_Stats_Extractor.xlsm" (enable macros)

2. **Add VBA Code**
   - Press `Alt + F11` to open VBA Editor
   - Insert → Module
   - Copy and paste the VBA code from `Cricket_Stats_Extractor.xlsx`
   - Save the workbook

3. **Create Buttons (Optional)**
   - Go to Developer tab → Insert → Button
   - Draw button and assign `ExtractCricketStats` macro
   - Add another button for `ClearData` macro

### How to Use Excel Solution

1. **Get ESPN HTML**
   - Go to ESPN cricket scorecard page
   - Press `Ctrl+U` (View Source)
   - Copy all HTML content

2. **Paste in Excel**
   - Paste the HTML content in cell **A1**
   - The cell will expand to fit the content

3. **Extract Stats**
   - Click the "Extract Stats" button, OR
   - Press `Alt + F8` → Select "ExtractCricketStats" → Run

4. **View Results**
   - Stats appear in columns **D-E** in 2-column format
   - Automatically formatted with borders and bold headers

### Excel Features
- ✅ Automatic HTML parsing
- ✅ Two-column Stat/Value format
- ✅ Auto-formatted output with borders
- ✅ Clear data function
- ✅ Error handling with message boxes
- ✅ Works offline

---

## 📈 Solution 2: Google Sheets

### Setup Instructions

1. **Create New Google Sheet**
   - Go to [sheets.google.com](https://sheets.google.com)
   - Create a new blank spreadsheet
   - Name it "Cricket Stats Extractor"

2. **Add Google Apps Script**
   - Extensions → Apps Script
   - Delete default code
   - Copy and paste the code from `Google_Sheets_Cricket_Stats.gs`
   - Save the script (Ctrl+S)

3. **Authorize Script**
   - Run any function once to authorize
   - Accept permissions when prompted

### How to Use Google Sheets Solution

#### Method 1: Using Menu (Recommended)
1. **Get ESPN HTML**
   - Go to ESPN cricket scorecard page
   - Press `Ctrl+U` (View Source)
   - Copy all HTML content

2. **Paste in Google Sheets**
   - Paste HTML content in cell **A1**
   - The cell will expand to accommodate the content

3. **Extract Stats**
   - Use the "🏏 Cricket Stats" menu (appears after setup)
   - Click "Extract Stats"

4. **View Results**
   - Stats appear in columns **D-E**
   - Automatically formatted with borders and bold headers

#### Method 2: Using Formula
1. Paste HTML in cell **A1**
2. In any cell, use: `=EXTRACT_CRICKET_STATS(A1)`
3. The formula will return the stats array

### Google Sheets Features
- ✅ Custom menu integration
- ✅ Formula-based extraction
- ✅ Auto-formatting and borders
- ✅ Shareable with others
- ✅ Works on mobile devices
- ✅ Cloud-based storage

---

## 📋 Output Format (Both Solutions)

| Column D (Stat) | Column E (Value) |
|-----------------|------------------|
| Highest Individual Score | Player Name (123) – Team Name |
| Top Batter – Team A | Player Name (95) |
| Top Batter – Team B | Player Name (87) |
| Total Match Fours | Team A 45 : 38 Team B |
| Most Match Sixes | Team A 12 : 8 Team B |
| Most Run Outs (by bowling side) | Team B 3 : 1 Team A |

## 🔍 Step-by-Step Workflow

### Getting ESPN HTML
1. Go to ESPN cricket scorecard (e.g., match summary page)
2. Press `Ctrl+U` to view page source
3. Press `Ctrl+A` to select all
4. Press `Ctrl+C` to copy

### Processing in Excel/Google Sheets
1. Open your Cricket Stats workbook/sheet
2. Click cell **A1**
3. Press `Ctrl+V` to paste HTML
4. Run the extraction (button/menu/formula)
5. View results in columns D-E

### Multiple Matches
- For multiple matches, use different rows
- Paste Match 1 HTML in A1, extract to D1:E7
- Paste Match 2 HTML in A10, extract to D10:E16
- And so on...

## 🛠️ Troubleshooting

### Excel Issues
**"Object doesn't support this property or method"**
- Enable macros: File → Options → Trust Center → Macro Settings
- Save as .xlsm file

**"Permission denied"**
- Run Excel as administrator
- Check antivirus settings

### Google Sheets Issues
**"You don't have permission to run this script"**
- Run the script once to authorize
- Accept all permissions when prompted

**"Script function not found"**
- Make sure script is saved in Apps Script editor
- Check function names match exactly

**Formula not working**
- Ensure you're using `=EXTRACT_CRICKET_STATS(A1)`
- Check that A1 contains the HTML content

## 📱 Mobile Usage

### Excel Mobile
- Use Excel mobile app
- VBA macros may not work on mobile
- Consider using Office 365 online version

### Google Sheets Mobile
- Works perfectly on mobile
- Use the menu option: "🏏 Cricket Stats" → "Extract Stats"
- Can copy HTML from mobile browser

## 🔒 Security & Privacy

### Excel
- All processing happens locally
- No data sent to external servers
- HTML content stays on your computer

### Google Sheets
- Processing happens on Google's servers
- HTML content is temporarily processed but not stored
- Standard Google privacy policies apply

## 📊 Advanced Usage

### Excel VBA Customization
```vba
' Modify output location
Range("F1").Value = "Custom Location"

' Add custom stats
Range("D8").Value = "Custom Stat"
Range("E8").Value = "Custom Value"
```

### Google Sheets Customization
```javascript
// Modify output location
sheet.getRange('F1').setValue('Custom Location');

// Add custom formatting
range.setBackgroundColor('#E8F5E8');
```

## 🎯 Use Cases

### Personal Use
- Track favorite team performance
- Compare players across matches
- Build personal cricket database

### Professional Use
- Sports journalism and reporting
- Team analysis and coaching
- Statistical research

### Educational Use
- Teaching data extraction
- Cricket statistics projects
- Sports analytics courses

## 🔄 Version History

### Excel Version
- **v1.0**: Basic HTML parsing and stats extraction
- **v1.1**: Added error handling and formatting
- **v1.2**: Improved team detection and run-out counting

### Google Sheets Version
- **v1.0**: Basic Google Apps Script implementation
- **v1.1**: Added custom menu and formula support
- **v1.2**: Enhanced mobile compatibility

## 📞 Support & Updates

### Common Solutions
1. **HTML not recognized**: Ensure you're copying the full page source
2. **Teams not detected**: Check if ESPN changed their HTML structure
3. **Stats incorrect**: Verify you're using cricket scorecard pages

### Getting Help
- Check the troubleshooting section above
- Ensure you're using the latest ESPN scorecard format
- Test with a known working cricket match page

---

## 🚀 Quick Start Checklist

### Excel Setup
- [ ] Create new Excel workbook (.xlsm)
- [ ] Enable macros
- [ ] Add VBA code
- [ ] Test with sample HTML

### Google Sheets Setup
- [ ] Create new Google Sheet
- [ ] Add Apps Script code
- [ ] Authorize permissions
- [ ] Test with sample HTML

### Usage
- [ ] Get ESPN cricket scorecard HTML
- [ ] Paste in cell A1
- [ ] Run extraction
- [ ] View results in columns D-E

*Now you can extract cricket stats directly in Excel or Google Sheets! 🏏*