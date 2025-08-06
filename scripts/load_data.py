import os
import sqlite3
import json
from glob import glob

DB_PATH = "ipl.db"
DATA_DIR = "data"

# Connect to SQLite DB
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id TEXT PRIMARY KEY,
    date TEXT,
    city TEXT,
    venue TEXT,
    team1 TEXT,
    team2 TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    winner TEXT,
    result TEXT,
    margin TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS deliveries (
    match_id TEXT,
    inning INTEGER,
    batting_team TEXT,
    bowling_team TEXT,
    over INTEGER,
    ball INTEGER,
    batsman TEXT,
    non_striker TEXT,
    bowler TEXT,
    runs_batsman INTEGER,
    runs_extras INTEGER,
    runs_total INTEGER,
    dismissal_kind TEXT,
    player_dismissed TEXT
)
""")

def parse_match(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    info = data.get("info", {})
    match_id = os.path.splitext(os.path.basename(filepath))[0]
    date = info["dates"][0]
    city = info.get("city", "")
    venue = info.get("venue", "")
    teams = info.get("teams", ["", ""])
    team1, team2 = teams[0], teams[1]

    toss = info.get("toss", {})
    toss_winner = toss.get("winner", "")
    toss_decision = toss.get("decision", "")

    outcome = info.get("outcome", {})
    winner = outcome.get("winner", "")
    result = outcome.get("result", "normal")
    margin = ""
    if "by" in outcome:
        if "runs" in outcome["by"]:
            margin = f"{outcome['by']['runs']} runs"
        elif "wickets" in outcome["by"]:
            margin = f"{outcome['by']['wickets']} wickets"

    # Insert match record
    cursor.execute("""
    INSERT OR REPLACE INTO matches
    (id, date, city, venue, team1, team2, toss_winner, toss_decision, winner, result, margin)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (match_id, date, city, venue, team1, team2, toss_winner, toss_decision, winner, result, margin))

    # Deliveries
    innings = data.get("innings", [])
    for inning_number, inning in enumerate(innings, start=1):
        for inning_name, inning_data in inning.items():
            batting_team = inning_data["team"]
            for over_data in inning_data["overs"]:
                over = over_data["over"]
                for delivery in over_data["deliveries"]:
                    batsman = delivery.get("batter")
                    non_striker = delivery.get("non_striker")
                    bowler = delivery.get("bowler")
                    bowling_team = delivery.get("team", "")
                    runs = delivery.get("runs", {})
                    runs_batsman = runs.get("batter", 0)
                    runs_extras = runs.get("extras", 0)
                    runs_total = runs.get("total", 0)
                    dismissal_kind = ""
                    player_dismissed = ""

                    if "wickets" in delivery:
                        wicket_info = delivery["wickets"][0]
                        dismissal_kind = wicket_info.get("kind", "")
                        player_dismissed = wicket_info.get("player_out", "")

                    ball = len(cursor.execute("SELECT * FROM deliveries WHERE match_id=? AND inning=? AND over=?",
                                              (match_id, inning_number, over)).fetchall()) + 1

                    cursor.execute("""
                    INSERT INTO deliveries (
                        match_id, inning, batting_team, bowling_team,
                        over, ball, batsman, non_striker, bowler,
                        runs_batsman, runs_extras, runs_total,
                        dismissal_kind, player_dismissed
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        match_id, inning_number, batting_team, team2 if batting_team == team1 else team1,
                        over, ball, batsman, non_striker, bowler,
                        runs_batsman, runs_extras, runs_total,
                        dismissal_kind, player_dismissed
                    ))

# Load all JSONs in /data/
json_files = glob(os.path.join(DATA_DIR, "*.json"))
for file_path in json_files:
    print(f"Loading: {file_path}")
    parse_match(file_path)

conn.commit()
conn.close()
print("✅ All matches loaded into ipl.db")
