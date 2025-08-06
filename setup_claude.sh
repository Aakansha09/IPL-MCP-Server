#!/bin/bash

# Claude Desktop Setup Script for IPL MCP Server
# This script helps set up the IPL MCP Server for Claude Desktop

echo "🏏 IPL MCP Server - Claude Desktop Setup"
echo "======================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if database exists
if [ ! -f "ipl.db" ]; then
    echo "❌ Database not found!"
    echo "Please run: source .venv/bin/activate && python scripts/process_cricsheet_data.py"
    exit 1
fi

# Test the MCP server
echo "🧪 Testing MCP Server..."
cd "$(dirname "$0")"

# Test initialize
echo "Testing initialize..."
INIT_RESPONSE=$(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test"}}}' | .venv/bin/python server/app.py)

if echo "$INIT_RESPONSE" | grep -q '"result"'; then
    echo "✅ Initialize test passed"
else
    echo "❌ Initialize test failed"
    echo "Response: $INIT_RESPONSE"
    exit 1
fi

# Test tools/list
echo "Testing tools/list..."
TOOLS_RESPONSE=$(echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | .venv/bin/python server/app.py)

if echo "$TOOLS_RESPONSE" | grep -q '"tools"'; then
    echo "✅ Tools list test passed"
    TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | grep -o '"name"' | wc -l)
    echo "📊 Found $TOOL_COUNT tools available"
else
    echo "❌ Tools list test failed"
    echo "Response: $TOOLS_RESPONSE"
    exit 1
fi

echo ""
echo "✅ MCP Server is working correctly!"
echo ""
echo "📋 Configuration for Claude Desktop:"
echo "======================================="

cat << EOF
Add this to your Claude Desktop config.json:

{
  "mcpServers": {
    "ipl-mcp-server": {
      "command": "$(pwd)/.venv/bin/python",
      "args": ["$(pwd)/server/app.py"],
      "env": {}
    }
  }
}

EOF

echo "📁 Claude Desktop config file locations:"
echo "• macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "• Windows: %APPDATA%\\Claude\\claude_desktop_config.json" 
echo "• Linux: ~/.config/Claude/claude_desktop_config.json"
echo ""

echo "🔄 Steps to connect:"
echo "1. Copy the configuration above"
echo "2. Add it to your Claude Desktop config.json file"
echo "3. Restart Claude Desktop"
echo "4. Look for 'ipl-mcp-server' in the MCP section"
echo ""

echo "🏏 Available IPL Tools:"
echo "• get_team_info - Get IPL team information"
echo "• get_player_info - Get player stats and details"  
echo "• get_match_details - Get match results and scores"
echo "• get_ball_by_ball - Get ball-by-ball commentary"
echo "• get_player_performance - Get detailed player performance"
echo "• get_match_officials - Get match officials information"
echo "• get_venue_info - Get cricket venue details"
echo ""
echo "🎯 You can now ask Claude questions like:"
echo "• \"Show me all IPL teams\""
echo "• \"Get Virat Kohli's batting stats\""  
echo "• \"Show me ball-by-ball for match 1394417\""
echo "• \"Get match details for Punjab Kings vs RCB\""
