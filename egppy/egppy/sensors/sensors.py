"""The sensor class."""
from sensors_abc import QuarternionABC, PositionABC


class Quarternion(QuarternionABC):
    """The Quarternion class."""

    def __init__(self, w: float = 0.0, x: float = 0.0, y: float = 0.0, z:float = 0.0) -> None:
        """The Quarternion class."""
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __abs__(self) -> QuarternionABC:
        """Return the magnitude of the quarternion."""
        return Quarternion(abs(self.w), abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, other: QuarternionABC) -> QuarternionABC:
        """Add two quarternions together."""
        return Quarternion(self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self) -> QuarternionABC:
        """Negate the quarternion."""
        return Quarternion(-self.w, -self.x, -self.y, -self.z)

    def __sub__(self, other: QuarternionABC) -> QuarternionABC:
        """Subtract two quarternions together."""
        return Quarternion(self.w - other.w, self.x - other.x, self.y - other.y, self.z - other.z)

    def abs(self) -> QuarternionABC:
        """Set the quarternion to its absolutes and return self."""
        self.w = abs(self.w)
        self.x = abs(self.x)
        self.y = abs(self.y)
        self.z = abs(self.z)
        return self

    def add(self, other: QuarternionABC) -> QuarternionABC:
        """Add a quarternion to this quarternion."""
        self.w += other.w
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def neg(self) -> QuarternionABC:
        """Negate the quarternion."""
        self.w = -self.w
        self.x = -self.x
        self.y = -self.y
        self.z = -self.z
        return self

    def sub(self, other: QuarternionABC) -> QuarternionABC:
        """Subtract a quarternion from this quarternion."""
        self.w -= other.w
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self


class Position(PositionABC):
    """The Position class."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """The Position class."""
        self.x = x
        self.y = y
        self.z = z

    def __abs__(self) -> PositionABC:
        """Return the magnitude of the position."""
        return Position(abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, other: PositionABC) -> PositionABC:
        """Add two positions together."""
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)

    def __div__(self, other: float) -> PositionABC:
        """Divide the position by a scalar."""
        return Position(self.x / other, self.y / other, self.z / other)

    def __mul__(self, other: float) -> PositionABC:
        """Multiply the position by a scalar."""
        return Position(self.x * other, self.y * other, self.z * other)

    def __neg__(self) -> PositionABC:
        """Negate the position."""
        return Position(-self.x, -self.y, -self.z)

    def __sub__(self, other: PositionABC) -> PositionABC:
        """Subtract two positions together."""
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def abs(self) -> PositionABC:
        """Return the magnitude of the position."""
        self.x = abs(self.x)
        self.y = abs(self.y)
        self.z = abs(self.z)
        return self

    def add(self, other: PositionABC) -> PositionABC:
        """Add a position to this position."""
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def div(self, other: float) -> PositionABC:
        """Divide the position by a scalar."""
        self.x /= other
        self.y /= other
        self.z /= other
        return self

    def mul(self, other: float) -> PositionABC:
        """Multiply the position by a scalar."""
        self.x *= other
        self.y *= other
        self.z *= other
        return self

    def neg(self) -> PositionABC:
        """Negate the position."""
        self.x = -self.x
        self.y = -self.y
        self.z = -self.z
        return self

    def sub(self, other: PositionABC) -> PositionABC:
        """Subtract a position from this position."""
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self


class Sensor:
    """A Sensor detects a value in the environment that is position invariant.
    For example barometric pressure could be considered to be the same at all points
    in the environment.
    """

    def __init__(self, v: float = 0.0) -> None:
        """The sensor class."""
        self.value = v


class PointSensor(Sensor):
    """The point sensor is used to measure the value at a point in space.
    For example a temperature sensor that measures the temperature at a point in space."""

    def __init__(self, p: PositionABC | None = None,
            po: PositionABC | None = None, v: float = 0.0) -> None:
        """Initialization of the point sensor.
        All point sensors have a position in space and an offset from that position.
        This allows sensors to be grouped together in a single object with a common position.
        """
        super().__init__(v)
        self.position = Position() if p is None else p
        self.p_offset = Position() if po is None else po

    def location(self) -> PositionABC:
        """Return the location (position + offset) of the sensor."""
        return self.position + self.p_offset


class PlateSensor(PointSensor):
    """The plate sensor is used to measure the value on one side of a square plate.
    For example a light sensor that measures the light intensity on one side of a plate.
    A square is used instead of a disc to make the maths easier/faster.
    """

    def __init__(self, s: float = 1E-9, p: Position | None = None, po: Position | None = None,
        q: Quarternion | None = None, qo: Quarternion | None = None, v: float = 0.0) -> None:
        """The sensor class."""
        super().__init__(p, po, v)
        self.quarternion = Quarternion() if q is None else q
        self.q_offset = Quarternion() if qo is None else qo
        self.side = s

    def orientation(self) -> QuarternionABC:
        """Return the orientation (quarternion + offset) of the sensor."""
        return self.quarternion + self.q_offset

    def pose(self) -> tuple[PositionABC, QuarternionABC]:
        """Return the pose (location, orientation) of the sensor."""
        return self.location(), self.orientation()


class TubeSensor(PlateSensor):
    """The tube sensor is a plate sensor at the end of a tube (sensor on the inside)
    like a telescope or a camera. The longer the tube the more focused the sensor is."""

    def __init__(self, l: float = 1E-9, s: float = 1E-9, p: Position | None = None,
        po: Position | None = None, q: Quarternion | None = None,
        qo: Quarternion | None = None, v: float = 0.0) -> None:
        """The sensor class."""
        super().__init__(s, p, po, q, qo, v)
        self.length = l


class SensorGroup:
    """A sensor group is a collection of sensors that all have the same position.
    This allows the sensors to be moved together."""

    def __init__(self, p: Position | None = None, s: list[PointSensor] | None = None) -> None:
        """The sensor class."""
        self.position = Position() if p is None else p
        self.sensors = [] if s is None else s
        for sensor in self.sensors:
            sensor.position = self.position

# Need to rethink: What to allow groups of groups of groups etc.
# Class needs to be recursive which means offset must be applied at each level and
# sensors accessed through the group at each level.

class AlignedSensorGroup(SensorGroup):
    """An aligned sensor group is a collection of sensors that all have the same position
    and orientation. This allows the sensors to be moved together."""

    def __init__(self, p: Position, q: Quarternion, s: list[PlateSensor]) -> None:
        """Initialization of the aligned sensor group."""
        super().__init__(p, s)
        self.quarternion = q
        for sensor in self.sensors:
            sensor.quarternion = self.quarternion