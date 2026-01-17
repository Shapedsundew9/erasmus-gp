"""Find the platform information of the system."""

import platform as pyplatform
from datetime import datetime
from hashlib import sha256

from egpcommon.common import DictTypeAccessor
from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.validator import Validator

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class PlatformInfo(Validator, DictTypeAccessor, CommonObj):
    """Worker platform information.
    i.e. details of the hardware it is running on.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        machine: str | None = None,
        signature: bytes | str | None = None,
        processor: str | None = None,
        platform: str | None = None,
        python_version: str | None = None,
        system: str | None = None,
        release: str | None = None,
        egp_ops: float | None = None,
        created: datetime | str | None = None,
    ) -> None:
        super().__init__()
        machine = pyplatform.machine() if machine is None else machine
        processor = pyplatform.processor() if processor is None else processor
        platform = pyplatform.platform() if platform is None else platform
        python_version = pyplatform.python_version() if python_version is None else python_version
        system = pyplatform.system() if system is None else system
        release = pyplatform.release() if release is None else release
        created = datetime.now().isoformat() if created is None else created
        egp_ops = 0.0 if egp_ops is None else egp_ops
        # TODO: Need to add consistency, regex of strings, etc.

        setattr(self, "machine", machine)
        setattr(self, "signature", signature)
        setattr(self, "processor", processor)
        setattr(self, "platform", platform)
        setattr(self, "python_version", python_version)
        setattr(self, "system", system)
        setattr(self, "release", release)
        setattr(self, "EGPOps", egp_ops)
        setattr(self, "created", created)

        if signature is None:
            setattr(self, "signature", self._generate_signature())
        else:
            setattr(self, "signature", signature)

    def _generate_signature(self) -> bytes:
        """Generate a signature for the platform."""
        hash_obj = sha256(self.machine.encode())
        hash_obj.update(self.processor.encode())
        hash_obj.update(self.platform.encode())
        hash_obj.update(self.python_version.encode())
        hash_obj.update(self.system.encode())
        hash_obj.update(self.release.encode())
        return hash_obj.digest()

    @property
    def created(self) -> str:
        """Get the created."""
        return self._created

    @created.setter
    def created(self, value: datetime | str) -> None:
        """The time the platform information was first created."""
        if isinstance(value, datetime):
            value = value.isoformat()
        self._created = value

    @property
    def egp_ops(self) -> float:
        """Get the EGPOps."""
        return self._egp_ops

    @egp_ops.setter
    def egp_ops(self, value: float) -> None:
        """An Erasmus GP specific performance metric directly proportional to the processing
        power of the system for typical Erasmus GP tasks in units of notional operations
        per second. Bigger = faster.
        """
        if not self._is_float("EGPOps", value):
            raise ValueError(f"EGPOps must be a float, but is {type(value)}")
        self._egp_ops = value

    @property
    def machine(self) -> str:
        """Get the machine."""
        return self._machine

    @machine.setter
    def machine(self, value: str) -> None:
        """The machine  type, e.g. 'i386'. An empty string if the value cannot be determined."""
        if not self._is_string("machine", value):
            raise ValueError(f"machine must be a string, but is {type(value)}")
        if not self._is_length("machine", value, 0, 128):
            raise ValueError(f"machine length must be between 0 and 128, but is {len(value)}")
        self._machine = value

    @property
    def platform(self) -> str:
        """Get the platform."""
        return self._platform

    @platform.setter
    def platform(self, value: str) -> None:
        """The underlying platform with as much useful information as possible.
        The output is intended to be human readable rather than machine parseable.
        """
        if not self._is_string("platform", value):
            raise ValueError(f"platform must be a string, but is {type(value)}")
        if not self._is_length("platform", value, 0, 1024):
            raise ValueError(f"platform length must be between 0 and 1024, but is {len(value)}")
        self._platform = value

    @property
    def processor(self) -> str:
        """Get the processor."""
        return self._processor

    @processor.setter
    def processor(self, value: str) -> None:
        """The (real) processor name, e.g. 'amdk6'.
        An empty string if the value cannot be determined.
        """
        if not self._is_string("processor", value):
            raise ValueError(f"processor must be a string, but is {type(value)}")
        if not self._is_length("processor", value, 0, 128):
            raise ValueError(f"processor length must be between 0 and 128, but is {len(value)}")
        self._processor = value

    @property
    def python_version(self) -> str:
        """Get the python version."""
        return self._python_version

    @python_version.setter
    def python_version(self, value: str) -> None:
        """The Python version as string 'major.minor.patchlevel'."""
        if not self._is_string("python_version", value):
            raise ValueError(f"python_version must be a string, but is {type(value)}")
        if not self._is_length("python_version", value, 0, 64):
            raise ValueError(f"python_version length must be between 0 and 64, but is {len(value)}")
        self._python_version = value

    @property
    def release(self) -> str:
        """Get the release."""
        return self._release

    @release.setter
    def release(self, value: str) -> None:
        """The system’s release, e.g. '2.2.0' or 'NT'.
        An empty string if the value cannot be determined.
        """
        if not self._is_string("release", value):
            raise ValueError(f"release must be a string, but is {type(value)}")
        if not self._is_length("release", value, 0, 64):
            raise ValueError(f"release length must be between 0 and 64, but is {len(value)}")
        self._release = value

    @property
    def signature(self) -> bytes:
        """Get the signature."""
        return self._signature

    @signature.setter
    def signature(self, value: bytes | str) -> None:
        """The SHA256 signature of the platform data."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        if not self._is_sha256("signature", value):
            raise ValueError("signature must be a valid SHA256 digest")
        if self._generate_signature() != value:
            raise ValueError("Signature does not match the platform.")
        self._signature = value

    @property
    def system(self) -> str:
        """Get the system."""
        return self._system

    @system.setter
    def system(self, value: str) -> None:
        """The system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'.
        An empty string if the value cannot be determined.
        """
        if not self._is_string("system", value):
            raise ValueError(f"system must be a string, but is {type(value)}")
        if not self._is_length("system", value, 0, 64):
            raise ValueError(f"system length must be between 0 and 64, but is {len(value)}")
        self._system = value
