"""The sensor class."""


class Quarternion:
    """The Quarternion class."""

    def __init__(self, w: float = 0.0, x: float = 0.0, y: float = 0.0, z:float = 0.0) -> None:
        """The Quarternion class."""
        self.w = w
        self.x = x
        self.y = y
        self.z = z


class Position:
    """The Position class."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """The Position class."""
        self.x = x
        self.y = y
        self.z = z


class Sensor:
    """A Sensor detects a value in the environment."""

    def __init__(self, v: float = 0.0) -> None:
        """The sensor class."""
        self.value = v


class PointSensor(Sensor):
    """The point sensor is used to measure the value at a point in space."""

    def __init__(self, p: Position, v: float = 0.0) -> None:
        """The sensor class."""
        super().__init__(v)
        self.position = p


class PlateSensor(PointSensor):
    """The plate sensor is used to measure the value on one side of a square plate.
    For example a light sensor that measures the light intensity on one side of a plate.
    A square is used instead of a disc to make the maths easier/faster.
    """

    def __init__(self, s: float, p: Position, q: Quarternion, v: float = 0.0) -> None:
        """The sensor class."""
        super().__init__(p, v)
        self.quarternion = q
        self.side = s


class TubeSensor(PlateSensor):
    """The tube sensor is a plate sensor at the end of a tube (sensor on the inside)
    like a telescope or a camera. The longer the tube the more focused the sensor is."""

    def __init__(self, l: float, dr: float, p: Position, q: Quarternion, v: float = 0.0) -> None:
        """The sensor class."""
        super().__init__(dr, p, q, v)
        self.length = l
