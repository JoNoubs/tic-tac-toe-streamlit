import streamlit as st
from dataclasses import dataclass, field
import numpy as np
from abc import ABC, abstractmethod
import random

# Configure Streamlit page
st.set_page_config(page_title="Tic Tac Toe", page_icon="❌⭕", layout="wide")
st.markdown("<h1 style='text-align: center;'>❌⭕ Tic-Tac-Toe </h1>", unsafe_allow_html=True)

# -----------------------------
# 🎮 GAME LOGIC
# -----------------------------

# Abstract base class for players
class Player(ABC):
    def __init__(self, symbol, name=""):
        self._symbol = symbol
        self._name = name or f"Player {symbol}"

    @property
    def symbol(self):
        return self._symbol

    @property
    def name(self):
        return self._name

    @abstractmethod
    def make_move(self, board, row=None, col=None):
        pass

# Human player class
class HumanPlayer(Player):
    def make_move(self, board, row, col):
        return board.make_move(row, col, self._symbol)

# AI player class with minimax algorithm
class SmartAIPlayer(Player):
    def make_move(self, board, row=None, col=None):
        best_score = -float('inf')
        best_move = None
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] == "":
                    board.grid[r][c] = self._symbol
                    score = self.minimax(board, 0, False, self._symbol, max_depth=3)
                    board.grid[r][c] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        if best_move:
            return board.make_move(best_move[0], best_move[1], self._symbol)
        return False

    def minimax(self, board, depth, is_maximizing, ai_symbol, max_depth):
        opponent = "O" if ai_symbol == "X" else "X"
        if board.check_win(ai_symbol):
            return 10 - depth
        elif board.check_win(opponent):
            return depth - 10
        elif board.is_full() or depth == max_depth:
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for r in range(board.rows):
                for c in range(board.cols):
                    if board.grid[r][c] == "":
                        board.grid[r][c] = ai_symbol
                        score = self.minimax(board, depth + 1, False, ai_symbol, max_depth)
                        board.grid[r][c] = ""
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for r in range(board.rows):
                for c in range(board.cols):
                    if board.grid[r][c] == "":
                        board.grid[r][c] = opponent
                        score = self.minimax(board, depth + 1, True, ai_symbol, max_depth)
                        board.grid[r][c] = ""
                        best_score = min(score, best_score)
            return best_score

@dataclass
class Board:
    rows: int
    cols: int
    grid: list = field(init=False)
    move_history: list = field(default_factory=list)

    def __post_init__(self):
        self.grid = [["" for _ in range(self.cols)] for _ in range(self.rows)]

    def make_move(self, row, col, player_symbol):
        if self.grid[row][col] == "":
            self.grid[row][col] = player_symbol
            self.move_history.append((row, col, player_symbol))
            return True
        return False

    def is_full(self):
        return all(cell != "" for row in self.grid for cell in row)

    def check_win(self, player_symbol):
        def check_line(line):
            return all(cell == player_symbol for cell in line)

        # Check rows and columns
        for i in range(self.rows):
            if check_line(self.grid[i]):
                return True
        for j in range(self.cols):
            if check_line([self.grid[i][j] for i in range(self.rows)]):
                return True

        # Check diagonals
        if check_line([self.grid[i][i] for i in range(min(self.rows, self.cols))]):
            return True
        if check_line([self.grid[i][self.cols - i - 1] for i in range(min(self.rows, self.cols))]):
            return True

        return False

@dataclass
class Game:
    rows: int
    cols: int
    player1_symbol: str = "X"
    board: Board = field(init=False)
    current_player: str = "X"
    winner: str = None
    ai_enabled: bool = False
    player1: Player = None
    player2: Player = None
    player1_name: str = "Player X"
    player2_name: str = "Player O"

    def __post_init__(self):
        self.board = Board(self.rows, self.cols)
        self.player2_symbol = "O" if self.player1_symbol == "X" else "X"
        self.player1 = HumanPlayer(self.player1_symbol, self.player1_name)
        self.player2 = SmartAIPlayer(self.player2_symbol, "AI") if self.ai_enabled else HumanPlayer(self.player2_symbol, self.player2_name)

    def play(self, row, col):
        if self.winner:
            return
        current_player_obj = self.player1 if self.current_player == self.player1.symbol else self.player2
        if self.ai_enabled and self.current_player != self.player1.symbol:
            return
        moved = current_player_obj.make_move(self.board, row, col)
        if moved:
            if self.board.check_win(self.current_player):
                self.winner = self.current_player
            elif self.board.is_full():
                self.winner = "Draw"
            else:
                self.current_player = self.player2.symbol if self.current_player == self.player1.symbol else self.player1.symbol
                if self.ai_enabled and self.current_player == self.player2.symbol and not self.winner:
                    self.player2.make_move(self.board)
                    if self.board.check_win(self.player2.symbol):
                        self.winner = self.player2.symbol
                    elif self.board.is_full():
                        self.winner = "Draw"
                    else:
                        self.current_player = self.player1.symbol

# ---------- Game Config UI ----------
if "game_started" not in st.session_state:
    st.session_state.game_started = False

if not st.session_state.game_started:
    st.subheader("🎮 Configure Your Game")
    player1_name = st.text_input("Name of Player ❌ (X):", "Player X")
    ai_enabled = st.checkbox("Play Against AI", value=True)
    player2_name = "AI" if ai_enabled else st.text_input("Name of Player ⭕ (O):", "Player O")
    rows = st.slider("Grid Rows", 3, 6, 3)
    cols = st.slider("Grid Columns", 3, 6, 3)

    if st.button("Start New Game 🎉"):
        st.session_state.game = Game(
            rows, cols,
            player1_symbol="X",
            ai_enabled=ai_enabled,
            player1_name=player1_name,
            player2_name=player2_name
        )
        st.session_state.scores = {"X": 0, "O": 0, "Draw": 0}
        st.session_state.game_started = True
        st.rerun()
else:
    game = st.session_state.game
    st.markdown(f"### 🧑‍🤝‍🧑 {game.player1.name} (❌) vs {game.player2.name} (⭕) — {game.rows}x{game.cols} Grid")

    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    with st.container():
        for i in range(game.rows):
            cols_streamlit = st.columns(game.cols)
            for j in range(game.cols):
                cell = game.board.grid[i][j]
                emoji = "❌" if cell == "X" else ("⭕" if cell == "O" else " ")
                if cell == "" and not game.winner:
                    if cols_streamlit[j].button(emoji, key=f"{i}-{j}", use_container_width=True):
                        game.play(i, j)
                        st.rerun()
                else:
                    cols_streamlit[j].button(emoji, key=f"{i}-{j}", disabled=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if game.winner == "Draw":
        st.warning("🤝 It's a draw!")
        st.session_state.scores["Draw"] += 1
    elif game.winner:
        winner_name = game.player1.name if game.winner == game.player1.symbol else game.player2.name
        st.success(f"🎉 {winner_name} wins!")
        st.session_state.scores[game.winner] += 1
    else:
        current_name = game.player1.name if game.current_player == game.player1.symbol else game.player2.name
        st.info(f"{current_name}'s turn ({game.current_player})")

    if st.button("🔄 New Game"):
        st.session_state.game_started = False
        st.rerun()

    with st.sidebar:
        st.header("📜 Move History")
        if game.board.move_history:
            for idx, (row, col, player) in enumerate(game.board.move_history):
                st.write(f"Move {idx + 1}: Player {player} at ({row}, {col})")
        else:
            st.write("No moves yet!")

        st.header("📊 Scores")
        st.write(f"❌ {game.player1.name}: {st.session_state.scores['X']} wins")
        st.write(f"⭕ {game.player2.name}: {st.session_state.scores['O']} wins")
        st.write(f"🤝 Draws: {st.session_state.scores['Draw']}")

# Privacy note
st.markdown("<div class='text-center mt-4 text-gray-600'><p>🔒 This app is privacy-friendly: no data is collected, and the game state is stored locally on your device.</p></div>", unsafe_allow_html=True)