import streamlit as st
import json

class TennisMatch:
    def __init__(self, player1="Player 1", player2="Player 2", best_of=3):
        self.players = [player1, player2]
        self.best_of = best_of
        self.sets_won = [0, 0]
        self.current_set = 1
        self.reset_set()
        self.server = 0  # 0 = player1 serving
        self.tiebreak_server_switch = 0
        self.stats = {
            0: {'aces': 0, 'double_faults': 0, 'winners': 0, 'unforced_errors': 0},
            1: {'aces': 0, 'double_faults': 0, 'winners': 0, 'unforced_errors': 0}
        }

    def reset_set(self):
        self.games = [0, 0]
        self.points = [0, 0]
        self.tiebreak = False
        self.tiebreak_points = [0, 0]
        self.tiebreak_server_switch = 0

    def is_tiebreak(self):
        return self.games == [6, 6]

    def award_point(self, winner, point_type='normal'):
        loser = 1 - winner
        if point_type == 'ace':
            self.stats[winner]['aces'] += 1
        elif point_type == 'double_fault':
            self.stats[loser]['double_faults'] += 1
        elif point_type == 'winner':
            self.stats[winner]['winners'] += 1
        elif point_type == 'unforced_error':
            self.stats[loser]['unforced_errors'] += 1

        if self.tiebreak:
            self.tiebreak_points[winner] += 1
            self.tiebreak_server_switch += 1
            if self.tiebreak_server_switch % 2 == 1 and self.tiebreak_server_switch > 1:
                self.server = 1 - self.server
            if self.tiebreak_points[winner] >= 7 and self.tiebreak_points[winner] - self.tiebreak_points[loser] >= 2:
                self.award_game(winner)
                self.tiebreak = False
        else:
            self.points[winner] += 1
            p1, p2 = self.points
            if max(p1, p2) >= 4:
                if p1 - p2 >= 2:
                    self.award_game(0)
                elif p2 - p1 >= 2:
                    self.award_game(1)
                elif p1 == p2 >= 4:
                    self.points = [3, 3]  # deuce

    def award_game(self, winner):
        self.games[winner] += 1
        self.points = [0, 0]
        self.tiebreak_points = [0, 0]
        self.server = 1 - self.server

        g1, g2 = self.games
        if (max(g1, g2) >= 6 and abs(g1 - g2) >= 2) or (max(g1, g2) == 7 and min(g1, g2) == 6):
            self.award_set(winner)
        elif g1 == 6 and g2 == 6:
            self.tiebreak = True
            self.tiebreak_server_switch = 0

    def award_set(self, winner):
        self.sets_won[winner] += 1
        self.current_set += 1
        self.reset_set()
        self.server = 1 - self.server  # alternate first server each set

        if max(self.sets_won) > self.best_of // 2:
            return True
        return False

    def get_score_display(self):
        if self.tiebreak:
            score = f"Tiebreak: {self.tiebreak_points[0]}–{self.tiebreak_points[1]}"
        else:
            pts_map = {0: "0", 1: "15", 2: "30", 3: "40"}
            p1 = pts_map.get(self.points[0], "AD" if self.points[0] > self.points[1] else "40")
            p2 = pts_map.get(self.points[1], "AD" if self.points[1] > self.points[0] else "40")
            if self.points == [3, 3]:
                p1 = p2 = "Deuce"
            score = f"Points: {p1} – {p2}"

        games = f"Games: {self.games[0]}–{self.games[1]}"
        sets = f"Sets: {self.sets_won[0]}–{self.sets_won[1]} (Set {self.current_set})"
        server = f"Server: {self.players[self.server]}{' *' if self.tiebreak else ''}"
        return f"{score}\n{games}\n{sets}\n{server}"

    def get_stats_display(self):
        lines = []
        for p in [0, 1]:
            lines.append(f"**{self.players[p]} Stats**")
            lines.append(f"Aces: {self.stats[p]['aces']}")
            lines.append(f"Double Faults: {self.stats[p]['double_faults']}")
            lines.append(f"Winners: {self.stats[p]['winners']}")
            lines.append(f"Unforced Errors: {self.stats[p]['unforced_errors']}")
            lines.append("")
        return "\n".join(lines)

    def to_json(self):
        return {
            'players': self.players,
            'best_of': self.best_of,
            'sets_won': self.sets_won,
            'current_set': self.current_set,
            'games': self.games,
            'points': self.points,
            'tiebreak': self.tiebreak,
            'tiebreak_points': self.tiebreak_points,
            'server': self.server,
            'tiebreak_server_switch': self.tiebreak_server_switch,
            'stats': self.stats
        }

    @classmethod
    def from_json(cls, data):
        match = cls(data['players'][0], data['players'][1], data['best_of'])
        match.sets_won = data['sets_won']
        match.current_set = data['current_set']
        match.games = data['games']
        match.points = data['points']
        match.tiebreak = data['tiebreak']
        match.tiebreak_points = data['tiebreak_points']
        match.server = data['server']
        match.tiebreak_server_switch = data['tiebreak_server_switch']
        match.stats = data['stats']
        return match

# ────────────────────────────────────────────────
#               STREAMLIT APP
# ────────────────────────────────────────────────

st.set_page_config(
    page_title="Tennis Match Scorer",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed"   # better on mobile
)

# Tennis theme styling
st.markdown("""
    <style>
    .stApp {
        background-color: #1e5c1e;  /* dark grass green */
    }
    .stButton > button {
        background-color: #f5d742;  /* tennis ball yellow */
        color: black;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #f5d742;
    }
    .block-container {
        padding-top: 1rem !important;
    }
    .stats-box {
        background-color: #0f3d0f;
        padding: 16px;
        border-radius: 8px;
        color: white;
    }
    .sponsor {
        text-align: center;
        color: #f5d742;
        font-style: italic;
        margin: 8px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎾 Tennis Match Scorer")

# Session state
if 'match' not in st.session_state:
    st.session_state.match = TennisMatch()

match = st.session_state.match

# ── Sidebar ─────────────────────────────────────
with st.sidebar:
    st.header("Match Setup")
    p1 = st.text_input("Player 1", value=match.players[0])
    p2 = st.text_input("Player 2", value=match.players[1])
    best_of = st.selectbox("Best of", [3, 5], index=0 if match.best_of == 3 else 1)

    if st.button("Start New Match"):
        st.session_state.match = TennisMatch(p1, p2, best_of)
        st.rerun()

    st.divider()
    st.header("Save / Load")
    if st.button("Save Match State"):
        json_str = json.dumps(match.to_json(), indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="tennis_match.json",
            mime="application/json"
        )

    uploaded = st.file_uploader("Upload saved match (JSON)", type=["json"])
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            st.session_state.match = TennisMatch.from_json(data)
            st.success("Match loaded!")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading file: {e}")

    st.divider()
    st.markdown('<div class="sponsor">Sponsored by Wilson</div>', unsafe_allow_html=True)
    st.markdown('<div class="sponsor">Powered by Head</div>', unsafe_allow_html=True)
    st.markdown('<div class="sponsor">Gear by Nike Tennis</div>', unsafe_allow_html=True)

# ── Main content ────────────────────────────────
col_score, col_controls = st.columns([2, 3])

with col_score:
    st.subheader("Current Score")
    st.code(match.get_score_display(), language=None)

    # Early match end check
    if max(match.sets_won) > match.best_of // 2:
        winner_idx = 0 if match.sets_won[0] > match.sets_won[1] else 1
        st.success(f"**MATCH COMPLETE!**  \n{match.players[winner_idx]} wins {match.sets_won[winner_idx]}–{match.sets_won[1-winner_idx]}")

with col_controls:
    st.subheader("Award Next Point")
    point_type = st.selectbox(
        "Point type (for stats)",
        ["normal", "ace", "double_fault", "winner", "unforced_error"]
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button(f"Point → {match.players[0]}", use_container_width=True):
            match.award_point(0, point_type)
            st.rerun()
    with btn_col2:
        if st.button(f"Point → {match.players[1]}", use_container_width=True):
            match.award_point(1, point_type)
            st.rerun()

# ── Stats ───────────────────────────────────────
st.subheader("Match Statistics")
st.markdown(f'<div class="stats-box">{match.get_stats_display()}</div>', unsafe_allow_html=True)
