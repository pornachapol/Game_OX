# app.py
import random
import streamlit as st

# -----------------------------
# Config & Theme
# -----------------------------
st.set_page_config(page_title="OX (Tic-Tac-Toe)", page_icon="🎮", layout="centered")

PRIMARY_BG = "#111318"
PANEL_BG   = "#1B1F2A"
ACCENT     = "#6C8CFF"
X_COLOR    = "#FF5C5C"
O_COLOR    = "#F56AC1"
GRID_BG    = "#23293A"

CSS = f"""
<style>
    .stApp {{
        background: {PRIMARY_BG};
        color: #FFFFFF;
    }}
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }}
    .title-wrap {{
        display:flex; align-items:center; gap:12px; margin-bottom:6px;
    }}
    .score-wrap {{
        background:{PANEL_BG}; padding:10px 14px; border-radius:12px; 
        display:inline-flex; gap:16px; font-weight:700; margin: 6px 0 16px 0;
        border:1px solid rgba(255,255,255,0.06);
    }}
    /* Board buttons */
    .stButton > button {{
        width: 100% !important;
        height: 110px !important;
        border-radius: 14px !important;
        background: {GRID_BG} !important;
        border: 2px solid rgba(255,255,255,0.08) !important;
        font-size: 44px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }}
    /* Make grid spacing nice */
    div[data-testid="column"] {{
        padding: 6px 8px !important;
    }}
    .panel {{
        background:{PANEL_BG}; padding:14px 16px; border-radius:12px;
        border:1px solid rgba(255,255,255,0.07);
    }}
    .smallnote {{ opacity:.8; font-size:.9rem; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Helpers: game logic
# -----------------------------
WIN_LINES = [
    (0,1,2), (3,4,5), (6,7,8),         # rows
    (0,3,6), (1,4,7), (2,5,8),         # cols
    (0,4,8), (2,4,6)                   # diagonals
]

def check_winner(board):
    for a,b,c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]  # "X" or "O"
    return None

def is_board_full(board):
    return all(cell != "" for cell in board)

def available_moves(board):
    return [i for i, v in enumerate(board) if v == ""]

def display_char(mark):
    return "❌" if mark == "X" else ("⭕" if mark == "O" else " ")

# -----------------------------
# Minimax for Hard AI
# -----------------------------
def minimax(board, ai_mark, human_mark, is_maximizing):
    winner = check_winner(board)
    if winner == ai_mark:
        return 10
    if winner == human_mark:
        return -10
    if is_board_full(board):
        return 0

    moves = available_moves(board)
    if is_maximizing:
        best = -999
        for m in moves:
            board[m] = ai_mark
            score = minimax(board, ai_mark, human_mark, False)
            board[m] = ""
            best = max(best, score)
        return best
    else:
        best = 999
        for m in moves:
            board[m] = human_mark
            score = minimax(board, ai_mark, human_mark, True)
            board[m] = ""
            best = min(best, score)
        return best

def best_move_minimax(board, ai_mark):
    human_mark = "O" if ai_mark == "X" else "X"
    best_score = -999
    move_best = None
    for m in available_moves(board):
        board[m] = ai_mark
        score = minimax(board, ai_mark, human_mark, False)
        board[m] = ""
        if score > best_score:
            best_score = score
            move_best = m
    return move_best

# -----------------------------
# Normal AI (rule-based)
# -----------------------------
def find_winning_move(board, mark):
    for m in available_moves(board):
        board[m] = mark
        if check_winner(board) == mark:
            board[m] = ""
            return m
        board[m] = ""
    return None

def best_move_normal(board, ai_mark):
    human_mark = "O" if ai_mark == "X" else "X"

    # 1) Win if possible
    m = find_winning_move(board, ai_mark)
    if m is not None:
        return m
    # 2) Block if needed
    m = find_winning_move(board, human_mark)
    if m is not None:
        return m
    # 3) Center
    if board[4] == "":
        return 4
    # 4) Corners
    corners = [i for i in [0,2,6,8] if board[i] == ""]
    if corners:
        return random.choice(corners)
    # 5) Sides
    sides = [i for i in [1,3,5,7] if board[i] == ""]
    if sides:
        return random.choice(sides)
    return None

# -----------------------------
# Easy AI (random)
# -----------------------------
def best_move_easy(board, ai_mark):
    moves = available_moves(board)
    return random.choice(moves) if moves else None

def get_ai_move(board, ai_mark, difficulty):
    if difficulty == "Hard":
        return best_move_minimax(board, ai_mark)
    elif difficulty == "Normal":
        return best_move_normal(board, ai_mark)
    else:
        return best_move_easy(board, ai_mark)

# -----------------------------
# Session State init
# -----------------------------
if "board" not in st.session_state:
    st.session_state.board = [""] * 9
if "current_player" not in st.session_state:
    st.session_state.current_player = "X"
if "scores" not in st.session_state:
    st.session_state.scores = {"X": 0, "O": 0, "TIE": 0}
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "mode" not in st.session_state:
    st.session_state.mode = "Human vs AI"
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Hard"
if "human_mark" not in st.session_state:
    st.session_state.human_mark = "X"   # You play as X by default

# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    mode = st.selectbox("Mode", ["Human vs AI", "Human vs Human"], index=0)
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.session_state.board = [""] * 9
        st.session_state.current_player = "X"
        st.session_state.game_over = False

    if st.session_state.mode == "Human vs AI":
        diff = st.selectbox("AI Difficulty", ["Easy", "Normal", "Hard"], index=["Easy","Normal","Hard"].index(st.session_state.difficulty))
        if diff != st.session_state.difficulty:
            st.session_state.difficulty = diff
            st.session_state.board = [""] * 9
            st.session_state.current_player = "X"
            st.session_state.game_over = False

        mark_pick = st.radio("You play as", ["X", "O"], horizontal=True, index=0)
        if mark_pick != st.session_state.human_mark:
            st.session_state.human_mark = mark_pick
            st.session_state.board = [""] * 9
            st.session_state.current_player = "X"
            st.session_state.game_over = False

    st.markdown("---")
    if st.button("🔁 New Round", use_container_width=True):
        st.session_state.board = [""] * 9
        st.session_state.current_player = "X"
        st.session_state.game_over = False

    if st.button("🗑️ Reset Score", use_container_width=True):
        st.session_state.scores = {"X": 0, "O": 0, "TIE": 0}
        st.session_state.board = [""] * 9
        st.session_state.current_player = "X"
        st.session_state.game_over = False

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="title-wrap"><span style="font-size:40px">🎮</span><h1>OX (Tic-Tac-Toe)</h1></div>', unsafe_allow_html=True)

sub = "👥 Human vs Human" if st.session_state.mode == "Human vs Human" else f"🤖 Human vs AI · <b>{st.session_state.difficulty}</b>"
st.markdown(f'<div class="smallnote">{sub}</div>', unsafe_allow_html=True)

# Score panel
sx = f'<span style="color:{X_COLOR}">✘ X</span>: {st.session_state.scores["X"]}'
so = f'<span style="color:{O_COLOR}">◯ O</span>: {st.session_state.scores["O"]}'
st.markdown(f'<div class="score-wrap">{sx} &nbsp;&nbsp; {so} &nbsp;&nbsp; 🥇 Tie: {st.session_state.scores["TIE"]}</div>', unsafe_allow_html=True)

# -----------------------------
# Game mechanics
# -----------------------------
def conclude_if_end():
    winner = check_winner(st.session_state.board)
    if winner:
        st.session_state.game_over = True
        st.session_state.scores[winner] += 1
        st.balloons()
        st.toast(f"{winner} wins! 🎉", icon="🏆")
        return True
    if is_board_full(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.scores["TIE"] += 1
        st.toast("It's a tie. 🤝", icon="💤")
        return True
    return False

def human_move(cell_index):
    if st.session_state.game_over:
        return
    if st.session_state.board[cell_index] == "":
        st.session_state.board[cell_index] = st.session_state.current_player
        # After human dropped, check
        if conclude_if_end():
            return
        # Next turn
        st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"

        # If vs AI and now AI's turn, make AI move
        if st.session_state.mode == "Human vs AI":
            ai_mark = "O" if st.session_state.human_mark == "X" else "X"
            if st.session_state.current_player == ai_mark and not st.session_state.game_over:
                ai_idx = get_ai_move(st.session_state.board, ai_mark, st.session_state.difficulty)
                if ai_idx is not None:
                    st.session_state.board[ai_idx] = ai_mark
                    if conclude_if_end():
                        return
                    st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"

# Auto-first move by AI when human chooses "O" and board is empty
if (
    st.session_state.mode == "Human vs AI"
    and st.session_state.human_mark == "O"
    and st.session_state.board == [""] * 9
    and not st.session_state.game_over
):
    ai_mark = "X"
    ai_idx = get_ai_move(st.session_state.board, ai_mark, st.session_state.difficulty)
    if ai_idx is not None:
        st.session_state.board[ai_idx] = ai_mark
        st.session_state.current_player = "O"
        # no conclude yet (first move can’t end the game)

# -----------------------------
# Render 3×3 Grid (clean columns)
# -----------------------------
for r in range(3):
    cols = st.columns(3, gap="small")
    for c in range(3):
        idx = r * 3 + c
        mark = st.session_state.board[idx]
        label = display_char(mark)

        # Use form per cell to avoid multiple clicks in same rerun
        with cols[c].form(key=f"cell-{idx}"):
            clicked = st.form_submit_button(label if label.strip() else " ", use_container_width=True)
            if clicked and mark == "":
                # Only allow the correct human to click when vs AI
                if st.session_state.mode == "Human vs AI":
                    if st.session_state.current_player == st.session_state.human_mark:
                        human_move(idx)
                else:
                    human_move(idx)

# Turn indicator
if not st.session_state.game_over:
    turn = st.session_state.current_player
    st.markdown(
        f'<div class="panel">Turn: {"❌" if turn=="X" else "⭕"} <b>{turn}</b></div>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<div class="panel">Game Over — start a new round from the sidebar.</div>', unsafe_allow_html=True)
