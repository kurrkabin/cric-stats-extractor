/**
 * 🏏 Cricket Stats Extractor for Google Sheets
 * Paste ESPN scorecard HTML in cell A1, then run extractCricketStats()
 * Stats will appear in columns D-E
 */

function extractCricketStats() {
  const sheet = SpreadsheetApp.getActiveSheet();
  
  // Clear previous results
  sheet.getRange('D:E').clear();
  
  // Get HTML from cell A1
  const htmlText = sheet.getRange('A1').getValue();
  if (!htmlText) {
    SpreadsheetApp.getUi().alert('Please paste ESPN scorecard HTML in cell A1');
    return;
  }
  
  try {
    // Parse HTML and extract cricket stats
    const stats = parseEspnHtml(htmlText);
    
    // Output results in 2-column format
    const results = [
      ['Stat', 'Value'],
      ['Highest Individual Score', `${stats.highestScorer.name} (${stats.highestScorer.runs}) – ${stats.highestScorer.team}`],
      [`Top Batter – ${stats.teams.team1}`, `${stats.topBatters.team1.name} (${stats.topBatters.team1.runs})`],
      [`Top Batter – ${stats.teams.team2}`, `${stats.topBatters.team2.name} (${stats.topBatters.team2.runs})`],
      ['Total Match Fours', `${stats.teams.team1} ${stats.fours.team1} : ${stats.fours.team2} ${stats.teams.team2}`],
      ['Most Match Sixes', `${stats.teams.team1} ${stats.sixes.team1} : ${stats.sixes.team2} ${stats.teams.team2}`],
      ['Most Run Outs (by bowling side)', `${stats.teams.team2} ${stats.runOuts.team2} : ${stats.runOuts.team1} ${stats.teams.team1}`]
    ];
    
    // Write to sheet
    const range = sheet.getRange(1, 4, results.length, 2);
    range.setValues(results);
    
    // Format the output
    const headerRange = sheet.getRange(1, 4, 1, 2);
    headerRange.setFontWeight('bold');
    
    const dataRange = sheet.getRange(1, 4, results.length, 2);
    dataRange.setBorder(true, true, true, true, true, true);
    
    // Auto-resize columns
    sheet.autoResizeColumn(4);
    sheet.autoResizeColumn(5);
    
    SpreadsheetApp.getUi().alert('Cricket stats extracted successfully!');
    
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error extracting stats: ' + error.toString());
  }
}

function parseEspnHtml(htmlText) {
  // Remove HTML tags and extract text content
  const cleanText = htmlText.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ');
  
  // Extract team names from innings headers
  const inningsPattern = /(\w+(?:\s+\w+)*)\s+Innings/gi;
  const teamMatches = [];
  let match;
  
  while ((match = inningsPattern.exec(htmlText)) !== null) {
    teamMatches.push(match[1].trim());
  }
  
  // Get unique team names
  const uniqueTeams = [...new Set(teamMatches)];
  if (uniqueTeams.length < 2) {
    throw new Error('Could not detect two distinct teams');
  }
  
  const team1 = uniqueTeams[0];
  const team2 = uniqueTeams[1];
  
  // Extract batting data using regex patterns
  const battingData = extractBattingData(htmlText);
  
  // Initialize stat collectors
  const stats = {
    teams: { team1, team2 },
    fours: { team1: 0, team2: 0 },
    sixes: { team1: 0, team2: 0 },
    runOuts: { team1: 0, team2: 0 },
    topBatters: { 
      team1: { name: '', runs: 0 }, 
      team2: { name: '', runs: 0 } 
    },
    highestScorer: { name: '', runs: 0, team: '' }
  };
  
  // Process batting data
  let currentTeamIndex = 0;
  
  for (const player of battingData) {
    const currentTeam = currentTeamIndex % 2 === 0 ? team1 : team2;
    const teamKey = currentTeamIndex % 2 === 0 ? 'team1' : 'team2';
    
    // Add fours and sixes
    stats.fours[teamKey] += player.fours;
    stats.sixes[teamKey] += player.sixes;
    
    // Track top batter for each team
    if (player.runs > stats.topBatters[teamKey].runs) {
      stats.topBatters[teamKey] = { name: player.name, runs: player.runs };
    }
    
    // Track highest overall scorer
    if (player.runs > stats.highestScorer.runs) {
      stats.highestScorer = { name: player.name, runs: player.runs, team: currentTeam };
    }
    
    // Count run outs
    if (player.dismissal && player.dismissal.toLowerCase().includes('run out')) {
      const bowlingTeam = currentTeamIndex % 2 === 0 ? 'team2' : 'team1';
      stats.runOuts[bowlingTeam]++;
    }
    
    // Check if we've moved to next innings
    if (player.isLastOfInnings) {
      currentTeamIndex++;
    }
  }
  
  return stats;
}

function extractBattingData(htmlText) {
  const players = [];
  
  // Extract table rows containing batting data
  const tablePattern = /<table[^>]*ci-scorecard-table[^>]*>(.*?)<\/table>/gis;
  let tableMatch;
  
  while ((tableMatch = tablePattern.exec(htmlText)) !== null) {
    const tableContent = tableMatch[1];
    
    // Extract rows from table
    const rowPattern = /<tr[^>]*>(.*?)<\/tr>/gis;
    let rowMatch;
    
    while ((rowMatch = rowPattern.exec(tableContent)) !== null) {
      const rowContent = rowMatch[1];
      
      // Skip header rows
      if (rowContent.toLowerCase().includes('batter') || rowContent.toLowerCase().includes('batting')) {
        continue;
      }
      
      // Extract cell data
      const cellPattern = /<td[^>]*>(.*?)<\/td>/gis;
      const cells = [];
      let cellMatch;
      
      while ((cellMatch = cellPattern.exec(rowContent)) !== null) {
        const cellText = cellMatch[1].replace(/<[^>]*>/g, '').trim();
        cells.push(cellText);
      }
      
      if (cells.length >= 8) {
        // Extract player data
        const playerName = cells[0].split('†')[0].split('(')[0].trim();
        const runs = parseInt(cells[2]) || 0;
        const fours = parseInt(cells[5]) || 0;
        const sixes = parseInt(cells[6]) || 0;
        const dismissal = cells[1] || '';
        
        if (playerName && runs >= 0) {
          players.push({
            name: playerName,
            runs: runs,
            fours: fours,
            sixes: sixes,
            dismissal: dismissal,
            isLastOfInnings: false
          });
        }
      }
    }
  }
  
  return players;
}

function clearData() {
  const sheet = SpreadsheetApp.getActiveSheet();
  sheet.getRange('A:E').clear();
  SpreadsheetApp.getUi().alert('Data cleared!');
}

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🏏 Cricket Stats')
    .addItem('Extract Stats', 'extractCricketStats')
    .addItem('Clear Data', 'clearData')
    .addToUi();
}

/**
 * Alternative function for cell-based extraction
 * Use this formula in any cell: =EXTRACT_CRICKET_STATS(A1)
 */
function EXTRACT_CRICKET_STATS(htmlCell) {
  if (!htmlCell) {
    return 'Please provide HTML content';
  }
  
  try {
    const stats = parseEspnHtml(htmlCell);
    
    // Return formatted stats as array
    return [
      ['Stat', 'Value'],
      ['Highest Individual Score', `${stats.highestScorer.name} (${stats.highestScorer.runs}) – ${stats.highestScorer.team}`],
      [`Top Batter – ${stats.teams.team1}`, `${stats.topBatters.team1.name} (${stats.topBatters.team1.runs})`],
      [`Top Batter – ${stats.teams.team2}`, `${stats.topBatters.team2.name} (${stats.topBatters.team2.runs})`],
      ['Total Match Fours', `${stats.teams.team1} ${stats.fours.team1} : ${stats.fours.team2} ${stats.teams.team2}`],
      ['Most Match Sixes', `${stats.teams.team1} ${stats.sixes.team1} : ${stats.sixes.team2} ${stats.teams.team2}`],
      ['Most Run Outs (by bowling side)', `${stats.teams.team2} ${stats.runOuts.team2} : ${stats.runOuts.team1} ${stats.teams.team1}`]
    ];
    
  } catch (error) {
    return 'Error: ' + error.toString();
  }
}