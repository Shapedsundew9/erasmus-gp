"""Tic-Tac-Toe game implementations.
See docs/tic-tac-toe.md for more information.
"""


class TicTacToe:
    """Tic-Tac-Toe game.

    The board state is stored internally as a ``list[str]`` (``self.board``) to
    allow O(1) in-place mutation when a player makes a move.  Strings are
    immutable in Python, so updating a single cell of a string would require
    creating an entirely new string on every move, which is unnecessarily
    wasteful during gameplay.

    The compact string representation (see ``to_str()``) is used **externally**
    whenever an immutable, hashable key is needed – for example as a node
    identifier in the state graph produced by ``generate_state_graph()``.
    Converting to a string on demand keeps the hot path (``move()``) fast while
    still providing an efficient format for storage and hashing.
    """

    def __init__(self, state: str = "         O") -> None:
        """Initialize the game from a state string.

        Args:
            state: A 10-character string encoding the board and the last player.
                The first 9 characters represent the 9 cells of the board
                (``' '``, ``'X'``, or ``'O'``), and the 10th character is the
                last player to move (``'X'`` or ``'O'``).  Defaults to an empty
                board where ``'O'`` moved last (so ``'X'`` moves first).

        Note:
            ``self.board`` is stored as a ``list[str]`` rather than a string so
            that individual cell updates during ``move()`` are O(1) mutations
            rather than O(n) string reconstructions.
        """
        self.board: list[str] = [] * 9
        self.last_player: str = ""
        self.from_str(state)

    def __str__(self) -> str:
        """Return the board as a string."""
        retval = "|".join(self.board[:3]) + "\n"
        retval += "-" * 5 + "\n"
        retval += "|".join(self.board[3:6]) + "\n"
        retval += "-" * 5 + "\n"
        retval += "|".join(self.board[6:9])
        return retval

    def from_str(self, state: str) -> None:
        """Set the state of the game from a string."""
        self.board = list(state[:-1])
        self.last_player = state[-1]

    def move(self, player: str, position: int) -> bool:
        """Make a move and return True if the move wins the game."""
        assert player in ("X", "O"), f"Invalid player {player}"
        assert 0 <= position < 9, f"Invalid position {position}"
        assert self.board[position] == " ", f"Position {position} is already taken"
        assert player != self.last_player, "Players must take alternate turns."
        self.last_player = player
        self.board[position] = player
        return self.winner()

    def next_move_options(self) -> list[int]:
        """Return a list of possible moves."""
        return [i for i, v in enumerate(self.board) if v == " "] if not self.winner() else []

    def next_player(self) -> str:
        """Return the next player."""
        return "X" if self.last_player == "O" else "O"

    def reset(self) -> None:
        """Reset the game."""
        self.board = [" "] * 9
        self.last_player = "O"

    def to_str(self) -> str:
        """Return the state of the game as a compact, hashable string.

        The returned 10-character string encodes the full game state: the first
        9 characters are the board cells (``' '``, ``'X'``, or ``'O'``) and the
        10th character is the last player to move.  This format is used for
        external storage and as node keys in the state graph (see
        ``generate_state_graph()``) where an immutable, hashable representation
        is required.

        Returns:
            A 10-character string representing the current game state.
        """
        return "".join(self.board) + self.last_player

    def valid_state(self) -> bool:
        """Return True if the state is valid."""
        if len(self.board) != 9:
            return False
        if self.last_player not in ("X", "O"):
            return False
        move_delta = abs(self.board.count("X") - self.board.count("O"))
        if move_delta > 1:
            return False
        if self.last_player == "X" and move_delta != 1:
            return False
        if self.last_player == "O" and move_delta != 0:
            return False
        return True

    def winner(self) -> bool:
        """Return True if the game is won."""
        for i in range(3):
            if self.board[i] == self.board[i + 3] == self.board[i + 6] != " ":
                return True
            if self.board[i * 3] == self.board[i * 3 + 1] == self.board[i * 3 + 2] != " ":
                return True
        if self.board[0] == self.board[4] == self.board[8] != " ":
            return True
        if self.board[2] == self.board[4] == self.board[6] != " ":
            return True
        return False


def generate_state_graph(
    graph: None | dict[str, list] = None, game: TicTacToe | None = None
) -> dict[str, list]:
    """Generate the state graph."""
    _graph = graph or {TicTacToe().to_str(): []}
    _game = game or TicTacToe()
    initial_state = _game.to_str()

    for next_move in _game.next_move_options():
        new_game = TicTacToe(_game.to_str())
        new_game.move(_game.next_player(), next_move)
        if new_game.valid_state():
            _graph[initial_state].append(_graph.setdefault(new_game.to_str(), []))
            generate_state_graph(_graph, new_game)
    return _graph


_VALID_CHARS: frozenset[str] = frozenset(("X", "O", " "))


def calculate_fitness(input_state: str, output_state: str) -> float:
    """Calculate a fitness score for how close ``output_state`` is to a valid move.

    The score measures how well ``output_state`` represents a valid next game
    state reachable from ``input_state`` in a single move.

    Scoring metric:
        For each valid next state reachable from ``input_state``, a weighted
        distance to ``output_state`` is computed by summing per-character costs:

        - **0**: Character at this index matches the target (valid next state).
        - **1**: Valid character (``'X'``, ``'O'``, ``' '``) at this index but
          different from the target character (mismatch, indices 0–9).
        - **2**: Extra character (index >= 10) in ``output_state`` that is a
          valid character.
        - **3**: Invalid character (not ``'X'``, ``'O'``, or ``' '``) at any
          index 0–9.
        - **4**: Extra character (index >= 10) in ``output_state`` that is
          invalid, **or** a missing character (index < 10 present in the target
          but absent from ``output_state``).

        The minimum distance across all valid next states is then converted to a
        fitness score via ``1 / (1 + min_distance)``.

    Args:
        input_state: A 10-character string encoding the current board and last
            player (see ``TicTacToe.to_str()``).
        output_state: The candidate next-state string produced by an evolved
            function.

    Returns:
        A float in the range ``[0.0, 1.0]`` representing the fitness of
        ``output_state``. A value of ``0.0`` is returned when
        ``output_state == input_state`` or when no valid moves are available
        from ``input_state``.
    """
    if output_state == input_state:
        return 0.0

    game = TicTacToe(input_state)
    next_player = game.next_player()

    valid_next_states: list[str] = []
    for position in game.next_move_options():
        candidate = TicTacToe(input_state)
        candidate.move(next_player, position)
        valid_next_states.append(candidate.to_str())

    if not valid_next_states:
        return 0.0

    def _distance(target: str) -> int:
        distance = 0
        output_len = len(output_state)
        for i in range(min(10, output_len)):
            if output_state[i] != target[i]:
                distance += 1 if output_state[i] in _VALID_CHARS else 3
        distance += (10 - output_len) * 4 if output_len < 10 else 0
        for i in range(10, output_len):
            distance += 2 if output_state[i] in _VALID_CHARS else 4
        return distance

    min_distance = min(_distance(target) for target in valid_next_states)
    return 1.0 / (1.0 + min_distance)


if __name__ == "__main__":
    ttt_graph = generate_state_graph()
    print("Number of states:", len(ttt_graph))
