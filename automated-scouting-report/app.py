import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# DATA
# -----------------------

map_win_rates = {
    "Lotus": 0.56,
    "Icebox": 0.67,
    "Sunset": 0.45,
    "Corrode": 0.66,
    "Bind": 0.41,
    "Ascent": 0.61,
    "Haven": 0.43
}

players = {
    "skuba": {"Kills": 207, "Deaths": 196, "Assists": 99},
    "brawk": {"Kills": 239, "Deaths": 194, "Assists": 88},
    "Ethan": {"Kills": 220, "Deaths": 204, "Assists": 143},
    "s0m": {"Kills": 221, "Deaths": 211, "Assists": 114},
    "mada": {"Kills": 241, "Deaths": 223, "Assists": 62}
}

star_player = "Ethan"

how_to_win = [
    "Force Sunset — NRG wins only 45% of rounds here.",
    "Force Bind — NRG wins only 41% of rounds here.",
    "Force Haven — NRG wins only 43% of rounds here.",
    "Avoid Icebox — NRG is very strong (67% win rate).",
    "Avoid Corrode — NRG is very strong (66% win rate).",
    "Lotus (56%), Ascent (61%) are neutral maps for NRG and not priority draft targets",
    "Target mada early — highest damage output on NRG."
]

team_strategies = [
    "Distributed fragging model with multiple players contributing consistently.",
    "Performs best on structured maps (Icebox, Corrode, Ascent).",
    "Struggles on high-variance maps (Sunset, Bind, Haven)."
]

map_bans = {"Bind": 3, "Sunset": 2, "Ascent": 1, "Lotus": 1}
map_picks = {"Lotus": 1, "Haven": 2, "Icebox": 2, "Corrode": 2}


st.set_page_config(page_title="NRG Scouting Report", layout="wide")

st.title("📊 Automated Scouting Report — NRG")
st.caption("Generated from GRID historical match data")



# -----------------------
# Map Win Rates
# -----------------------
st.header("🗺️ Map-Based Tendencies")

df_maps = pd.DataFrame.from_dict(
    map_win_rates, orient="index", columns=["Round Win Rate"]
)
st.bar_chart(df_maps)
st.divider()



# -----------------------
# Player Tendencies
# -----------------------
st.header("👥 Player Tendencies")

df_players = pd.DataFrame(players).T
df_players.columns = ["kills", "deaths", "assists"]

st.dataframe(df_players, use_container_width=True)


st.subheader("📊 Player Impact Comparison (Kills / Deaths / Assists)")

fig, ax = plt.subplots(figsize=(6, 3))

x = list(range(len(df_players)))
width = 0.25

ax.bar(
    [i - width for i in x],
    df_players["kills"].values,
    width,
    label="Kills"
)

ax.bar(
    x,
    df_players["deaths"].values,
    width,
    label="Deaths"
)

ax.bar(
    [i + width for i in x],
    df_players["assists"].values,
    width,
    label="Assists"
)

ax.set_xticks(x)
ax.set_xticklabels(df_players.index, rotation=30)
ax.set_ylabel("Count", fontsize=9)
ax.legend(fontsize=8)
ax.tick_params(axis="both", labelsize=8)

st.pyplot(fig, use_container_width=False)


# -----------------------
# Star Player
# -----------------------
st.divider()
st.header("⭐ Star Player")

st.success(f"**{star_player}** is the most impactful player based on overall contribution.")
st.divider()



# -----------------------
# Map Picks & Bans
# -----------------------
st.header("🗺️ Draft Tendencies")

st.subheader("📊 Map Picks vs Bans")

# Create combined DataFrame
df_draft = pd.DataFrame({
    "Bans": map_bans,
    "Picks": map_picks
}).fillna(0)

fig, ax = plt.subplots(figsize=(6, 3))

x = range(len(df_draft))
width = 0.35

ax.bar(
    [i - width/2 for i in x],
    df_draft["Bans"],
    width,
    label="Bans"
)

ax.bar(
    [i + width/2 for i in x],
    df_draft["Picks"],
    width,
    label="Picks"
)

ax.set_xticks(list(x))
ax.set_xticklabels(df_draft.index, rotation=30)
ax.set_ylabel("Count")
ax.legend(fontsize=8)

plt.tight_layout()
st.pyplot(fig, use_container_width=False)

st.divider()



# -----------------------
# Win Conversion & Loss Collapse
# -----------------------
st.header("📈 Win Conversion & Loss Collapse")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="🔥 Win Snowball Rate",
        value=f"{int(0.66 * 100)}%",
        help="How often NRG converts an early lead into a round win"
    )

with col2:
    st.metric(
        label="⚠️ Loss Collapse Rate",
        value=f"{int(0.59 * 100)}%",
        help="How often NRG collapses after losing early advantage"
    )
st.write("•", "NRG converts early leads effectively, but struggles to stabilize after early losses.")
st.write("•", "Apply early pressure and force eco rounds to exploit NRG’s higher collapse rate.")



# -----------------------
# Team-Wide Strategies
# -----------------------
st.divider()
st.header("🧠 Team-Wide Strategies")

for s in team_strategies:
    st.write("•", s)
st.divider()



# -----------------------
# How To Win
# -----------------------
st.header("🏆 How to Win Against NRG")

for h in how_to_win:
    st.warning(h)
