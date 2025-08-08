import random
from typing import List, Optional, Tuple

import streamlit as st

# -----------------------------
# Page & Theme
# -----------------------------
st.set_page_config(page_title="OX Game • Streamlit", page_icon="🎮", layout="centered")

# Inject a bit of CSS for a slick look
st.markdown(
    """
    <style>
        :root {
            --x-color: #ff4b4b;
            --o-color: #2bb673;
            --board-bg: #0e1117; /* Streamlit dark bg friendly */
            --tile-bg: #1f2633;
            --tile-hover: #2a3342;
            --accent: #7aa2f7;
        }
        .board {
            display: grid;
            grid-template-columns: repeat(3, 110px);
            gap: 10px;
            justify-content: center;
            background: transparent;
            padding: 10px 0 20px 0;
        }
        .tile button {
            width: 110px !important;
            height: 110px !important;
            border-radius: 22px !important;
            background: var(--tile-bg) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            transition: all .15s ease;
            font-size: 44px !important;
            font-weight: 700 !important;
            letter-spacing: 1px;
        }
        .tile button:hover {
            background: var(--tile-hover) !important;
            transform: translateY(-1px);
        }
        .mark-x { color: var(--x-color); text-shadow: 0 0 16px rgba(255,75,75,.35); }
        .mark-o { color: var(--o-color); text-shadow: 0 0 16px rgba(43,182,115,.35); }
        .score-badge {
            padding: 6px 10px; border-radius: 10px; background: rgba(255,255,255,.04);
            border: 1px solid rgba(255,255,255,.08); margin-right: 8px;
        }
        .winner-text { font-weight: 800; font-size: 28px; }
        .subtle { opacity: .8 }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6)              # diags
]


def check_winner(board: List[str]) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
    for a, b, c in WIN_LINES:
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    if all(cell != "" for cell in board):
        return "TIE", None
    return None, None


def available_moves(board: List[str]) -> List[int]:
    return [i for i, v in enumerate(board) if v == ""]


def minimax(board: List[str], player: str, ai: str, human: str, depth: int,
            alpha: int, beta: int) -> Tuple[int, Optional[int]]:
    winner, _ = check_winner(board)
    if winner == ai:
        return 10 - depth, None
    if winner == human:
        return depth - 10, None
    if winner == "TIE":
        return 0, None

    if player == ai:
        best_score = -10**9
        best_move = None
        for m in available_moves(board):
            board[m] = ai
            score, _ = minimax(board, human, ai, human, depth + 1, alpha, beta)
            board[m] = ""
            if score > best_score:
                best_score, best_move = score, m
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = 10**9
        best_move = None
        for m in available_moves(board):
            board[m] = human
            score, _ = minimax(board, ai, ai, human, depth + 1, alpha, beta)
            board[m] = ""
            if score < best_score:
                best_score, best_move = score, m
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move


def best_ai_move(board: List[str], ai: str, human: str, difficulty: str) -> int:
    moves = available_moves(board)
    if difficulty == "Easy":
        return random.choice(moves)
    if difficulty == "Normal":
        # 60% optimal, 40% random to feel human
        if random.random() < 0.6:
            _, mv = minimax(board[:], ai, ai, human, 0, -10**9, 10**9)
            return mv if mv is not None else random.choice(moves)
        return random.choice(moves)
    # Hard
    _, mv = minimax(board[:], ai, ai, human, 0, -10**9, 10**9)
    return mv if mv is not None else random.choice(moves)


# -----------------------------
# State
# -----------------------------
if "board" not in st.session_state:
    st.session_state.board = [""] * 9
if "turn" not in st.session_state:
    st.session_state.turn = "X"
if "mode" not in st.session_state:
    st.session_state.mode = "Human vs AI"  # or "Human vs Human"
if "human" not in st.session_state:
    st.session_state.human = "X"
if "ai" not in st.session_state:
    st.session_state.ai = "O"
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Hard"
if "score" not in st.session_state:
    st.session_state.score = {"X": 0, "O": 0, "TIE": 0}
if "highlight" not in st.session_state:
    st.session_state.highlight = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False


# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("⚙️ Settings")
st.session_state.mode = st.sidebar.radio(
    "Mode", ["Human vs AI", "Human vs Human"], index=0
)

if st.session_state.mode == "Human vs AI":
    st.session_state.human = st.sidebar.radio("You play as", ["X", "O"], index=0)
    st.session_state.ai = "O" if st.session_state.human == "X" else "X"
    st.session_state.difficulty = st.sidebar.select_slider(
        "AI Difficulty", options=["Easy", "Normal", "Hard"], value=st.session_state.difficulty
    )

col_a, col_b = st.sidebar.columns(2)
if col_a.button("New Round"):
    st.session_state.board = [""] * 9
    st.session_state.turn = "X"
    st.session_state.highlight = None
    st.session_state.game_over = False

if col_b.button("Reset Score"):
    st.session_state.score = {"X": 0, "O": 0, "TIE": 0}
    st.session_state.board = [""] * 9
    st.session_state.turn = "X"
    st.session_state.highlight = None
    st.session_state.game_over = False

# -----------------------------
# Header & Scoreboard
# -----------------------------
st.title("🎮 OX (Tic‑Tac‑Toe)")
sub = "🤝 Human vs Human" if st.session_state.mode == "Human vs Human" else f"🧠 Human vs AI · {st.session_state.difficulty}"
st.caption(sub)

with st.container():
    s = st.session_state.score
    st.markdown(
        f"<span class='score-badge'>❌ X: <b>{s['X']}</b></span>"
        f"<span class='score-badge'>⭕ O: <b>{s['O']}</b></span>"
        f"<span class='score-badge'>🤝 Tie: <b>{s['TIE']}</b></span>",
        unsafe_allow_html=True,
    )

# -----------------------------
# Game Logic Handlers
# -----------------------------

def place_mark(idx: int):
    if st.session_state.game_over:
        return
    if st.session_state.board[idx] != "":
        return
    st.session_state.board[idx] = st.session_state.turn
    st.session_state.turn = "O" if st.session_state.turn == "X" else "X"

    winner, line = check_winner(st.session_state.board)
    if winner:
        st.session_state.game_over = True
        st.session_state.highlight = line
        st.session_state.score[winner] = st.session_state.score.get(winner, 0) + 1
        if winner == "TIE":
            st.toast("It's a tie!", icon="🤝")
        else:
            st.toast(f"{winner} wins!", icon="🏆")
            st.balloons()


def maybe_ai_move():
    if st.session_state.mode != "Human vs AI":
        return
    if st.session_state.game_over:
        return
    # It's AI's turn?
    if st.session_state.turn == st.session_state.ai:
        mv = best_ai_move(st.session_state.board[:], st.session_state.ai, st.session_state.human, st.session_state.difficulty)
        place_mark(mv)

# If human chose O and it's the very first turn, make AI start
if st.session_state.mode == "Human vs AI" and st.session_state.human == "O" and st.session_state.board == [""] * 9 and not st.session_state.game_over:
    maybe_ai_move()

# -----------------------------
# Board Rendering
# -----------------------------
st.markdown("<div class='board'>", unsafe_allow_html=True)
for r in range(3):
    for c in range(3):
        idx = r * 3 + c
        mark = st.session_state.board[idx]
        style_class = "mark-x" if mark == "X" else ("mark-o" if mark == "O" else "")
        label = mark if mark else "\u00A0"  # keep height
        # Each tile is its own form to avoid double-click issues
        with st.form(key=f"cell-{idx}"):
            submitted = st.form_submit_button(
                label=f":{style_class}:{label}" if style_class else label,
                use_container_width=False,
            )
            if submitted and mark == "":
                place_mark(idx)
        
st.markdown("</div>", unsafe_allow_html=True)

# After human move, let AI respond immediately
maybe_ai_move()

# -----------------------------
# Footer / Turn indicator
# -----------------------------
if not st.session_state.game_over:
    nxt = st.session_state.turn
    color = "var(--x-color)" if nxt == "X" else "var(--o-color)"
    st.markdown(f"<div class='subtle'>Next turn: <b style='color:{color}'>{nxt}</b></div>", unsafe_allow_html=True)
else:
    winner, _ = check_winner(st.session_state.board)
    if winner == "TIE":
        st.markdown("<div class='winner-text'>🤝 Tie Game</div>", unsafe_allow_html=True)
    else:
        color = "var(--x-color)" if winner == "X" else "var(--o-color)"
        st.markdown(f"<div class='winner-text'>🏆 Winner: <span style='color:{color}'>{winner}</span></div>", unsafe_allow_html=True)

st.caption("Built with ❤️ using Streamlit. Source: GitHub repository.")
