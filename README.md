# 🏏 Cricket Match Stats Extractor & Exporter

Enhanced cricket statistics extraction tool for ESPN scorecard data with Excel and Google Sheets export functionality.

## ✨ Features

- **Extract cricket match stats** from ESPN scorecard HTML
- **Multiple match support** - collect stats from multiple matches
- **Excel export** - downloadable .xlsx files with timestamped names
- **Google Sheets export** - shareable live documents with public links
- **Two-column format** - maintains Stat/Value layout as requested
- **Enhanced UI** - improved interface with match naming and collection management

## 📋 Quick Start

### Option 1: Use the Enhanced Script (Recommended)
```python
# In a Jupyter notebook cell:
exec(open('cricket_stats_enhanced.py').read())
```

### Option 2: Run the Original Notebook
Open `Test_Cricket_Matches.ipynb` in Jupyter and run all cells.

### Option 3: Manual Installation
```bash
pip install pandas beautifulsoup4 ipywidgets openpyxl gspread oauth2client google-auth google-auth-oauthlib google-auth-httplib2
```

## 🎯 How to Use

1. **Extract Stats**: Paste ESPN cricket scorecard HTML and click "Extract Stats"
2. **Add to Collection**: Click "Add to Collection" to store the match
3. **Repeat**: Add multiple matches to the same collection
4. **Export**: Choose Excel or Google Sheets export

## 📊 Export Options

### Excel Export
- Creates timestamped `.xlsx` files
- Direct download links in notebook
- Three-column format: Match | Stat | Value

### Google Sheets Export
- Creates shareable live documents
- Public viewing links
- Real-time collaboration
- Requires Google Cloud setup (see guide)

## 📖 Documentation

- **[Complete Guide](CRICKET_STATS_EXPORT_GUIDE.md)** - Detailed instructions and setup
- **[Enhanced Script](cricket_stats_enhanced.py)** - Full Python implementation
- **[Original Notebook](Test_Cricket_Matches.ipynb)** - Jupyter notebook version

## 🔧 Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Google Sheets API
3. Create Service Account and download JSON key
4. Use "Setup Google Sheets" button in the interface

## 📁 Files

- `cricket_stats_enhanced.py` - Enhanced Python script with export functionality
- `Test_Cricket_Matches.ipynb` - Original Jupyter notebook
- `CRICKET_STATS_EXPORT_GUIDE.md` - Complete documentation
- `requirements.txt` - Python dependencies

## 🚀 Example Output

```
Match                  | Stat                     | Value
--------------------- | ------------------------ | --------------------------------
India vs Australia   | Highest Individual Score | Kohli (95) – India
India vs Australia   | Top Batter – India       | Kohli (95)
India vs Australia   | Top Batter – Australia   | Smith (87)
India vs Australia   | Total Match Fours        | India 45 : 38 Australia
India vs Australia   | Most Match Sixes         | India 12 : 8 Australia
```

## 📞 Support

For issues or questions, see the [troubleshooting section](CRICKET_STATS_EXPORT_GUIDE.md#troubleshooting) in the complete guide.

---

*Enhanced version with Excel and Google Sheets export functionality*
