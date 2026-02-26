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

    The compact string representation (see :meth:`to_str`) is used **externally**
    whenever an immutable, hashable key is needed – for example as a node
    identifier in the state graph produced by :func:`generate_state_graph`.
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
            that individual cell updates during :meth:`move` are O(1) mutations
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
        :func:`generate_state_graph`) where an immutable, hashable representation
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


if __name__ == "__main__":
    ttt_graph = generate_state_graph()
    print("Number of states:", len(ttt_graph))
