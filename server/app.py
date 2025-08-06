#!/usr/bin/env python3
"""
IPL MCP Server
A Model Context Protocol server for IPL cricket statistics
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

class IPLMCPServer:
    """IPL Model Context Protocol Server"""
    
    def __init__(self, db_path: str = "ipl.db"):
        self.db_path = Path(__file__).parent.parent / db_path
        self.server_info = {
            "name": "ipl-mcp-server",
            "version": "1.0.0",
            "description": "IPL Cricket Statistics MCP Server"
        }
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dictionaries"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except sqlite3.Error as e:
            print(f"Database error: {e}", file=sys.stderr)
            return []
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools"""
        return [
            {
                "name": "get_team_info",
                "description": "Get information about IPL teams",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_name": {
                            "type": "string",
                            "description": "Name or short name of the team"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_player_info",
                "description": "Get player information and team details",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "player_name": {
                            "type": "string",
                            "description": "Name of the player"
                        },
                        "team_name": {
                            "type": "string",
                            "description": "Filter by team name"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_match_details",
                "description": "Get detailed match information including scores and outcome",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "match_id": {
                            "type": "string",
                            "description": "Specific match ID"
                        },
                        "season": {
                            "type": "integer",
                            "description": "IPL season year"
                        },
                        "team_name": {
                            "type": "string",
                            "description": "Filter by team name"
                        },
                        "venue": {
                            "type": "string",
                            "description": "Filter by venue"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_ball_by_ball",
                "description": "Get ball-by-ball commentary and deliveries for a match",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "match_id": {
                            "type": "string",
                            "description": "Match ID"
                        },
                        "innings": {
                            "type": "integer",
                            "description": "Innings number (1 or 2)"
                        },
                        "over_start": {
                            "type": "integer",
                            "description": "Starting over number"
                        },
                        "over_end": {
                            "type": "integer",
                            "description": "Ending over number"
                        }
                    },
                    "required": ["match_id"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_player_performance",
                "description": "Get player performance in specific match or overall",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "player_name": {
                            "type": "string",
                            "description": "Player name"
                        },
                        "match_id": {
                            "type": "string",
                            "description": "Specific match ID"
                        },
                        "stat_type": {
                            "type": "string",
                            "description": "Type of stats",
                            "enum": ["batting", "bowling", "fielding", "all"],
                            "default": "all"
                        }
                    },
                    "required": ["player_name"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_match_officials",
                "description": "Get match officials information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "match_id": {
                            "type": "string",
                            "description": "Match ID"
                        },
                        "official_name": {
                            "type": "string",
                            "description": "Official name"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_venue_info",
                "description": "Get information about cricket venues",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "venue_name": {
                            "type": "string",
                            "description": "Name of the venue"
                        },
                        "city": {
                            "type": "string",
                            "description": "Filter by city"
                        }
                    },
                    "additionalProperties": False
                }
            }
        ]
    
    async def handle_get_team_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get team information"""
        team_name = arguments.get('team_name')
        
        if team_name:
            query = """
                SELECT t.*, COUNT(CASE WHEN m.winner = t.name THEN 1 END) as wins,
                       COUNT(m.id) as total_matches
                FROM teams t
                LEFT JOIN matches m ON (m.team1 = t.name OR m.team2 = t.name)
                WHERE t.name LIKE ? OR t.short_name LIKE ?
                GROUP BY t.id
            """
            results = self.execute_query(query, (f"%{team_name}%", f"%{team_name}%"))
        else:
            query = """
                SELECT t.*, COUNT(CASE WHEN m.winner = t.name THEN 1 END) as wins,
                       COUNT(m.id) as total_matches
                FROM teams t
                LEFT JOIN matches m ON (m.team1 = t.name OR m.team2 = t.name)
                GROUP BY t.id
                ORDER BY t.name
            """
            results = self.execute_query(query)
        
        return {
            "teams": results,
            "total_teams": len(results)
        }
    
    async def handle_get_player_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get player information"""
        player_name = arguments.get('player_name')
        team_name = arguments.get('team_name')
        
        conditions = []
        params = []
        
        if player_name:
            conditions.append("p.name LIKE ?")
            params.append(f"%{player_name}%")
        
        if team_name:
            conditions.append("p.team LIKE ?")
            params.append(f"%{team_name}%")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT p.*, 
                   COUNT(d.id) as total_deliveries,
                   SUM(d.runs_batter) as total_runs,
                   AVG(d.runs_batter) as avg_runs_per_delivery,
                   COUNT(CASE WHEN d.runs_batter >= 4 THEN 1 END) as boundaries
            FROM players p
            LEFT JOIN deliveries d ON d.batter = p.name OR d.bowler = p.name
            {where_clause}
            GROUP BY p.id
            ORDER BY total_runs DESC NULLS LAST, p.name
        """
        
        results = self.execute_query(query, tuple(params))
        
        return {
            "players": results,
            "total_players": len(results)
        }
    
    async def handle_get_match_details(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get match details"""
        match_id = arguments.get('match_id')
        season = arguments.get('season')
        team_name = arguments.get('team_name')
        venue = arguments.get('venue')
        
        conditions = []
        params = []
        
        if match_id:
            conditions.append("m.id = ?")
            params.append(match_id)
        
        if season:
            conditions.append("m.season = ?")
            params.append(season)
        
        if team_name:
            conditions.append("(m.team1 LIKE ? OR m.team2 LIKE ?)")
            params.extend([f"%{team_name}%", f"%{team_name}%"])
        
        if venue:
            conditions.append("m.venue LIKE ?")
            params.append(f"%{venue}%")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT m.*, 
                   i1.total_runs as team1_runs,
                   i1.total_wickets as team1_wickets,
                   i1.total_overs as team1_overs,
                   i2.total_runs as team2_runs,
                   i2.total_wickets as team2_wickets,
                   i2.total_overs as team2_overs,
                   COUNT(o.id) as total_officials
            FROM matches m
            LEFT JOIN innings i1 ON i1.match_id = m.id AND i1.innings_number = 1
            LEFT JOIN innings i2 ON i2.match_id = m.id AND i2.innings_number = 2
            LEFT JOIN officials o ON o.match_id = m.id
            {where_clause}
            GROUP BY m.id
            ORDER BY m.date DESC
        """
        
        results = self.execute_query(query, tuple(params))
        
        return {
            "matches": results,
            "total_matches": len(results)
        }
    
    async def handle_get_ball_by_ball(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get ball by ball details"""
        match_id = arguments.get('match_id')
        innings = arguments.get('innings')
        over_start = arguments.get('over_start')
        over_end = arguments.get('over_end')
        
        conditions = ["d.match_id = ?"]
        params = [match_id]
        
        if innings:
            conditions.append("d.innings = ?")
            params.append(innings)
        
        if over_start is not None:
            conditions.append("d.over >= ?")
            params.append(over_start)
        
        if over_end is not None:
            conditions.append("d.over <= ?")
            params.append(over_end)
        
        where_clause = "WHERE " + " AND ".join(conditions)
        
        query = f"""
            SELECT d.*, m.team1, m.team2
            FROM deliveries d
            JOIN matches m ON m.id = d.match_id
            {where_clause}
            ORDER BY d.innings, d.over, d.ball
        """
        
        results = self.execute_query(query, tuple(params))
        
        # Get match summary
        match_query = "SELECT * FROM matches WHERE id = ?"
        match_info = self.execute_query(match_query, (match_id,))
        
        return {
            "match_info": match_info[0] if match_info else None,
            "deliveries": results,
            "total_deliveries": len(results),
            "overs_covered": len(set((r['innings'], r['over']) for r in results))
        }
    
    async def handle_get_player_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get player performance"""
        player_name = arguments.get('player_name')
        match_id = arguments.get('match_id')
        stat_type = arguments.get('stat_type', 'all')
        
        performance = {}
        
        # Batting stats
        if stat_type in ['batting', 'all']:
            batting_conditions = ["d.batter LIKE ?"]
            batting_params = [f"%{player_name}%"]
            
            if match_id:
                batting_conditions.append("d.match_id = ?")
                batting_params.append(match_id)
            
            batting_where = "WHERE " + " AND ".join(batting_conditions)
            
            batting_query = f"""
                SELECT 
                    COUNT(d.id) as balls_faced,
                    SUM(d.runs_batter) as runs_scored,
                    COUNT(CASE WHEN d.runs_batter = 4 THEN 1 END) as fours,
                    COUNT(CASE WHEN d.runs_batter = 6 THEN 1 END) as sixes,
                    COUNT(CASE WHEN d.runs_batter >= 4 THEN 1 END) as boundaries,
                    ROUND(CAST(SUM(d.runs_batter) AS FLOAT) / COUNT(d.id) * 100, 2) as strike_rate,
                    COUNT(DISTINCT d.match_id) as matches_played
                FROM deliveries d
                {batting_where}
            """
            
            batting_results = self.execute_query(batting_query, tuple(batting_params))
            performance['batting'] = batting_results[0] if batting_results else {}
        
        # Bowling stats
        if stat_type in ['bowling', 'all']:
            bowling_conditions = ["d.bowler LIKE ?"]
            bowling_params = [f"%{player_name}%"]
            
            if match_id:
                bowling_conditions.append("d.match_id = ?")
                bowling_params.append(match_id)
            
            bowling_where = "WHERE " + " AND ".join(bowling_conditions)
            
            bowling_query = f"""
                SELECT 
                    COUNT(d.id) as balls_bowled,
                    SUM(d.runs_total) as runs_conceded,
                    COUNT(CASE WHEN d.wicket_type IS NOT NULL AND d.wicket_type != '' THEN 1 END) as wickets,
                    ROUND(CAST(SUM(d.runs_total) AS FLOAT) / COUNT(d.id) * 6, 2) as economy_rate,
                    COUNT(DISTINCT d.match_id) as matches_bowled
                FROM deliveries d
                {bowling_where}
            """
            
            bowling_results = self.execute_query(bowling_query, tuple(bowling_params))
            performance['bowling'] = bowling_results[0] if bowling_results else {}
        
        return {
            "player_name": player_name,
            "match_id": match_id,
            "stat_type": stat_type,
            "performance": performance
        }
    
    async def handle_get_match_officials(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get match officials"""
        match_id = arguments.get('match_id')
        official_name = arguments.get('official_name')
        
        conditions = []
        params = []
        
        if match_id:
            conditions.append("o.match_id = ?")
            params.append(match_id)
        
        if official_name:
            conditions.append("o.name LIKE ?")
            params.append(f"%{official_name}%")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT o.*, m.date, m.venue, m.team1, m.team2
            FROM officials o
            LEFT JOIN matches m ON m.id = o.match_id
            {where_clause}
            ORDER BY m.date DESC, o.role, o.name
        """
        
        results = self.execute_query(query, tuple(params))
        
        return {
            "officials": results,
            "total_officials": len(results)
        }
    
    async def handle_get_venue_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get venue information"""
        venue_name = arguments.get('venue_name')
        city = arguments.get('city')
        
        conditions = []
        params = []
        
        if venue_name:
            conditions.append("m.venue LIKE ?")
            params.append(f"%{venue_name}%")
        
        if city:
            conditions.append("m.venue LIKE ?")
            params.append(f"%{city}%")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                m.venue,
                COUNT(m.id) as total_matches,
                COUNT(CASE WHEN m.winner = m.team1 THEN 1 END) as team1_wins,
                COUNT(CASE WHEN m.winner = m.team2 THEN 1 END) as team2_wins,
                GROUP_CONCAT(DISTINCT m.winner) as teams_won,
                MIN(m.date) as first_match_date,
                MAX(m.date) as last_match_date
            FROM matches m
            {where_clause}
            GROUP BY m.venue
            ORDER BY total_matches DESC, m.venue
        """
        
        results = self.execute_query(query, tuple(params))
        
        return {
            "venues": results,
            "total_venues": len(results)
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        method = request.get("method")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": self.server_info
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": self.get_tools()
                }
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            handlers = {
                "get_team_info": self.handle_get_team_info,
                "get_player_info": self.handle_get_player_info,
                "get_match_details": self.handle_get_match_details,
                "get_ball_by_ball": self.handle_get_ball_by_ball,
                "get_player_performance": self.handle_get_player_performance,
                "get_match_officials": self.handle_get_match_officials,
                "get_venue_info": self.handle_get_venue_info
            }
            
            if name in handlers:
                try:
                    result = await handlers[name](arguments)
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {name}"
                    }
                }
        
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "resources": []
                }
            }
        
        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "prompts": []
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }

async def main():
    """Main entry point"""
    server = IPLMCPServer()
    
    while True:
        try:
            line = input()
            if not line:
                break
                
            request = json.loads(line)
            response = await server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
            
        except EOFError:
            break
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
