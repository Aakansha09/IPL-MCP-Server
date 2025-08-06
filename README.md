# IPL MCP Server 🏏

A Model Context Protocol (MCP) server that provides detailed IPL cricket statistics from ball-by-ball match data. This server allows AI assistants to query comprehensive cricket data including teams, players, matches, ball-by-ball details, and performance statistics.

## Features

- **Team Information**: Get team details with win/loss records
- **Player Information**: Access player stats with batting/bowling performance
- **Match Details**: Query complete match information with scores and innings
- **Ball-by-Ball Data**: Get detailed delivery-wise match commentary
- **Player Performance**: Analyze batting, bowling, and fielding statistics
- **Match Officials**: Access umpire and referee information
- **Venue Information**: Get stadium details with match statistics
- **SQLite Database**: Fast, reliable local data storage
- **MCP Protocol**: Standard Model Context Protocol implementation

## Project Structure

```
ipl-mcp-server/
├── data/                  # Match data files (Cricsheet format)
│   ├── match_1.json      # Ball-by-ball match data
│   ├── match_2.json
│   ├── match_3.json
│   ├── match_4.json
│   └── match_5.json
├── scripts/
│   └── load_data.py      # Data loading script (JSON → SQLite)
├── server/
│   └── app.py           # MCP Server implementation
├── ipl.db               # SQLite database (auto-generated)
├── claude-desktop-config_ipl.json  # Claude Desktop configuration
├── setup_claude.sh      # Claude Desktop setup script
├── CLAUDE_DESKTOP_SETUP.md  # Detailed setup guide
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd ipl-mcp-server
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```

3. **Initialize Database**:
   ```bash
   python scripts/load_data.py
   ```
   This creates the SQLite database and loads the match data.

4. **Run the MCP Server**:
   ```bash
   python server/app.py
   ```

The server will listen for MCP requests on stdin/stdout.

## Claude Desktop Setup

To use this MCP server with Claude Desktop:

### 1. Copy Configuration
Copy the Claude Desktop configuration:
```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude/

# Copy the configuration file
cp claude-desktop-config_ipl.json ~/Library/Application\ Support/Claude/mcp_settings.json
```

### 2. Restart Claude Desktop
- Quit Claude Desktop completely
- Reopen Claude Desktop
- The IPL MCP server should now be available

### 3. Test the Connection
In Claude Desktop, you can now ask cricket questions like:
- "What are the match details for match ID 1473508?"
- "Show me ball-by-ball commentary for the first 5 overs"
- "What was the bowling performance in that match?"
- "Which teams played in these matches?"

### Troubleshooting
If Claude Desktop doesn't see the server:
1. Check that the file is at: `~/Library/Application Support/Claude/mcp_settings.json`
2. Ensure the Python virtual environment path is correct in the config
3. Verify the IPL database exists: `ls -la ipl.db`
4. Test the server manually: `python server/app.py`

## Available Tools

The MCP server provides these tools for cricket data analysis:

### 1. `get_team_info`
Get team information with match statistics.
- **Parameters**: `team_name` (optional) - Filter by team name or short name
- **Returns**: Team details with win/loss records

### 2. `get_player_info`
Get player information with performance statistics.
- **Parameters**: 
  - `player_name` (optional) - Filter by player name
  - `team_name` (optional) - Filter by team
- **Returns**: Player profiles with batting/bowling stats

### 3. `get_match_details`
Get complete match information with scores and innings details.
- **Parameters**: 
  - `match_id` (optional) - Specific match ID
  - `season` (optional) - Filter by season
  - `team_name` (optional) - Filter by team
  - `venue` (optional) - Filter by venue
- **Returns**: Match details with innings scores and results

### 4. `get_ball_by_ball`
Get ball-by-ball commentary and delivery details.
- **Parameters**: 
  - `match_id` (required) - Match ID
  - `innings` (optional) - Innings number (1 or 2)
  - `over_start` (optional) - Starting over number
  - `over_end` (optional) - Ending over number
- **Returns**: Detailed delivery data with runs, wickets, extras

### 5. `get_player_performance`
Get comprehensive player performance statistics.
- **Parameters**: 
  - `player_name` (required) - Player name
  - `match_id` (optional) - Specific match
  - `stat_type` (optional) - 'batting', 'bowling', 'fielding', or 'all'
- **Returns**: Detailed performance metrics

### 6. `get_match_officials`
Get match officials information.
- **Parameters**: 
  - `match_id` (optional) - Match ID
  - `official_name` (optional) - Official name
- **Returns**: Umpires and match officials data

### 7. `get_venue_info`
Get venue information with match statistics.
- **Parameters**: 
  - `venue_name` (optional) - Filter by venue name
  - `city` (optional) - Filter by city
- **Returns**: Venue details with match counts and results

## Usage Examples

### Basic MCP Request Format

**Get team information:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_team_info",
    "arguments": {
      "team_name": "Royal Challengers"
    }
  }
}
```

**Get ball-by-ball data:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_ball_by_ball",
    "arguments": {
      "match_id": "1473508",
      "innings": 1
    }
  }
}
```

**Get player performance:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_player_performance",
    "arguments": {
      "player_name": "Virat Kohli",
      "stat_type": "batting"
    }
  }
}
```

## Database Schema

The SQLite database includes these tables:
- `teams` - Team information and details
- `players` - Player profiles and statistics  
- `matches` - Match metadata and results
- `innings` - Innings-level statistics
- `deliveries` - Ball-by-ball delivery data
- `officials` - Match officials (umpires, referees)
- `venues` - Stadium information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Submit a pull request

---

**Happy Cricket Analytics! 🏏📊**
# IPL-MCP-Server
