"""Find the platform information of the system."""
from hashlib import sha256
import platform as pyplatform
from datetime import datetime
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.common.common import DictTypeAccessor, Validator


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class PlatformInfo(Validator, DictTypeAccessor):
    """Worker plaftorm information.
    i.e. details of the hardware it is running on.
    
    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(self,
        machine: str | None = None,
        signature: bytes | str | None = None,
        processor: str | None = None,
        platform: str | None = None,
        python_version: str | None = None,
        system: str | None = None,
        release: str | None = None,
        egp_ops: float | None = None,
        created: datetime | str | None = None
    ) -> None:
        super().__init__()
        machine =  pyplatform.machine() if machine is None else machine
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
    def machine(self) -> str:
        """Get the machine."""
        return self._machine

    @machine.setter
    def machine(self, value: str) -> None:
        """The machine  type, e.g. 'i386'. An empty string if the value cannot be determined."""
        self._is_string("machine", value)
        self._is_length("machine", value, 0, 128)
        self._machine = value

    @property
    def signature(self) -> bytes:
        """Get the signature."""
        return self._signature

    @signature.setter
    def signature(self, value: bytes | str) -> None:
        """The SHA256 signature of the platform data."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        self._is_sha256("signature", value)
        assert self._generate_signature() == value, "Signature does not match the platform."
        self._signature = value

    @property
    def processor(self) -> str:
        """Get the processor."""
        return self._processor

    @processor.setter
    def processor(self, value: str) -> None:
        """The (real) processor name, e.g. 'amdk6'.
        An empty string if the value cannot be determined.
        """
        self._is_string("processor", value)
        self._is_length("processor", value, 0, 128)
        self._processor = value

    @property
    def platform(self) -> str:
        """Get the platform."""
        return self._platform

    @platform.setter
    def platform(self, value: str) -> None:
        """The underlying platform with as much useful information as possible. 
        The output is intended to be human readable rather than machine parseable.
        """
        self._is_string("platform", value)
        self._is_length("platform", value, 0, 1024)
        self._platform = value

    @property
    def python_version(self) -> str:
        """Get the python version."""
        return self._python_version

    @python_version.setter
    def python_version(self, value: str) -> None:
        """The Python version as string 'major.minor.patchlevel'."""
        self._is_string("python_version", value)
        self._is_length("python_version", value, 0, 64)
        self._python_version = value

    @property
    def system(self) -> str:
        """Get the system."""
        return self._system

    @system.setter
    def system(self, value: str) -> None:
        """The system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'.
        An empty string if the value cannot be determined.
        """
        self._is_string("system", value)
        self._is_length("system", value, 0, 64)
        self._system = value

    @property
    def release(self) -> str:
        """Get the release."""
        return self._release

    @release.setter
    def release(self, value: str) -> None:
        """The system’s release, e.g. '2.2.0' or 'NT'.
        An empty string if the value cannot be determined.
        """
        self._is_string("release", value)
        self._is_length("release", value, 0, 64)
        self._release = value

    @property
    def egp_ops(self) -> float:
        """Get the EGPOps."""
        return self._egp_ops

    @egp_ops.setter
    def egp_ops(self, value: float) -> None:
        """An Erasmus GP specific performance metric directly proportional to the prcoessing 
        power of the system for typical Erasmus GP tasks in units of notional operations
        per second. Bigger = faster.
        """
        self._is_float("EGPOps", value)
        self._egp_ops = value

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
