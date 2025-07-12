# 🏏 Cricket Match Stats Extractor & Exporter - Enhanced Guide

## Overview
The enhanced Test_Cricket_Matches.ipynb notebook now includes comprehensive export functionality for cricket match statistics. You can extract stats from multiple ESPN cricket scorecard pages and export them to both Excel files and Google Sheets.

## 🆕 New Features

### 1. Multiple Match Support
- **Match Collection**: Add multiple matches to a single collection
- **Match Naming**: Assign custom names to each match or use auto-generated names
- **Persistent Storage**: All matches are stored in memory until you clear them

### 2. Excel Export (.xlsx)
- **Automatic Export**: Creates downloadable Excel files with timestamped names
- **Structured Format**: Maintains the two-column Stat/Value layout
- **Match Column**: Includes match names for easy identification
- **Download Links**: Provides direct download links in the notebook

### 3. Google Sheets Export
- **Live Sharing**: Creates shareable Google Sheets documents
- **Real-time Access**: Multiple users can view the same sheet
- **Formatted Output**: Automatically formats headers and data
- **Public Links**: Generates public viewing links

## 📋 How to Use

### Step 1: Extract Match Stats
1. **Enter Match Name** (optional): Give your match a descriptive name
2. **Paste HTML**: Copy the full HTML from ESPN cricket scorecard (Ctrl+U)
3. **Extract Stats**: Click "Extract Stats" to process the data
4. **Add to Collection**: Click "Add to Collection" to store the match

### Step 2: Export Data
- **Excel Export**: Click "📊 Export to Excel" for downloadable .xlsx files
- **Google Sheets**: Click "📈 Export to Google Sheets" for live sharing
- **Setup Required**: First-time Google Sheets users need to run setup

## 🔧 Google Sheets Setup

### Prerequisites
1. Google Cloud Platform account
2. Project with Google Sheets API enabled
3. Service Account credentials

### Setup Steps
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Download the JSON key file
5. In the notebook, click "🔧 Setup Google Sheets"
6. Paste the JSON content and save

### Service Account Permissions
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
```

## 📊 Export Format

The exported data maintains the two-column layout:

| Match | Stat | Value |
|-------|------|-------|
| Match 1 | Highest Individual Score | Player Name (123) – Team Name |
| Match 1 | Top Batter – Team A | Player Name (95) |
| Match 1 | Top Batter – Team B | Player Name (87) |
| Match 1 | Total Match Fours | Team A 45 : 38 Team B |
| Match 1 | Most Match Sixes | Team A 12 : 8 Team B |
| Match 1 | Most Run Outs (by bowling side) | Team B 3 : 1 Team A |

## 🖼️ Interface Layout

### Input Section
- **Match Name Field**: Optional custom naming
- **HTML Textarea**: Large area for pasting ESPN HTML
- **Action Buttons**: Extract, Add to Collection, Clear All

### Export Section
- **Excel Export**: Direct download functionality
- **Google Sheets**: Live sharing with public links
- **Setup Button**: First-time Google Sheets configuration

### Output Display
- **Match Details**: Shows team names and match info
- **Formatted Stats**: Two-column table with highlighting
- **Collection Counter**: Shows total matches stored

## 🔍 Workflow Examples

### Single Match Export
1. Paste HTML from ESPN scorecard
2. Click "Extract Stats"
3. Click "Add to Collection"
4. Click "📊 Export to Excel"

### Multiple Matches Export
1. First match: Paste HTML → Extract → Add to Collection
2. Second match: Paste HTML → Extract → Add to Collection
3. Repeat for all matches
4. Click "📈 Export to Google Sheets" for live sharing

### Team Analysis
1. Extract stats from multiple matches of the same teams
2. Export to Excel for detailed analysis
3. Use Google Sheets for collaborative review

## 🔧 Technical Details

### Dependencies Added
- `openpyxl`: Excel file creation
- `gspread`: Google Sheets integration
- `oauth2client`: Google authentication
- `google-auth*`: Enhanced Google authentication

### File Structure
```
cricket_matches_stats_YYYYMMDD_HHMMSS.xlsx
google_credentials.json (created after setup)
```

### Data Storage
- In-memory storage during session
- Persistent export files
- Cloud-based Google Sheets

## 🚀 Enhanced Code Implementation

### Key Functions Added:

```python
# Export to Excel
def export_to_excel(filename=None):
    """Export all matches data to Excel file"""
    # Creates timestamped .xlsx files
    # Provides download links

# Google Sheets Setup
def setup_google_sheets():
    """Setup Google Sheets authentication"""
    # Interactive credential setup
    # JSON validation and storage

# Google Sheets Export
def export_to_google_sheets(sheet_name=None):
    """Export all matches data to Google Sheets"""
    # Creates shareable sheets
    # Formats data with headers
    # Generates public links

# Enhanced Match Processing
def extract_stats_to_df(raw_html, match_name=None):
    """Enhanced stats extraction with match naming"""
    # Supports custom match names
    # Returns team information
    # Maintains original functionality
```

### Interface Enhancements:
- **Match Name Input**: Custom naming for each match
- **Collection Management**: Add/clear multiple matches
- **Export Options**: Excel and Google Sheets buttons
- **Setup Integration**: Built-in Google Sheets setup
- **Status Display**: Match count and feedback

## 🎯 Use Cases

### Personal Analysis
- Track favorite team performance across matches
- Compare batting statistics between series
- Create personal cricket statistics database

### Team/Club Analysis
- Analyze team performance trends
- Share statistics with team members
- Create reports for coaching staff

### Media/Journalism
- Quick stat generation for articles
- Shareable data for social media
- Collaborative analysis with colleagues

### Educational/Research
- Cricket statistics for academic projects
- Data analysis learning with real sports data
- Collaborative research with shared datasets

## 📱 Mobile/Tablet Compatibility

The enhanced interface works on mobile devices:
- **Responsive Layout**: Adapts to screen size
- **Touch-Friendly**: Large buttons and input areas
- **Mobile HTML**: Can paste HTML from mobile browsers

## 🔒 Security Notes

### Google Sheets Security
- Service account credentials are stored locally
- Sheets are created with view-only public access
- No sensitive data in credentials (project-specific)

### Data Privacy
- All processing happens locally in your notebook
- No data sent to external servers (except Google Sheets)
- HTML parsing is done client-side

## 🐛 Troubleshooting

### Common Issues:

**Excel Export Not Working**
- Check if openpyxl is installed: `!pip install openpyxl`
- Ensure you have matches in collection

**Google Sheets Authentication Failed**
- Verify JSON credentials are valid
- Check API is enabled in Google Cloud Console
- Ensure service account has necessary permissions

**HTML Parsing Errors**
- Ensure you're copying the full page HTML (Ctrl+U)
- Check if ESPN changed their HTML structure
- Verify you're using cricket scorecard pages

**No Download Links**
- Refresh the notebook cell
- Check file permissions in your environment
- Try running in different notebook environment

## 📈 Future Enhancements

Potential additional features:
- **PDF Export**: Generate formatted PDF reports
- **CSV Export**: Simple CSV for data analysis tools
- **Chart Generation**: Visual statistics with matplotlib
- **Database Integration**: Store in SQLite or PostgreSQL
- **API Integration**: Direct ESPN API access
- **Real-time Updates**: Live match tracking
- **Advanced Analytics**: Player performance trends

## 🤝 Contributing

If you'd like to enhance this tool:
1. Fork the repository
2. Add new features or fix bugs
3. Test with various ESPN cricket pages
4. Submit pull requests with documentation

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review Google Sheets setup steps
- Verify all dependencies are installed
- Test with a simple single match first

---

*Last updated: 2024 - Enhanced Cricket Stats Export Tool*