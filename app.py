import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Pickleball Session Manager", layout="wide", page_icon="🏓")

# Initialize persistent session state variables
if "venue" not in st.session_state:
    st.session_state.venue = "Local Pickleball Club"
if "session_date" not in st.session_state:
    st.session_state.session_date = date.today()
if "players" not in st.session_state:
    st.session_state.players = {}
if "current_session_matches" not in st.session_state:
    st.session_state.current_session_matches = []
if "archived_sessions" not in st.session_state:
    st.session_state.archived_sessions = []

st.title("🏓 Pickleball Session Manager")

# Sidebar: Session & Venue Setup
with st.sidebar:
    st.header("1. Current Session Details")
    st.session_state.session_date = st.date_input("Session Date", st.session_state.session_date)
    st.session_state.venue = st.text_input("Venue Name", st.session_state.venue)
    
    # Close & Archive Session Button
    if st.button("🔒 Close Current Session & Start New", type="primary"):
        if st.session_state.current_session_matches:
            # Save the active session into archive
            session_summary = {
                "Date": st.session_state.session_date.strftime("%Y-%m-%d"),
                "Venue": st.session_state.venue,
                "Matches": list(st.session_state.current_session_matches)
            }
            st.session_state.archived_sessions.append(session_summary)
            
            # Reset active session
            st.session_state.current_session_matches = []
            st.session_state.players = {}
            st.success("Session closed and archived! Ready for a new session.")
            st.rerun()
        else:
            st.warning("No matches played in this session to close.")

    st.divider()
    st.header("2. Register Players")
    new_player = st.text_input("Add Player Name")
    if st.button("Add Player") and new_player.strip():
        if new_player not in st.session_state.players:
            st.session_state.players[new_player] = {"games_played": 0, "status": "Available"}
            st.success(f"Added {new_player}")
        else:
            st.warning("Player already added.")

    st.subheader("Active Roster")
    for name, info in list(st.session_state.players.items()):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{name}** ({info['games_played']} games)")
        if col2.button("❌", key=f"del_{name}"):
            del st.session_state.players[name]
            st.rerun()

st.caption(f"📅 **Date:** {st.session_state.session_date} | 📍 **Venue:** {st.session_state.venue}")

# Main Tabs
tab1, tab2, tab3 = st.tabs(["🎾 Active Games", "🏆 Current Session Results", "📊 All Archived Sessions"])

# TAB 1: Game Generator & Score Logging
with tab1:
    st.header("Game Organizer")
    game_mode = st.radio("Select Mode", ["Doubles (4 Players)", "Singles (2 Players)"], horizontal=True)
    needed_players = 4 if "Doubles" in game_mode else 2
    
    available_players = [p for p, data in st.session_state.players.items() if data["status"] == "Available"]
    
    if len(available_players) < needed_players:
        st.info(f"Need at least {needed_players} players to generate a game. Currently available: {len(available_players)}")
    else:
        # Fair Play Algorithm: Sort players by FEWEST games played
        sorted_players = sorted(available_players, key=lambda p: st.session_state.players[p]["games_played"])
        selected_players = sorted_players[:needed_players]
        
        st.subheader("Suggested Match")
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
            for p in selected_players:
                st.session_state.players[p]["games_played"] += 1
            
            record = {
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Mode": "Doubles" if needed_players == 4 else "Singles",
                "Team A": ", ".join(team_a),
                "Score A": score_a,
                "Score B": score_b,
                "Team B": ", ".join(team_b),
                "Winner": "Team A" if score_a > score_b else ("Team B" if score_b > score_a else "Draw")
            }
            st.session_state.current_session_matches.append(record)
            st.balloons()
            st.success("Result Saved!")
            st.rerun()

# TAB 2: Current Session Leaderboard
with tab2:
    st.header(f"Results for Session: {st.session_state.session_date}")
    if st.session_state.current_session_matches:
        df_current = pd.DataFrame(st.session_state.current_session_matches)
        st.dataframe(df_current, use_container_width=True)
    else:
        st.write("No matches recorded for this active session yet.")

# TAB 3: Historical & Archived Sessions
with tab3:
    st.header("Archived Sessions History")
    if st.session_state.archived_sessions:
        for idx, sess in enumerate(reversed(st.session_state.archived_sessions)):
            with st.expander(f"📅 Session: {sess['Date']} @ {sess['Venue']}"):
                df_archive = pd.DataFrame(sess["Matches"])
                st.dataframe(df_archive, use_container_width=True)
    else:
        st.write("No closed/archived sessions yet. Once you click 'Close Current Session', it will appear here.")
