"""The sensor ABC classes."""
from __future__ import annotations
from abc import ABC, abstractmethod


class QuarternionABC(ABC):
    """The Quarternion class."""

    @abstractmethod
    def __init__(self, w: float = 0.0, x: float = 0.0, y: float = 0.0, z:float = 0.0) -> None:
        """The Quarternion class."""
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    @abstractmethod
    def __abs__(self) -> QuarternionABC:
        """Return the magnitude of the quarternion."""

    @abstractmethod
    def __add__(self, other: QuarternionABC) -> QuarternionABC:
        """Add two quarternions together."""

    @abstractmethod
    def __neg__(self) -> QuarternionABC:
        """Negate the quarternion."""

    @abstractmethod
    def __sub__(self, other: QuarternionABC) -> QuarternionABC:
        """Subtract two quarternions together."""

    @abstractmethod
    def abs(self) -> QuarternionABC:
        """Return the magnitude of the quarternion."""

    @abstractmethod
    def add(self, other: QuarternionABC) -> QuarternionABC:
        """Add a quarternion to this quarternion."""

    @abstractmethod
    def neg(self) -> QuarternionABC:
        """Negate the quarternion."""

    @abstractmethod
    def sub(self, other: QuarternionABC) -> QuarternionABC:
        """Subtract a quarternion from this quarternion."""


class PositionABC(ABC):
    """The Position class."""

    @abstractmethod
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """The Position class."""
        self.x = x
        self.y = y
        self.z = z

    @abstractmethod
    def __abs__(self) -> PositionABC:
        """Return the magnitude of the position."""

    @abstractmethod
    def __add__(self, other: PositionABC) -> PositionABC:
        """Add two positions together."""

    @abstractmethod
    def __div__(self, other: float) -> PositionABC:
        """Divide the position by a scalar."""

    @abstractmethod
    def __mul__(self, other: float) -> PositionABC:
        """Multiply the position by a scalar."""

    @abstractmethod
    def __neg__(self) -> PositionABC:
        """Negate the position."""

    @abstractmethod
    def __sub__(self, other: PositionABC) -> PositionABC:
        """Subtract two positions together."""

    @abstractmethod
    def abs(self) -> PositionABC:
        """Return the magnitude of the position."""

    @abstractmethod
    def add(self, other: PositionABC) -> PositionABC:
        """Add a position to this position."""

    @abstractmethod
    def div(self, other: float) -> PositionABC:
        """Divide the position by a scalar."""

    @abstractmethod
    def mul(self, other: float) -> PositionABC:
        """Multiply the position by a scalar."""

    @abstractmethod
    def neg(self) -> PositionABC:
        """Negate the position."""

    @abstractmethod
    def sub(self, other: PositionABC) -> PositionABC:
        """Subtract a position from this position."""
