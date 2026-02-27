"""Tests for the TicTacToe class and calculate_fitness function.

Covers the calculate_fitness scoring metric, edge cases such as no available
moves, an identical output state, and perfect / near-perfect matches.
"""

from unittest import TestCase

from egppy.problems.tictactoe import TicTacToe, calculate_fitness


class TestCalculateFitness(TestCase):
    """Test calculate_fitness(input_state, output_state) -> float."""

    # ------------------------------------------------------------------
    # Hard constraints
    # ------------------------------------------------------------------

    def test_identical_states_returns_zero(self) -> None:
        """Identical input and output states must return exactly 0.0."""
        state = "         O"
        self.assertEqual(calculate_fitness(state, state), 0.0)

    def test_game_over_returns_zero(self) -> None:
        """A finished board (winner exists) with no valid moves returns 0.0."""
        # X wins the top row
        won_state = "XXXOO    X"
        game = TicTacToe(won_state)
        self.assertTrue(game.winner(), "Precondition: this board should be won.")
        self.assertEqual(calculate_fitness(won_state, "XXXOO    O"), 0.0)

    # ------------------------------------------------------------------
    # Return-type and range
    # ------------------------------------------------------------------

    def test_returns_float(self) -> None:
        """calculate_fitness always returns a float."""
        result = calculate_fitness("         O", "X        X")
        self.assertIsInstance(result, float)

    def test_result_in_open_unit_interval(self) -> None:
        """Non-trivial output states produce a score strictly in (0, 1]."""
        result = calculate_fitness("         O", "X        X")
        self.assertGreater(result, 0.0)
        self.assertLessEqual(result, 1.0)

    # ------------------------------------------------------------------
    # Perfect match
    # ------------------------------------------------------------------

    def test_perfect_match_returns_one(self) -> None:
        """A perfect valid next state returns fitness 1.0."""
        input_state = "         O"
        game = TicTacToe(input_state)
        player = game.next_player()
        for position in game.next_move_options():
            candidate = TicTacToe(input_state)
            candidate.move(player, position)
            score = calculate_fitness(input_state, candidate.to_str())
            self.assertAlmostEqual(score, 1.0, places=10, msg=f"position={position}")

    # ------------------------------------------------------------------
    # Distance / ordering
    # ------------------------------------------------------------------

    def test_closer_state_scores_higher(self) -> None:
        """A state closer to a valid next state scores higher than a random one."""
        input_state = "         O"
        # Example of a valid next move: place X at position 0 → "X        X"
        valid_next = "X        X"
        # A clearly wrong output with multiple invalid differences
        bad_output = "OOOOOOOOO X"
        score_valid = calculate_fitness(input_state, valid_next)
        score_bad = calculate_fitness(input_state, bad_output)
        self.assertGreater(score_valid, score_bad)

    def test_extra_valid_chars_penalised(self) -> None:
        """Extra valid characters beyond index 9 reduce the fitness score."""
        input_state = "         O"
        # Perfect state
        perfect = "X        X"
        # Same but with an extra valid character appended
        extra = "X        X "
        score_perfect = calculate_fitness(input_state, perfect)
        score_extra = calculate_fitness(input_state, extra)
        self.assertGreater(score_perfect, score_extra)

    def test_extra_invalid_chars_penalised_more(self) -> None:
        """Extra invalid characters beyond index 9 incur a higher penalty."""
        input_state = "         O"
        perfect = "X        X"
        extra_valid = "X        X "
        extra_invalid = "X        X!"
        score_extra_valid = calculate_fitness(input_state, extra_valid)
        score_extra_invalid = calculate_fitness(input_state, extra_invalid)
        self.assertGreater(score_extra_valid, score_extra_invalid)

    def test_missing_characters_penalised(self) -> None:
        """A truncated output state (missing characters) scores lower than perfect."""
        input_state = "         O"
        perfect = "X        X"
        truncated = "X        "  # only 9 characters
        score_perfect = calculate_fitness(input_state, perfect)
        score_truncated = calculate_fitness(input_state, truncated)
        self.assertGreater(score_perfect, score_truncated)

    def test_invalid_character_at_board_position(self) -> None:
        """An invalid character at a board position scores lower than a valid mismatch."""
        input_state = "         O"
        # Valid character mismatch (cost 1 per char, depending on position)
        valid_mismatch = "O        X"
        # Invalid character at position 0 (cost 3)
        invalid_char = "!        X"
        score_valid = calculate_fitness(input_state, valid_mismatch)
        score_invalid = calculate_fitness(input_state, invalid_char)
        self.assertGreater(score_valid, score_invalid)

    # ------------------------------------------------------------------
    # Mid-game state
    # ------------------------------------------------------------------

    def test_mid_game_state(self) -> None:
        """Mid-game state: a valid next state scores 1.0."""
        # X moved first (to position 0), now it is O's turn
        input_state = "X        X"
        game = TicTacToe(input_state)
        player = game.next_player()
        for position in game.next_move_options():
            candidate = TicTacToe(input_state)
            candidate.move(player, position)
            score = calculate_fitness(input_state, candidate.to_str())
            self.assertAlmostEqual(score, 1.0, places=10)
