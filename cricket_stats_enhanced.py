"""
🏏 Cricket Match Stats Extractor & Exporter - Enhanced Version
============================================================

This enhanced version includes:
- Multiple match support
- Excel export (.xlsx) with download links
- Google Sheets export with live sharing
- Enhanced UI with match naming and collection management

Usage:
1. Run this script in a Jupyter notebook
2. Follow the interface prompts
3. Export to Excel or Google Sheets
"""

# 📦 Install dependencies
import subprocess
import sys

def install_packages():
    """Install required packages"""
    packages = [
        'pandas', 'beautifulsoup4', 'ipywidgets', 'openpyxl', 
        'gspread', 'oauth2client', 'google-auth', 
        'google-auth-oauthlib', 'google-auth-httplib2'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
        except subprocess.CalledProcessError:
            print(f"Warning: Could not install {package}")

# Install packages
install_packages()

# 🔄 Imports
from bs4 import BeautifulSoup
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML, FileLink
import json
import os
from datetime import datetime
import re

# Optional Google Sheets imports (will handle gracefully if not available)
try:
    import gspread
    from google.oauth2.service_account import Credentials
    from google.auth.exceptions import RefreshError
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("⚠️ Google Sheets functionality not available. Install gspread and google-auth packages.")

# 📊 Global storage for multiple matches
all_matches_data = []

# 🏏 Enhanced Stats Extractor Function
def extract_stats_to_df(raw_html, match_name=None):
    """
    Extract cricket match statistics from ESPN HTML
    
    Args:
        raw_html (str): Full HTML from ESPN cricket scorecard
        match_name (str): Optional custom match name
    
    Returns:
        tuple: (DataFrame, team_1, team_2)
    """
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Extract innings headers and map team order
    innings_headers = soup.select('span.ds-text-title-xs.ds-font-bold.ds-capitalize')
    all_teams = [h.get_text(strip=True).replace(' Innings', '') for h in innings_headers]
    unique_teams = list(dict.fromkeys(all_teams))  # preserve order, remove duplicates

    if len(unique_teams) < 2:
        raise ValueError("❌ Could not detect two distinct teams.")

    team_1, team_2 = unique_teams[:2]

    # Initialise stat collectors
    top_scores = {}
    sixes = {team_1: 0, team_2: 0}
    fours = {team_1: 0, team_2: 0}
    run_outs = {team_1: 0, team_2: 0}
    top_batters = {team_1: ('', 0), team_2: ('', 0)}

    # Get all batting tables (one per innings)
    batting_tables = soup.find_all('table', class_='ci-scorecard-table')

    for i, table in enumerate(batting_tables):
        rows = table.find_all('tr')[1:]
        current_team = all_teams[i] if i < len(all_teams) else None
        if current_team not in (team_1, team_2):
            continue

        bowled_by = team_2 if current_team == team_1 else team_1

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 8:
                continue
            name = cols[0].get_text(strip=True).split('†')[0].split('(')[0].strip()

            try:
                runs = int(cols[2].get_text(strip=True))
                _4s = int(cols[5].get_text(strip=True))
                _6s = int(cols[6].get_text(strip=True))
            except ValueError:
                continue

            fours[current_team] += _4s
            sixes[current_team] += _6s

            # track highest individual
            if name not in top_scores or runs > top_scores[name]:
                top_scores[name] = runs

            # track top batter per innings
            if runs > top_batters[current_team][1]:
                top_batters[current_team] = (name, runs)

        # Count run outs (credited to the bowling side)
        for row in rows:
            text = ' '.join(td.get_text(strip=True) for td in row.find_all('td'))
            if 'run out' in text.lower():
                run_outs[bowled_by] += 1

    # Identify overall highest scorer
    if not top_scores:
        raise ValueError("❌ Could not extract any batting statistics.")
    
    top_name_all, top_runs_all = max(top_scores.items(), key=lambda x: x[1])
    top_team_all = team_1 if top_name_all in [top_batters[team_1][0]] else team_2

    # Build results DataFrame
    df = pd.DataFrame({
        'Stat': [
            'Highest Individual Score',
            f'Top Batter – {team_1}',
            f'Top Batter – {team_2}',
            'Total Match Fours',
            'Most Match Sixes',
            'Most Run Outs (by bowling side)'
        ],
        'Value': [
            f"{top_name_all} ({top_runs_all}) – {top_team_all}",
            f"{top_batters[team_1][0]} ({top_batters[team_1][1]})",
            f"{top_batters[team_2][0]} ({top_batters[team_2][1]})",
            f"{team_1} {fours[team_1]} : {fours[team_2]} {team_2}",
            f"{team_1} {sixes[team_1]} : {sixes[team_2]} {team_2}",
            f"{team_2} {run_outs[team_2]} : {run_outs[team_1]} {team_1}"
        ]
    })

    # Add match name column if provided
    if match_name:
        df['Match'] = match_name

    return df, team_1, team_2

# 📊 Export Functions
def export_to_excel(filename=None):
    """Export all matches data to Excel file"""
    if not all_matches_data:
        print("❌ No match data available to export!")
        return
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cricket_matches_stats_{timestamp}.xlsx"
    
    try:
        # Create combined DataFrame
        combined_df = pd.concat(all_matches_data, ignore_index=True)
        
        # Reorder columns if 'Match' exists
        if 'Match' in combined_df.columns:
            combined_df = combined_df[['Match', 'Stat', 'Value']]
        
        # Save to Excel
        combined_df.to_excel(filename, index=False, engine='openpyxl')
        print(f"✅ Excel file saved as: {filename}")
        print(f"📁 File location: {os.path.abspath(filename)}")
        
        # Create downloadable link
        try:
            display(FileLink(filename))
        except:
            print(f"📥 Download: {filename}")
        
        # Show preview
        print("\n📊 Export Preview:")
        print(combined_df.head(10).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error exporting to Excel: {e}")

def setup_google_sheets():
    """Setup Google Sheets authentication"""
    if not GOOGLE_SHEETS_AVAILABLE:
        print("❌ Google Sheets functionality not available.")
        print("Please install: pip install gspread google-auth google-auth-oauthlib")
        return
    
    print("🔧 Setting up Google Sheets access...")
    print("📋 Instructions:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Google Sheets API and Google Drive API")
    print("4. Create a Service Account and download the JSON key")
    print("5. Paste the JSON content in the text area below")
    
    json_input = widgets.Textarea(
        value='',
        placeholder='Paste your Google Service Account JSON key here...',
        layout=widgets.Layout(width='100%', height='200px')
    )
    
    save_button = widgets.Button(description='Save Credentials', button_style='success')
    
    def save_credentials(b):
        try:
            credentials_json = json_input.value.strip()
            if not credentials_json:
                print("❌ Please paste the JSON credentials first.")
                return
            
            # Parse and save credentials
            creds_dict = json.loads(credentials_json)
            with open('google_credentials.json', 'w') as f:
                json.dump(creds_dict, f)
            
            print("✅ Credentials saved successfully!")
            print("🔄 You can now use the 'Export to Google Sheets' button.")
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON format. Please check your credentials.")
        except Exception as e:
            print(f"❌ Error saving credentials: {e}")
    
    save_button.on_click(save_credentials)
    display(json_input, save_button)

def export_to_google_sheets(sheet_name=None):
    """Export all matches data to Google Sheets"""
    if not GOOGLE_SHEETS_AVAILABLE:
        print("❌ Google Sheets functionality not available.")
        return
    
    if not all_matches_data:
        print("❌ No match data available to export!")
        return
    
    if sheet_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_name = f"Cricket_Matches_Stats_{timestamp}"
    
    try:
        # Check if credentials file exists
        if not os.path.exists('google_credentials.json'):
            print("❌ Google credentials not found!")
            print("📋 Please run the setup first:")
            setup_google_sheets()
            return
        
        # Set up Google Sheets client
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 
                  'https://www.googleapis.com/auth/drive']
        
        creds = Credentials.from_service_account_file('google_credentials.json', scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Create new spreadsheet
        spreadsheet = client.create(sheet_name)
        worksheet = spreadsheet.sheet1
        
        # Prepare data
        combined_df = pd.concat(all_matches_data, ignore_index=True)
        
        # Reorder columns if 'Match' exists
        if 'Match' in combined_df.columns:
            combined_df = combined_df[['Match', 'Stat', 'Value']]
        
        # Convert to list of lists for Google Sheets
        data = [combined_df.columns.tolist()] + combined_df.values.tolist()
        
        # Upload data
        worksheet.update('A1', data)
        
        # Format the spreadsheet
        worksheet.format('A1:Z1', {'textFormat': {'bold': True}})
        
        # Share the spreadsheet (make it viewable by anyone with link)
        spreadsheet.share(None, perm_type='anyone', role='reader')
        
        print(f"✅ Google Sheets created successfully!")
        print(f"📊 Sheet name: {sheet_name}")
        print(f"🔗 Share link: {spreadsheet.url}")
        
        # Display clickable link
        display(HTML(f'<a href="{spreadsheet.url}" target="_blank">📊 Open Google Sheets</a>'))
        
    except Exception as e:
        print(f"❌ Error exporting to Google Sheets: {e}")
        if "credentials" in str(e).lower():
            print("📋 Please check your Google credentials setup.")

# 🎨 Formatting Functions
def bold_team(value, metric):
    """Apply bold formatting to winning team in comparative stats"""
    if metric in ["Total Match Fours", "Most Match Sixes"]:
        match = re.match(r"(.+?) (\d+) : (\d+) (.+)", value)
        if match:
            team1, score1, score2, team2 = match.groups()
            score1, score2 = int(score1), int(score2)
            if score1 > score2:
                team1 = f"<b>{team1.strip()}</b>"
                return f"{team1} {score1} : {score2} {team2.strip()}"
            elif score2 > score1:
                team2 = f"<b>{team2.strip()}</b>"
                return f"{team1.strip()} {score1} : {score2} {team2}"
            else:
                return f"{team1.strip()} {score1} : {score2} {team2.strip()}"
    return value

# 🖼️ Enhanced Interface
def create_interface():
    """Create the enhanced user interface"""
    
    # Input widgets
    html_input = widgets.Textarea(
        value='',
        placeholder='Paste full Ctrl+U HTML here…',
        layout=widgets.Layout(width='100%', height='300px')
    )

    match_name_input = widgets.Text(
        value='',
        placeholder='Enter match name (optional)',
        description='Match Name:',
        layout=widgets.Layout(width='50%')
    )

    # Action buttons
    extract_button = widgets.Button(description='Extract Stats', button_style='primary')
    add_match_button = widgets.Button(description='Add to Collection', button_style='info')
    clear_button = widgets.Button(description='Clear All', button_style='warning')

    # Export buttons
    export_excel_button = widgets.Button(description='📊 Export to Excel', button_style='success')
    export_sheets_button = widgets.Button(description='📈 Export to Google Sheets', button_style='success')
    setup_sheets_button = widgets.Button(description='🔧 Setup Google Sheets', button_style='default')

    # Output areas
    output = widgets.Output()
    status_output = widgets.Output()
    
    # Global variable to store current match
    current_match_df = None

    def on_extract_click(b):
        nonlocal current_match_df
        with output:
            clear_output()
            raw_html = html_input.value.strip()
            if not raw_html:
                print("❗ Please paste the full HTML first.")
                return
            try:
                match_name = match_name_input.value.strip() or f"Match {len(all_matches_data) + 1}"
                current_match_df, team_1, team_2 = extract_stats_to_df(raw_html, match_name)
                
                # Create display copy with formatting
                display_df = current_match_df.copy()
                if 'Match' in display_df.columns:
                    display_df = display_df[['Stat', 'Value']]  # Hide Match column for display
                
                display_df["Value"] = display_df.apply(lambda row: bold_team(row["Value"], row["Stat"]), axis=1)
                
                print(f"🏏 Match: {match_name}")
                print(f"⚔️ Teams: {team_1} vs {team_2}")
                print("\n📊 Extracted Stats:")
                display(HTML(display_df.to_html(index=False, escape=False)))
                
                # Update status
                with status_output:
                    clear_output()
                    print(f"✅ Stats extracted! Ready to add to collection.")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                with status_output:
                    clear_output()
                    print(f"❌ Extraction failed: {e}")

    def on_add_match_click(b):
        nonlocal current_match_df
        with output:
            if current_match_df is None:
                print("❌ No match data extracted yet! Please extract stats first.")
                return
            
            all_matches_data.append(current_match_df)
            match_name = current_match_df['Match'].iloc[0] if 'Match' in current_match_df.columns else f"Match {len(all_matches_data)}"
            print(f"✅ '{match_name}' added to collection!")
            print(f"📊 Total matches in collection: {len(all_matches_data)}")
            
            # Clear inputs for next match
            html_input.value = ''
            match_name_input.value = ''
            current_match_df = None
            
            # Update status
            with status_output:
                clear_output()
                print(f"📊 Collection: {len(all_matches_data)} matches | Ready for next match or export")

    def on_clear_click(b):
        nonlocal current_match_df
        with output:
            clear_output()
            all_matches_data.clear()
            current_match_df = None
            html_input.value = ''
            match_name_input.value = ''
            print("🗑️ All match data cleared!")
            
            with status_output:
                clear_output()
                print("🗑️ Collection cleared")

    def on_export_excel_click(b):
        with output:
            clear_output()
            export_to_excel()

    def on_export_sheets_click(b):
        with output:
            clear_output()
            export_to_google_sheets()

    def on_setup_sheets_click(b):
        with output:
            clear_output()
            setup_google_sheets()

    # Wire up button events
    extract_button.on_click(on_extract_click)
    add_match_button.on_click(on_add_match_click)
    clear_button.on_click(on_clear_click)
    export_excel_button.on_click(on_export_excel_click)
    export_sheets_button.on_click(on_export_sheets_click)
    setup_sheets_button.on_click(on_setup_sheets_click)

    # Display interface
    display(widgets.HTML("<h2>🏏 Cricket Match Stats Extractor & Exporter</h2>"))
    display(widgets.HTML("<p><em>Enhanced version with Excel and Google Sheets export</em></p>"))
    
    display(widgets.HTML("<h3>📋 Step 1: Extract Match Stats</h3>"))
    display(match_name_input)
    display(widgets.HTML("<p>Paste ESPNcricinfo Scorecard HTML below:</p>"))
    display(html_input)
    display(widgets.HBox([extract_button, add_match_button, clear_button]))

    display(widgets.HTML("<h3>📊 Step 2: Export Data</h3>"))
    display(widgets.HBox([export_excel_button, export_sheets_button, setup_sheets_button]))

    display(widgets.HTML("<h3>📋 Status</h3>"))
    display(status_output)
    
    display(widgets.HTML("<h3>📊 Output</h3>"))
    display(output)
    
    # Initial status
    with status_output:
        print(f"📊 Collection: {len(all_matches_data)} matches | Ready to extract stats")

# 🚀 Main execution
if __name__ == "__main__":
    print("🏏 Cricket Stats Extractor & Exporter - Enhanced Version")
    print("=" * 60)
    print("Starting interface...")
    create_interface()