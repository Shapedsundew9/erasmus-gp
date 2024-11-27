# The Tic-Tac-Toe Problem

[Tic-Tac-Toe](https://en.wikipedia.org/wiki/Tic-tac-toe), TTT, is a good way to explore different evolutionary paths as it can be implemented in may different ways quickly and reliably. In this case a TTT agent is designed such that the output by one player agent is the input to the opposition player agent. A judge records the state of the board and determines if there is a win/loss or draw after each output (and before the next input). With this architecture there are 4 basic designs of agent input interface (and hence output).

1. Full board state i.e. 9 tertiary values representing the state of the board.
2. Implicit empty grid positions i.e. 0 to 9 coorindates each with a binary value specifying the player (**O** or **X**)
3. Implicit player grid positions i.e. a container of positions for player **O** and a container of positions for player **X**
4. Grid memory i.e. a single position input identifying the position of the other players play which requires a record of plays to be stored.

## Full Grid State

There are several sub-design options:

1. Linear grid state where the index of the state position is (column, row) = divmod(index, 3)
2. 2D grid: i.e. 3 containers (columns) of 3 ordered states (rows)
3. Key: State mapping where the key represents a set of grid coordinates

1 & 2 can both be implemented with a list, tuple or individual parameters (states) and 3 can be implemented with a dict (making 7 variants). In all cases the state may be represented almost infinite ways but we will restrict ourselves to hitting the basic python types:

- int where -1 = **O**, 0 = empty, 1 = **X**
- str with the characters "O", "" or "X"
- bool | None where True = **O**, None = empty, False = **X**
- float where -INF = **O**, NAN = empty, +INF = **X**

The key in the dict type can also be represented an infinite number of ways. In this case:

- str as a letter A - I represented a specific cell on the grid
- int as a index 0 to 8 where (column, row) = divmod(index, 3)
- tuple[int, int] coordinates as (column, row)

So that gives us 3 \* 2 \* 4 + 3 \* 4 = 36 different TTT grid state representation designs. There is also a special case for 1 where the linear grid state can be implemented as a string of "O", "-" and "X".

So 37 cases in total.

## Implict Empty Grid

The implicit empty grid interface only specifies the occupied positions of the grid and thus required 2 bits of information, position and binary state (**O** or **X**). As with the full grid state design there are a few basic design choices:

1. Sequence of position-states
2. Mapping of position:states

1 can be implemented as a list, tuple or set and there is a special str case too (see below), 2 can be implemented with a dict. position-states can be implemented:

- The characters A to I in uppercase for one player and lower case for the other.
- A tuple[str, bool] where str is a letter A to I specifying the position and bool is the player.
- A tuple [int, int, bool] = (column, row, player)

position:states can be implemented:

- str:bool where str is a letter A to I specifying the position and bool is the player.
- tuple[int, int]:bool where the key is (column, row) and the value the player.

The special case is a 0 to 9 length string with the characters A to I in uppercase for one player and lower case for the other. The order of the letters does not matter (and randomising the order should be part of the fitness function.)

In total that makes 3 \* 3 + 1 \* 2 + 1 = 12

## Implicit Empty Grid & Player

TBD

## Memory

TBD


