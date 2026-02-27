"""Tests for the TicTacToe class and calculate_fitness function.

Covers the calculate_fitness scoring metric, edge cases such as no available
moves, an identical output state, and perfect / near-perfect matches.
"""

from unittest import TestCase

from egppy.problems.tictactoe import TicTacToe, calculate_fitness, generate_state_graph


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
        # Intentionally invalid: fills all empty cells with 'O' and appends an extra 'X' (11 chars)
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


class TestTicTacToeInit(TestCase):
    """Test TicTacToe initialisation."""

    def test_default_init(self) -> None:
        """Default state has an empty board and last player O."""
        game = TicTacToe()
        self.assertEqual(game.board, [" "] * 9)
        self.assertEqual(game.last_player, "O")

    def test_custom_init(self) -> None:
        """A state string is parsed correctly on construction."""
        game = TicTacToe("XO       X")
        self.assertEqual(game.board[0], "X")
        self.assertEqual(game.board[1], "O")
        self.assertEqual(game.last_player, "X")


class TestTicTacToeFromStrToStr(TestCase):
    """Test from_str and to_str round-trip."""

    def test_round_trip(self) -> None:
        """to_str(from_str(s)) == s for an arbitrary legal state."""
        state = "XO  X   OX"
        game = TicTacToe()
        game.from_str(state)
        self.assertEqual(game.to_str(), state)

    def test_to_str_default(self) -> None:
        """Default state serialises to the expected string."""
        self.assertEqual(TicTacToe().to_str(), "         O")


class TestTicTacToeDunderStr(TestCase):
    """Test the __str__ visual representation."""

    def test_str_contains_separators(self) -> None:
        """__str__ output contains row separators."""
        output = str(TicTacToe())
        self.assertIn("-----", output)

    def test_str_contains_pipes(self) -> None:
        """__str__ output contains column delimiters."""
        output = str(TicTacToe())
        self.assertIn("|", output)

    def test_str_shows_pieces(self) -> None:
        """__str__ output reflects the board pieces."""
        game = TicTacToe("X        O")
        output = str(game)
        self.assertIn("X", output)


class TestTicTacToeReset(TestCase):
    """Test the reset method."""

    def test_reset_clears_board(self) -> None:
        """After reset the board is empty."""
        game = TicTacToe("XOX OX   X")
        game.reset()
        self.assertEqual(game.board, [" "] * 9)

    def test_reset_sets_last_player(self) -> None:
        """After reset last_player is O (so X moves first)."""
        game = TicTacToe("XOX OX   X")
        game.reset()
        self.assertEqual(game.last_player, "O")


class TestTicTacToeNextPlayer(TestCase):
    """Test the next_player helper."""

    def test_next_player_after_o(self) -> None:
        """When last_player is O the next player is X."""
        game = TicTacToe()
        self.assertEqual(game.next_player(), "X")

    def test_next_player_after_x(self) -> None:
        """When last_player is X the next player is O."""
        game = TicTacToe("X        X")
        self.assertEqual(game.next_player(), "O")


class TestTicTacToeMove(TestCase):
    """Test the move method."""

    def test_move_places_piece(self) -> None:
        """A valid move places the correct piece on the board."""
        game = TicTacToe()
        game.move("X", 0)
        self.assertEqual(game.board[0], "X")
        self.assertEqual(game.last_player, "X")

    def test_move_returns_false_when_no_win(self) -> None:
        """move() returns False when the game is not yet won."""
        game = TicTacToe()
        self.assertFalse(game.move("X", 4))

    def test_move_returns_true_on_win(self) -> None:
        """move() returns True when the move wins the game."""
        # X is at 0, 1; O is at 4, 5; last_player is O so X moves next.
        # Position 2 completes the top row for X.
        game = TicTacToe("XX  OO   O")
        self.assertTrue(game.move("X", 2))

    def test_move_invalid_player_raises(self) -> None:
        """move() raises AssertionError for an invalid player symbol."""
        game = TicTacToe()
        with self.assertRaises(AssertionError):
            game.move("A", 0)

    def test_move_invalid_position_raises(self) -> None:
        """move() raises AssertionError for a position outside 0–8."""
        game = TicTacToe()
        with self.assertRaises(AssertionError):
            game.move("X", 9)

    def test_move_taken_position_raises(self) -> None:
        """move() raises AssertionError when the position is occupied."""
        game = TicTacToe("X        X")
        with self.assertRaises(AssertionError):
            game.move("O", 0)

    def test_move_same_player_twice_raises(self) -> None:
        """move() raises AssertionError when the same player moves twice."""
        game = TicTacToe()
        game.move("X", 0)
        with self.assertRaises(AssertionError):
            game.move("X", 1)


class TestTicTacToeNextMoveOptions(TestCase):
    """Test next_move_options."""

    def test_empty_board_has_nine_options(self) -> None:
        """All 9 positions are available at the start."""
        self.assertEqual(TicTacToe().next_move_options(), list(range(9)))

    def test_partial_board(self) -> None:
        """Only unoccupied positions are returned."""
        game = TicTacToe("X  O     X")
        options = game.next_move_options()
        self.assertNotIn(0, options)  # X at 0
        self.assertNotIn(3, options)  # O at 3
        self.assertEqual(len(options), 7)

    def test_no_options_after_win(self) -> None:
        """next_move_options returns an empty list when the game is won."""
        # Top row already won by X.
        game = TicTacToe("XXX   OO X")
        self.assertEqual(game.next_move_options(), [])


class TestTicTacToeWinner(TestCase):
    """Test winner detection for all winning lines."""

    def test_no_winner_empty_board(self) -> None:
        """Empty board has no winner."""
        self.assertFalse(TicTacToe().winner())

    def test_winner_row_0(self) -> None:
        """Three in row 0 (positions 0,1,2) is a win."""
        # X at 0,1,2; O at 6,7 — valid state.
        game = TicTacToe("XXX   OO X")
        self.assertTrue(game.winner())

    def test_winner_row_1(self) -> None:
        """Three in row 1 (positions 3,4,5) is a win."""
        # X at 3,4,5; O at 7,8 — valid state.
        game = TicTacToe("   XXX OOX")
        self.assertTrue(game.winner())

    def test_winner_row_2(self) -> None:
        """Three in row 2 (positions 6,7,8) is a win."""
        # X at 6,7,8; O at 0,1 — valid state.
        game = TicTacToe("OO    XXXX")
        self.assertTrue(game.winner())

    def test_winner_col_0(self) -> None:
        """Three in column 0 (positions 0,3,6) is a win."""
        # X at 0,3,6; O at 2,5 — valid state.
        game = TicTacToe("X OX OX  X")
        self.assertTrue(game.winner())

    def test_winner_col_1(self) -> None:
        """Three in column 1 (positions 1,4,7) is a win."""
        # X at 1,4,7; O at 0,3 — valid state.
        game = TicTacToe("OX OX OX O")
        self.assertTrue(game.winner())

    def test_winner_col_2(self) -> None:
        """Three in column 2 (positions 2,5,8) is a win."""
        # X at 2,5,8; O at 0,1 — valid state.
        game = TicTacToe("OOX  X  XX")
        self.assertTrue(game.winner())

    def test_winner_main_diagonal(self) -> None:
        """Main diagonal (positions 0,4,8) is a win."""
        # X at 0,4,8; O at 3,6 — valid state.
        game = TicTacToe("X  OX O XX")
        self.assertTrue(game.winner())

    def test_winner_anti_diagonal(self) -> None:
        """Anti-diagonal (positions 2,4,6) is a win."""
        # X at 2,4,6; O at 1,5 — valid state.
        game = TicTacToe(" OX XOX  X")
        self.assertTrue(game.winner())

    def test_no_winner_partial_board(self) -> None:
        """Partial board with no winning line has no winner."""
        game = TicTacToe("XO XO    X")
        self.assertFalse(game.winner())


class TestTicTacToeValidState(TestCase):
    """Test valid_state for legal and illegal board positions."""

    def test_valid_default_state(self) -> None:
        """The default starting state is valid."""
        self.assertTrue(TicTacToe().valid_state())

    def test_valid_after_one_move(self) -> None:
        """State after one X move is valid."""
        game = TicTacToe("X        X")
        self.assertTrue(game.valid_state())

    def test_invalid_last_player(self) -> None:
        """A non-X/O last_player value makes the state invalid."""
        game = TicTacToe()
        game.last_player = "A"
        self.assertFalse(game.valid_state())

    def test_invalid_move_delta_too_large(self) -> None:
        """More than one move difference makes the state invalid."""
        # X has 4 pieces, O has 0 — delta is 4.
        game = TicTacToe("XXXX     X")
        self.assertFalse(game.valid_state())

    def test_invalid_last_player_o_unequal_counts(self) -> None:
        """When last_player is O the piece counts must be equal."""
        # X=2, O=1 — last_player O but delta != 0.
        game = TicTacToe("XOX      O")
        self.assertFalse(game.valid_state())

    def test_invalid_last_player_x_equal_counts(self) -> None:
        """When last_player is X the X count must exceed the O count by 1."""
        # X=1, O=1 — last_player X but delta != 1.
        game = TicTacToe("XO       X")
        self.assertFalse(game.valid_state())


class TestGenerateStateGraph(TestCase):
    """Test the generate_state_graph helper function."""

    initial_state: str
    state_graph: dict[str, list[str]]

    @classmethod
    def setUpClass(cls) -> None:
        """Generate the default state graph once for all tests in this class."""
        cls.initial_state = TicTacToe().to_str()
        cls.state_graph = generate_state_graph()

    def test_returns_dict(self) -> None:
        """generate_state_graph returns a dictionary."""
        self.assertIsInstance(self.state_graph, dict)

    def test_initial_state_present(self) -> None:
        """The starting state key is present in the graph."""
        self.assertIn(self.initial_state, self.state_graph)

    def test_graph_values_are_lists(self) -> None:
        """Every value in the graph is a list of successor states."""
        for value in self.state_graph.values():
            self.assertIsInstance(value, list)

    def test_graph_has_many_states(self) -> None:
        """The graph covers substantially more than just the initial state."""
        self.assertGreater(len(self.state_graph), 1)

    def test_graph_accepts_existing_graph_and_game(self) -> None:
        """Passing an existing graph and game does not raise and returns a dict."""
        seed_game = TicTacToe()
        seed_graph: dict = {seed_game.to_str(): []}
        result = generate_state_graph(graph=seed_graph, game=seed_game)
        self.assertIsInstance(result, dict)
        self.assertIn(seed_game.to_str(), result)
