import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # automated-scouting-report/
DATA_DIR = BASE_DIR / "data"

#Load JSON file
def load_series(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


#File paths
series_files = [
    DATA_DIR / "c9_esports_data_2843070.json",
    DATA_DIR / "c9_esports_data_2843071.json",
    DATA_DIR / "c9_esports_data_2843069.json",
    DATA_DIR / "c9_esports_data_2843067.json",
    DATA_DIR / "c9_esports_data_2843063.json",
]


#Load all raw JSONs
all_series = []
for file in series_files:
    all_series.append(load_series(file))


#Extract the data
series_states = []
for series in all_series:
    series_states.append(series["data"]["seriesState"])



# -----------------------
# Extract round-level data for opponent
# -----------------------
OPPONENT = "NRG"

def extract_round_data(series_states, opponent):
    rounds = []

    for series in series_states:
        for game in series["games"]:
            map_name = game["map"]["name"]

            for segment in game["segments"]:
                if not segment["finished"]:
                    continue

                for team in segment["teams"]:
                    if team["name"] == opponent:
                        rounds.append({
                            "map": map_name,
                            "won": team["won"],
                            "players": team["players"]
                        })

    return rounds

rounds = extract_round_data(series_states, OPPONENT)
print("Total rounds for", OPPONENT, ":", len(rounds))


# -----------------------
# Compute map win rates
# -----------------------
def map_win_rates(rounds):
    stats = defaultdict(lambda: {"wins": 0, "total": 0})

    for r in rounds:
        stats[r["map"]]["total"] += 1
        if r["won"]:
            stats[r["map"]]["wins"] += 1

    for m in stats:
        stats[m]["win_rate"] = round(stats[m]["wins"] / stats[m]["total"], 2)

    return stats

map_stats = map_win_rates(rounds)
print("\nMap Win Rates:")
for m, v in map_stats.items():
    print(m, "→", v)


# -----------------------
# Compute player stats
# -----------------------
def player_stats(rounds):
    stats = defaultdict(lambda: {"kills": 0, "deaths": 0, "assists": 0})

    for r in rounds:
        for p in r["players"]:
            name = p["name"]
            stats[name]["kills"] += p["kills"]
            stats[name]["deaths"] += p["deaths"]
            stats[name]["assists"] += p["killAssistsGiven"]

    return stats

players = player_stats(rounds)
print("\nPlayer Stats:")
for p, s in players.items():
    print(p, s)


# -----------------------
# Identify star player
# -----------------------
star_player = max(
    players.items(),
    key=lambda x: x[1]["kills"] + x[1]["assists"]
)
print("\nStar Player:")
print(star_player)


# -----------------------
# win Conversion & Loss Collapse Rates
# -----------------------
def round_level_patterns(rounds):
    patterns = {
        "loss_after_loss": 0,
        "loss_sequences": 0,
        "win_after_win": 0,
        "win_sequences": 0
    }

    prev = None
    for r in rounds:
        if prev is not None:
            # losing streak
            if prev is False:
                patterns["loss_sequences"] += 1
                if r["won"] is False:
                    patterns["loss_after_loss"] += 1

            # winning streak
            if prev is True:
                patterns["win_sequences"] += 1
                if r["won"] is True:
                    patterns["win_after_win"] += 1

        prev = r["won"]

    loss_collapse_rate = (
        patterns["loss_after_loss"] / patterns["loss_sequences"]
        if patterns["loss_sequences"] > 0 else 0
    )

    win_snowball_rate = (
        patterns["win_after_win"] / patterns["win_sequences"]
        if patterns["win_sequences"] > 0 else 0
    )

    return {
        "loss_collapse_rate": round(loss_collapse_rate, 2),
        "win_snowball_rate": round(win_snowball_rate, 2)
    }

round_patterns = round_level_patterns(rounds)
print("\n")
print("Win Conversion & Loss Collapse Rates")
print(round_patterns)


# -----------------------
# Map Draft Tendencies (Picks & Bans)
# -----------------------
EVENT_FILE = [
    DATA_DIR / "events_2843071_grid.jsonl",
    DATA_DIR / "events_2843070_grid.jsonl",
    DATA_DIR / "events_2843069_grid.jsonl",
    DATA_DIR / "events_2843067_grid.jsonl",
    DATA_DIR / "events_2843063_grid.jsonl",
]

def extract_map_draft_events(paths):
    bans = defaultdict(lambda: defaultdict(int))
    picks = defaultdict(lambda: defaultdict(int))

    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)

                for event in data.get("events", []):
                    event_type = event.get("type")

                    if event_type in ["team-banned-map", "team-picked-map"]:
                        team = event["actor"]["state"]["name"]
                        map_name = event["target"]["state"]["name"]

                        if event_type == "team-banned-map":
                            bans[team][map_name] += 1
                        else:
                            picks[team][map_name] += 1

                    elif event_type == "series-picked-map":
                        map_name = event["target"]["state"]["name"]
                        picks["DECIDER"][map_name] += 1

    return bans, picks


bans, picks = extract_map_draft_events(EVENT_FILE)

OPPONENT = "NRG"

print("\nNRG MAP BANS:")
print(dict(bans.get(OPPONENT, {})))

print("\nNRG MAP PICKS:")
print(dict(picks.get(OPPONENT, {})))


# -----------------------
# TEAM-WIDE STRATEGIC IDENTITY ANALYSIS
# -----------------------
def team_wide_strategies(players, map_win_rates):
    strategies = []

    total_kills = sum(p["kills"] for p in players.values())
    star_name, star_stats = max(players.items(), key=lambda x: x[1]["kills"])
    star_kill_share = star_stats["kills"] / total_kills

    if star_kill_share > 0.35:
        strategies.append(
            f"High dependency on {star_name}, who contributes {int(star_kill_share*100)}% of total team kills."
        )
    else:
        strategies.append(
            "Distributed fragging model with multiple players contributing consistently."
        )

    support_players = [
        name for name, stats in players.items()
        if stats["assists"] > stats["kills"]
    ]

    if len(support_players) >= 2:
        strategies.append(
            f"Utility- and support-heavy playstyle driven by {', '.join(support_players)}."
        )

    strong_maps = [m for m, d in map_win_rates.items() if d["win_rate"] >= 0.6]
    weak_maps = [m for m, d in map_win_rates.items() if d["win_rate"] <= 0.45]

    if strong_maps:
        strategies.append(
            f"Team performs best on structured maps such as {', '.join(strong_maps)}."
        )

    if weak_maps:
        strategies.append(
            f"Team struggles on looser, high-variance maps like {', '.join(weak_maps)}."
        )

    return strategies

team_strategy = team_wide_strategies(players, map_stats)

print("\nTEAM-WIDE STRATEGIES:")
for s in team_strategy:
    print("-", s)


# -----------------------
# how to win strats
# -----------------------
def how_to_win(map_stats, players):
    insights = []

    weak_maps = []
    strong_maps = []
    neutral_maps = []

    # Categorize maps
    for m, v in map_stats.items():
        win_rate = v["win_rate"]

        if win_rate <= 0.45:
            weak_maps.append((m, win_rate))
        elif win_rate >= 0.65:
            strong_maps.append((m, win_rate))
        else:
            neutral_maps.append((m, win_rate))

    # Weak maps → force
    for m, wr in weak_maps:
        insights.append(
            f"Force {m.title()} — NRG wins only {int(wr * 100)}% of rounds here."
        )

    # Strong maps → avoid
    for m, wr in strong_maps:
        insights.append(
            f"Avoid {m.title()} — NRG is very strong with a {int(wr * 100)}% win rate."
        )

    # Neutral maps → clarify
    if neutral_maps:
        neutral_names = ", ".join(
            f"{m.title()} ({int(wr * 100)}%)" for m, wr in neutral_maps
        )
        insights.append(
            f"{neutral_names} are neutral maps for NRG and not priority draft targets."
        )

    # Star player (NOW properly used)
    star_name, star_stats = max(players.items(), key=lambda x: x[1]["kills"])
    insights.append(
    f"Target {star_name} early — highest damage output on NRG "
    f"with {star_stats['kills']} total kills."
)

    return insights

insights = how_to_win(map_stats, players)

print("\nHOW TO WIN:")
for i in insights:
    print("-", i)