import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pickleball Session Manager", layout="wide", page_icon="🏓")

# Initialize persistent session state variables
if "venue" not in st.session_state:
    st.session_state.venue = "Local Pickleball Club"
if "players" not in st.session_state:
    # Player structure: {name: {"games_played": 0, "status": "Available"}}
    st.session_state.players = {}
if "match_history" not in st.session_state:
    st.session_state.match_history = []

st.title("🏓 Pickleball Session Manager")

# Sidebar: Venue Setup & Player Registration
with st.sidebar:
    st.header("1. Venue & Settings")
    st.session_state.venue = st.text_input("Venue Name", st.session_state.venue)
    
    st.header("2. Register Players")
    new_player = st.text_input("Add Player Name")
    if st.button("Add Player") and new_player.strip():
        if new_player not in st.session_state.players:
            st.session_state.players[new_player] = {"games_played": 0, "status": "Available"}
            st.success(f"Added {new_player}")
        else:
            st.warning("Player already added.")

    st.subheader("Player Roster")
    for name, info in list(st.session_state.players.items()):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{name}** ({info['games_played']} games)")
        if col2.button("❌", key=f"del_{name}"):
            del st.session_state.players[name]
            st.rerun()

st.caption(f"📍 **Current Venue:** {st.session_state.venue}")

# Main Tabs
tab1, tab2, tab3 = st.tabs(["🎾 Active Games", "🏆 Live Leaderboard", "📊 Historical Stats"])

# TAB 1: Game Generator & Score Logging
with tab1:
    st.header("Game Organizer")
    game_mode = st.radio("Select Mode", ["Doubles (4 Players)", "Singles (2 Players)"], horizontal=True)
    needed_players = 4 if "Doubles" in game_mode else 2
    
    # Filter available players
    available_players = [p for p, data in st.session_state.players.items() if data["status"] == "Available"]
    
    if len(available_players) < needed_players:
        st.info(f"Need at least {needed_players} players to generate a game. Currently available: {len(available_players)}")
    else:
        # Fair Play Algorithm: Sort players by FEWEST games played to balance rest & play time
        sorted_players = sorted(available_players, key=lambda p: st.session_state.players[p]["games_played"])
        selected_players = sorted_players[:needed_players]
        
        st.subheader("Suggested Match (Balanced Playtime)")
        if needed_players == 4:
            team_a = selected_players[:2]
            team_b = selected_players[2:]
            st.success(f"**Team A:** {team_a[0]} & {team_a[1]}  🆚  **Team B:** {team_b[0]} & {team_b[1]}")
        else:
            team_a = [selected_players[0]]
            team_b = [selected_players[1]]
            st.success(f"**Team A:** {team_a[0]}  🆚  **Team B:** {team_b[1]}")
        
        # Log Score Section
        st.markdown("### Record Score")
        col_score1, col_score2 = st.columns(2)
        score_a = col_score1.number_input(f"Team A Score ({', '.join(team_a)})", min_value=0, max_value=30, value=11)
        score_b = col_score2.number_input(f"Team B Score ({', '.join(team_b)})", min_value=0, max_value=30, value=9)
        
        if st.button("Submit Match Result"):
            # Update games played count
            for p in selected_players:
                st.session_state.players[p]["games_played"] += 1
            
            # Save result to history
            record = {
                "Timestamp": datetime.now(),
                "Venue": st.session_state.venue,
                "Mode": "Doubles" if needed_players == 4 else "Singles",
                "Team A": ", ".join(team_a),
                "Score A": score_a,
                "Score B": score_b,
                "Team B": ", ".join(team_b),
                "Winner": "Team A" if score_a > score_b else ("Team B" if score_b > score_a else "Draw")
            }
            st.session_state.match_history.append(record)
            st.balloons()
            st.success("Result Saved!")
            st.rerun()

# TAB 2: Live Leaderboard
with tab2:
    st.header("Current Session Results")
    if st.session_state.match_history:
        df = pd.DataFrame(st.session_state.match_history)
        st.dataframe(df[["Timestamp", "Venue", "Mode", "Team A", "Score A", "Score B", "Team B", "Winner"]], use_container_width=True)
    else:
        st.write("No matches recorded for this session yet.")

# TAB 3: Historical Stats Filters
with tab3:
    st.header("Historical Stats & Tables")
    if st.session_state.match_history:
        df = pd.DataFrame(st.session_state.match_history)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        
        filter_option = st.selectbox("View Results By:", ["All Time", "This Week", "This Month"])
        now = datetime.now()
        
        if filter_option == "This Week":
            filtered_df = df[df["Timestamp"].dt.isocalendar().week == now.isocalendar().week]
        elif filter_option == "This Month":
            filtered_df = df[(df["Timestamp"].dt.month == now.month) & (df["Timestamp"].dt.year == now.year)]
        else:
            filtered_df = df
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.write("No historical data available.")