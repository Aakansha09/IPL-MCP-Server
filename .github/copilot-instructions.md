<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# IPL MCP Server - Copilot Instructions

This is an IPL (Indian Premier League) cricket statistics MCP (Model Context Protocol) server project. 

## Project Context

- **Purpose**: Provide cricket statistics and data through MCP protocol
- **Database**: SQLite with IPL teams, players, matches, venues, and standings data
- **Protocol**: Model Context Protocol (MCP) for AI assistant integration
- **Language**: Python 3.9+ with standard library modules

## Key Components

1. **Data Layer**: JSON files in `data/` directory with cricket statistics
2. **Database**: SQLite database created from JSON data via `scripts/load_data.py`
3. **MCP Server**: `server/app.py` implements the MCP protocol with cricket data tools
4. **Tools**: 5 main tools for querying teams, players, matches, venues, and standings

## Development Guidelines

- Use Python standard library when possible (sqlite3, json, asyncio)
- Follow MCP protocol specifications for request/response format
- Include proper error handling for database operations
- Use cricket domain terminology (runs, wickets, overs, strike rate, etc.)
- Maintain data relationships between teams, players, and matches

## Data Schema

- Teams: Basic info, titles, home venues, colors
- Players: Stats including runs, average, strike rate, centuries
- Matches: Results with scores, venues, winners, player of match
- Venues: Stadium details, capacity, pitch characteristics
- Standings: Season points table with wins/losses/points

## MCP Tools Available

1. `get_team_info` - Team information and history
2. `get_player_stats` - Player statistics and performance
3. `get_match_results` - Match results and details
4. `get_standings` - Season standings and points table
5. `get_venue_info` - Stadium and venue information

You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
