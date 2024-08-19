"""Problems Module.

The problems module provides an interface to searching for and loading problems.
"""
from os.path import exists, join
from os import access, W_OK, chdir, getcwd
from sys import exit as sys_exit
from pathlib import Path
from requests import get, Response
from egppy.common.security import load_signed_json
from egppy.worker.configuration import WorkerConfig
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.problems.configuration import ProblemConfig


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def load_problems(config: WorkerConfig) -> dict[bytes, ProblemConfig]:
    """Load the problems from the configuration."""
    # Check the problem data folder
    directory_path: str = config["problem_folder"]
    if exists(directory_path):
        if not access(directory_path, W_OK):
            print(f"The 'problem_folder' directory '{directory_path}' exists but is not writable.")
            sys_exit(1)
    else:
        # Create the directory if it does not exist
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
        except PermissionError as permission_error:
            print(f"The 'problem_folder' directory '{directory_path}' "
                  f"does not exist and cannot be created: {permission_error}")
            sys_exit(1)

    # Store the current working directory & change to where Erasmus GP keeps its data
    cwd: str = getcwd()
    chdir(directory_path)

    # Check the verified problem definitions file
    prob_defs_file: str = join(directory_path, "egp_problems.json")
    prob_defs_file_exists: bool = exists(prob_defs_file)
    if not prob_defs_file_exists:
        _logger.info("The egp_problems.json does not exist in %s. Pulling from %s",
                     directory_path, config['problem_definitions'])
        # TODO: Verify the size of the download before downloading
        response: Response = get(config["problem_definitions"], timeout=30, allow_redirects=False)
        if prob_defs_file_exists := response.status_code == 200:
            with open(prob_defs_file, "wb") as file:
                file.write(response.content)
            _logger.info("File 'egp_problems.json' downloaded successfully.")
        else:
            _logger.warning("Failed to download the file. Status code: %s.", response.status_code)

    # Load the problems definitions file if it exists
    with open(prob_defs_file, "r", encoding="utf8") as file_ptr:
        prob_defs_json = load_signed_json(file_ptr)
    assert isinstance(prob_defs_json, list), "Problem definitions file is not a list."
    assert prob_defs_json, "Problem definitions file is empty."
    assert all(isinstance(p, dict) for p in prob_defs_json), \
        "Problem definitions are not dictionaries."

    chdir(cwd)
    return {p["git_hash"]: ProblemConfig(**p) for p in prob_defs_json}


def load_problem(config: WorkerConfig, git_hash: bytes) -> ProblemConfig:
    """Load a problem from the configuration."""
    return load_problems(config)[git_hash]
