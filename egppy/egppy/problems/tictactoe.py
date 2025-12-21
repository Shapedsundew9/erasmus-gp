"""Tic-Tac-Toe game implementations.
See docs/tic-tac-toe.md for more information.
"""


class TicTacToe:
    """Tic-Tac-Toe game."""

    def __init__(self, state: str = "         O") -> None:
        """Initialize the game."""
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
        """Return the state of the game as a string."""
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
