# Claude Desktop Setup Guide for IPL MCP Server

## Quick Setup Instructions

### Step 1: Copy Configuration File
Copy the configuration to Claude Desktop's MCP settings directory:

```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude/

# Copy the configuration file
cp claude-desktop-config.json ~/Library/Application\ Support/Claude/mcp_settings.json
```

### Step 2: Restart Claude Desktop
- Quit Claude Desktop completely
- Reopen Claude Desktop
- The IPL MCP server should now be available

### Step 3: Test the Connection
In Claude Desktop, you can now ask questions like:

**Example Questions:**
- "What are the match details for match ID 1473508?"
- "Show me ball-by-ball commentary for the first 5 overs of match 1473508"
- "What was Suyash Sharma's bowling performance in match 1473508?"
- "Which teams played in the 2025 IPL season?"
- "Show me player information for Royal Challengers Bengaluru players"

## Available MCP Tools

Claude Desktop will have access to these 7 tools:

1. **get_team_info** - IPL team information
2. **get_player_info** - Player profiles and team details  
3. **get_match_details** - Complete match information with scores
4. **get_ball_by_ball** - Detailed ball-by-ball commentary
5. **get_player_performance** - Batting, bowling, fielding statistics
6. **get_match_officials** - Match officials and umpire information
7. **get_venue_info** - Cricket venue information

## Troubleshooting

### If Claude Desktop doesn't see the server:
1. Check that the file is at: `~/Library/Application Support/Claude/mcp_settings.json`
2. Ensure the Python virtual environment path is correct
3. Verify the IPL database exists: `ls -la ipl.db`
4. Test the server manually: `python server/app.py`

### If you get permission errors:
```bash
chmod +x server/app.py
chmod +x scripts/process_cricsheet_data.py
```

### To check server logs:
The server outputs logs to stderr, which Claude Desktop should show in its developer tools.

## Configuration File Location

The configuration file should be placed at:
```
~/Library/Application Support/Claude/mcp_settings.json
```

Content:
```json
{
  "mcpServers": {
    "ipl-mcp-server": {
      "command": "/Users/aakanshasrivastava/ipl-mcp-server/.venv/bin/python",
      "args": ["/Users/aakanshasrivastava/ipl-mcp-server/server/app.py"],
      "env": {}
    }
  }
}
```

## Example Claude Desktop Queries

Once connected, you can ask Claude Desktop:

- **"What happened in the IPL Qualifier 1 match?"**
  - Claude will use `get_match_details` to show the Punjab Kings vs RCB match

- **"Show me the first over of that match"**
  - Claude will use `get_ball_by_ball` with over_start=0, over_end=0

- **"How did Suyash Sharma perform as a bowler?"**
  - Claude will use `get_player_performance` with bowling stats

- **"Which venues have hosted IPL matches?"**
  - Claude will use `get_venue_info` to list all stadiums

The server provides rich, detailed cricket data that Claude Desktop can analyze and present in natural language!
