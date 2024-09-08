"""The Genesis Problem.

The genesis problem is a simple simulation of life forms that move around
a 2D ENVIRONMENT_SIZE x ENVIRONMENT_SIZE pixel environment absorbing
nutrients to boost their energy levels. Each pixel in the environment starts
with NUTRIENT_LEVEL energy worth of nutrients. 
Life forms are square LIFEFORM_SIZE x LIFEFORM_SIZE pixels in
size. When they absorb nutrients, their energy level is increased by
the sum of the nutrients underneath them and the nutrient level drops to
zero in those pixels. The life form dies when its energy level drops to zero.

The simulation runs for a maximum of THE_END_OF_TIME ticks or until all
life forms are dead. Each tick, the life forms can move in a random
direction (up, down, left, right, or diagonally) and their energy level
is decremented by TIME_COST. The energy level is also decremented by
MOVEMENT_COST if the life form moves. The energy level is incremented by
the amount of nutrients absorbed.

Two sets of classes are provided. The first set is the base classes
Environment and LifeForm which can efficiently run 'headless' as a
fitness function. The second set is the RenderEnvironment and RenderLifeForm
classes which use the pygame library to display the environment and life
forms as they move around the screen. In the display version, the life forms
are colored blue when they have energy and red when they die. The color
intensity is proportional to the energy level. Nutrients are displayed as
green shades with intensity proportional to the nutrient level.
"""

from __future__ import annotations
from random import choice, randint
from timeit import timeit
from typing import Iterable, Callable, Any
from pygame import quit as pgquit, display, init, QUIT, draw, \
    Rect, surfarray, event, time  # pylint: disable=no-name-in-module
from numpy import full, zeros, int64, uint8, bool_, False_, True_, double
from egppy.genotype.genotype import Genotype


# Constants
TIME_COST = int64(10) # Energy decrement per tick
THE_END_OF_TIME = 10000 # Maximum number of ticks to run the simulation
MOVEMENT_COST = int64(1000) # Energy decrement per movement
ENV_SIZE = 1000 # Environment size in pixels
LIFEFORM_SIZE = 10 # Life form size in pixels
NUTRIENT_LEVEL = int64(1000) # Initial nutrient level
NLFS = 100 # Number of life forms
BLACK = (0, 0, 0) # Black color
ZERO = int64(0)


# Derived Constants
LFS_HALF = LIFEFORM_SIZE // 2 # Half the life form size
ENV_MAX = ENV_SIZE - LFS_HALF # Environment limit
ENV_MIN = LFS_HALF # Environment limit


class LifeForm:
    """A simple life form that can move around the screen
    absorbing nutrients. The life form has a position (x, y) in pixels
    and an integer energy level. The energy level is a measure of the
    life form's health and is decremented by the amount of energy
    expended in actions (movement) and resisting entropy (time). Time
    is measured in ticks."""

    def __init__(self, x: int | None = None, y: int | None = None) -> None:
        self.x = x if x is not None else randint(ENV_MIN, ENV_MAX)
        self.y = y if y is not None else randint(ENV_MIN, ENV_MAX)
        self.energy = int64(2**16)
        self.moved = False  # Previous tick's movement
        self.lifespan = 0  # Number of ticks the life form survived
        def _action() -> bool:
            return choice([True, False])
        self.action_cb: Callable[[], bool] = _action
        def _energy(x: int64) -> None:
            self.energy += x
        self.energy_cb: Callable[[int64], None] = _energy

    def action(self) -> bool:
        """Return True if the life form should move."""
        self.moved = self.action_cb()
        return self.moved

    def move(self) -> None:
        """Move the life form in a random direction and decrement the energy."""
        self.x += choice([-1, 0, 1])
        self.y += choice([-1, 0, 1])

        # Clip the life form's position to the environment limits
        self.x = ENV_MIN if self.x < ENV_MIN else ENV_MAX if self.x > ENV_MAX else self.x
        self.y = ENV_MIN if self.y < ENV_MIN else ENV_MAX if self.y > ENV_MAX else self.y

        # Decrement the energy level.
        # NOTE this does give an advantage to life forms that move diagonally.
        self.energy_cb(-MOVEMENT_COST)

    def update(self, nutrients: int64 = ZERO) -> bool_:
        """Update the life form's energy level based on the passage of
        time & its movement. Update() returns a boolean indicating
        whether the life form is still alive."""
        assert self.energy > ZERO, "Energy level must be > 0 for this call."
        self.energy_cb(nutrients - TIME_COST)
        if self.moved:
            self.move()
        return self.energy > ZERO


class RenderLifeForm(LifeForm):
    """Life form subclass for rendering the life form."""
    blues = tuple((0, 0, blue) for blue in range(0, 256))

    # Callbacks
    cb_pre_move: Callable | None = None
    cb_post_move: Callable | None = None
    cb_pre_update: Callable | None = None
    cb_post_update: Callable | None = None
    cb_died: Callable | None = None

    def __init__(self, x: int | None = None, y: int | None = None) -> None:
        """Initialize the life form with a position and color."""
        super().__init__(x, y)
        self.color: tuple[int, int, int] = (0, 0, 255)
        self.prev_color: tuple[int, int, int] = BLACK

    def move(self) -> None:
        """Wrap the move method with pre and post move callbacks."""
        if self.cb_pre_move is not None:
            self.cb_pre_move()
        super().move()
        if self.cb_post_move is not None:
            self.cb_post_move()

    def update(self, nutrients: int64 = ZERO) -> bool_:
        """Wrap the update method with pre and post update callbacks."""
        if self.cb_pre_update is not None:
            self.cb_pre_update()
        alive = super().update(nutrients)
        if self.cb_post_update is not None:
            self.cb_post_update()
        return alive


class Environment:
    """A 2D environment that contains nutrients and life forms. The
    environment is a ENV_SIZE x ENV_SIZE pixel grid.
    Each pixel contains an
    integer value representing the amount of nutrients present. The
    environment also contains a list of life forms that move around
    the grid absorbing nutrients."""

    def __init__(self, lfs: Iterable[LifeForm] | None = None) -> None:
        self.nutrients = full((ENV_SIZE, ENV_SIZE), NUTRIENT_LEVEL, dtype=int64)
        self.alive = list(lfs) if lfs is not None else [LifeForm() for _ in range(NLFS)]
        self.dead: list[LifeForm] = []
        self.num_ticks = 0
        self.moved = False

    def run(self, tick_limit = THE_END_OF_TIME) -> None:
        """Run the environment until all life forms are dead or 
        the end of time is reached."""
        while self.alive and self.num_ticks < tick_limit and not self.stop_run():
            self.tick()

    def stop_run(self) -> bool_:
        """Return True if the run should stop."""
        return False_

    def tick(self) -> None:
        """Update the environment for one tick."""
        self.num_ticks += 1
        self.update_alive()

    def update_alive(self) -> None:
        """Update the life form's energy level based on the nutrients"""
        for lifeform in self.alive:
            # Since, in this version, the life form consumes all nutrient
            # in the square it occupies when it moves on to them we can
            # assume there are none left if the life form has not moved.
            nutrients = self.nutrients[lifeform.x - LFS_HALF:lifeform.x + LFS_HALF + 1,
                lifeform.y - LFS_HALF:lifeform.y + LFS_HALF + 1
                ].sum() if lifeform.action() else ZERO

            # Update() must be called every tick whilst the lifeform is alive
            # as energy reduces due to entropy every tick.
            still_alive = lifeform.update(nutrients)

            # Only zero the nutrients if there were some to begin with
            if still_alive and nutrients > ZERO:
                self.nutrients[lifeform.x - LFS_HALF:lifeform.x + LFS_HALF + 1,
                    lifeform.y - LFS_HALF:lifeform.y + LFS_HALF + 1] = 0

            # Lifeform ran out of energy and died (circumbed to entropy)
            # Move it from the alive list to the dead list.
            if not still_alive:
                lifeform.lifespan = self.num_ticks
                self.moved = False
                self.dead.append(lifeform)
                self.alive.remove(lifeform)


class RenderEnvironment(Environment):
    """Environment subclass for rendering the environment and life forms."""
    def __init__(self, lfs: Iterable[RenderLifeForm] | None = None) -> None:
        super().__init__(lfs if lfs is not None else [RenderLifeForm() for _ in range(NLFS)])
        init()
        self.screen = display.set_mode((ENV_SIZE, ENV_SIZE))
        display.set_caption(
            f"Genesis - Ticks: 0 - Alive: {len(self.alive)} - Dead: {len(self.dead)}")
        self.starting_colors = zeros((ENV_SIZE, ENV_SIZE, 3), dtype=uint8)
        self.starting_colors[:, :, 1] = uint8(self.nutrients * 255 // NUTRIENT_LEVEL)
        surfarray.blit_array(self.screen, self.starting_colors)

        # Set up the rendering callbacks
        # Prior to moving
        _prev_rect = Rect(0, 0, 0, 0)
        def pre_move(lf: LifeForm) -> None:
            nonlocal _prev_rect
            _prev_rect = Rect(lf.x - LFS_HALF, lf.y - LFS_HALF, LIFEFORM_SIZE, LIFEFORM_SIZE)
        RenderLifeForm.cb_pre_move = pre_move

        # Post moving
        def post_move(_: LifeForm) -> None:
            self.screen.fill(BLACK, _prev_rect)
        RenderLifeForm.cb_post_move = post_move

        # Post updating
        def post_update(lf: RenderLifeForm) -> None:
            lf.prev_color = lf.color
            eidx = lf.energy * int64(192) // int64(2**16) + int64(64)
            idx = eidx if eidx < int64(255) else int64(255)
            lf.color = lf.blues[idx] if lf.energy > 0 else BLACK
            if lf.energy > 0 and (lf.moved or lf.color[2] != lf.prev_color[2]):
                draw.rect(self.screen, lf.color, (lf.x - LFS_HALF, lf.y - LFS_HALF,
                                                    LIFEFORM_SIZE, LIFEFORM_SIZE))
            elif lf.energy <= 0 and lf.color[2] != lf.prev_color[2]:
                lf.prev_color = lf.color
                draw.line(self.screen, (255, 0, 0),
                                    (lf.x - LFS_HALF, lf.y - LFS_HALF),
                                    (lf.x + LFS_HALF, lf.y + LFS_HALF))
                draw.line(self.screen, (255, 0, 0),
                                    (lf.x - LFS_HALF, lf.y + LFS_HALF),
                                    (lf.x + LFS_HALF, lf.y - LFS_HALF))
        RenderLifeForm.cb_post_update = post_update

    def run(self, tick_limit=THE_END_OF_TIME) -> None:
        """Run the environment until all life forms are dead or
        the end of time is reached."""
        super().run(tick_limit)
        while not self.stop_run():
            time.delay(1000)
        pgquit()

    def stop_run(self) -> bool_:
        """Return True if the run should stop."""
        for evt in event.get():
            if evt.type == QUIT:
                return True_
        return False_

    def tick(self) -> None:
        """Update the environment for one tick."""
        super().tick()
        display.set_caption(
            f"Ticks: {self.num_ticks:6d} - Alive: {len(self.alive):4d} - Dead: {len(self.dead):4d}")
        display.flip()


def fitness_function(genotypes: Iterable[Genotype]) -> None:
    """Run the headless version of the simulation with one individual
    life form and set the genotype fitness score.

    The fitness score is the fraction of the maximum number of ticks
    that the life form survived. The maximum number of ticks is
    THE_END_OF_TIME.
    
    The life form starts in the center of the environment and decides
    whether to move or not based on the action callback.    
    """
    for genotype in genotypes:
        lifeform = LifeForm(ENV_SIZE // 2, ENV_SIZE // 2)
        lifeform.action_cb = genotype.func
        environment = Environment([lifeform])
        environment.run()
        genotype.fitness = double(lifeform.lifespan / THE_END_OF_TIME)
        genotype.survivability = genotype.fitness


# This structure is required by Erasmus
EGP_PROBLEM_CONFIG: dict[str, Any] = {
    "creator": "22c23596-df90-4b87-88a4-9409a0ea764f",  # Optional
    "description": __doc__,  # Optional but recommended
    "inputs": [],  # Required
    "outputs": ["bool"],  # Required
    "name": "Genesis",  # Optional but recommended
    "fitness_function": fitness_function,  # Required
    "survivability_function": fitness_function,  # Required
}


if __name__ == "__main__":
    print(timeit("Environment().run()", globals=globals(), number=1))
    print(timeit("RenderEnvironment().run()", globals=globals(), number=1))
