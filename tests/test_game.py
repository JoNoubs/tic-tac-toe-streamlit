import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import Board, HumanPlayer, SmartAIPlayer

class TestTicTacToe(unittest.TestCase):
    def setUp(self):
        self.board = Board(3, 3)

    def test_make_move(self):
        player = HumanPlayer("X")
        self.assertTrue(player.make_move(self.board, 0, 0))
        self.assertEqual(self.board.grid[0][0], "X")
        self.assertFalse(player.make_move(self.board, 0, 0))  # Already taken

    def test_check_win_row(self):
        player = HumanPlayer("X")
        player.make_move(self.board, 0, 0)
        player.make_move(self.board, 0, 1)
        player.make_move(self.board, 0, 2)
        self.assertTrue(self.board.check_win("X"))

    def test_check_win_column(self):
        player = HumanPlayer("X")
        player.make_move(self.board, 0, 0)
        player.make_move(self.board, 1, 0)
        player.make_move(self.board, 2, 0)
        self.assertTrue(self.board.check_win("X"))

    def test_check_win_diagonal(self):
        player = HumanPlayer("X")
        player.make_move(self.board, 0, 0)
        player.make_move(self.board, 1, 1)
        player.make_move(self.board, 2, 2)
        self.assertTrue(self.board.check_win("X"))

    def test_is_full(self):
        player_x = HumanPlayer("X")
        player_o = HumanPlayer("O")
        for i in range(3):
            for j in range(3):
                if (i + j) % 2 == 0:
                    player_x.make_move(self.board, i, j)
                else:
                    player_o.make_move(self.board, i, j)
        self.assertTrue(self.board.is_full())

if __name__ == "__main__":
    unittest.main()