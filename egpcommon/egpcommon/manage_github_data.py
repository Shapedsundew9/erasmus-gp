"""Release data management functions for GitHub.

These functions manage the data files in a GitHub release for the Erasmus GP project.
Data files (codons.json, types_def.json and their .sig counterparts) are stored as
assets on a GitHub release tagged ``latest-data``.

``upload_data()``
    Requires authentication via the ``RELEASE_DATA_MANAGER_TOKEN`` environment variable.
    Compares local .sig file timestamps against remote ones, uploading only when the
    local data is newer. Old assets with the same name are deleted before uploading.

``download_data()``
    Uses public (unauthenticated) access to the GitHub release. Compares local .sig file
    timestamps against remote ones, downloading only when the remote data is newer. Network
    failures are logged as warnings and local data is used as a fallback.

``download_data()`` should be called as a pre-init step before Gene Pool initialisation
to ensure the latest data is always available.
"""

from datetime import datetime
from json import loads
from logging import INFO
from os import getenv, makedirs
from os.path import dirname, exists, join
from typing import Any

from requests import ConnectionError as RequestsConnectionError
from requests import HTTPError, RequestException, Timeout
from requests import delete as requests_delete
from requests import get, post

from egpcommon.egp_log import Logger, egp_logger
from egpcommon.security import load_signature_data

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_INFO: bool = _logger.isEnabledFor(level=INFO)

# --- CONFIGURATION ---
REPO_NAME = "Shapedsundew9/erasmus-gp"  # Public repo
TAG_NAME = "latest-data"
RELEASE_TITLE = "Latest Data Build"

# GitHub API base URL
_API_BASE = f"https://api.github.com/repos/{REPO_NAME}"
_UPLOAD_BASE = f"https://uploads.github.com/repos/{REPO_NAME}"

# Files to upload/download
JSON_FILES: tuple[str, ...] = ("codons.json", "types_def.json")
SIG_FILES: tuple[str, ...] = tuple(f + ".sig" for f in JSON_FILES)
ALL_FILES: tuple[str, ...] = JSON_FILES + SIG_FILES
FILES_FOLDER: str = join(dirname(__file__), "..", "..", "egppy", "egppy", "data")
# ---------------------


def _get_github_token() -> str:
    """Retrieve the GitHub token from the environment.

    Returns:
        The GitHub token string.

    Raises:
        EnvironmentError: If the token environment variable is not set.
    """
    token = getenv("RELEASE_DATA_MANAGER_TOKEN")
    if not token:
        raise EnvironmentError(
            "RELEASE_DATA_MANAGER_TOKEN environment variable is not set. "
            "This is required for upload operations."
        )
    return token


def _auth_headers(token: str) -> dict[str, str]:
    """Build authorised request headers.

    Args:
        token: GitHub personal access token.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }


def _get_or_create_release(token: str) -> dict[str, Any]:
    """Get the existing release for TAG_NAME or create one.

    Args:
        token: GitHub personal access token.

    Returns:
        Release JSON dict from the GitHub API.

    Raises:
        HTTPError: If the API request fails.
    """
    headers = _auth_headers(token)

    # Try to fetch existing release by tag
    resp = get(f"{_API_BASE}/releases/tags/{TAG_NAME}", headers=headers, timeout=30)
    if resp.status_code == 200:
        return resp.json()

    # Create a new release
    _logger.info("Release with tag '%s' not found, creating it.", TAG_NAME)
    payload = {
        "tag_name": TAG_NAME,
        "name": RELEASE_TITLE,
        "body": "Automatically managed data release.",
        "draft": False,
        "prerelease": False,
    }
    resp = post(f"{_API_BASE}/releases", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _remote_sig_data(release: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Download and parse remote .sig assets from a release.

    Args:
        release: GitHub release JSON dict containing an ``assets`` list.

    Returns:
        Mapping of asset name (e.g. ``codons.json.sig``) to the full parsed
        sig data dict (containing ``file_hash``, ``timestamp``, etc.).
    """
    result: dict[str, dict[str, Any]] = {}
    for asset in release.get("assets", []):
        name: str = asset["name"]
        if name.endswith(".sig"):
            download_url = asset["browser_download_url"]
            try:
                resp = get(download_url, timeout=30)
                resp.raise_for_status()
                result[name] = resp.json()
            except RequestException:
                _logger.warning("Failed to download remote sig asset: %s", name)
    return result


def _parse_sig_timestamp(sig_data: dict[str, Any]) -> datetime | None:
    """Parse the ISO-format timestamp from a .sig data dict.

    Args:
        sig_data: Parsed contents of a .sig file.

    Returns:
        A timezone-aware datetime, or ``None`` if the timestamp is missing or
        cannot be parsed.
    """
    ts_str = sig_data.get("timestamp")
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return None


def _local_sig_data(sig_filename: str) -> dict[str, Any] | None:
    """Load the full sig data dict from a local .sig file.

    Args:
        sig_filename: Name of the .sig file (relative to FILES_FOLDER).

    Returns:
        The parsed sig data dict, or ``None`` if the file does not exist or
        cannot be read.
    """
    path = join(FILES_FOLDER, sig_filename)
    if not exists(path):
        return None
    try:
        return load_signature_data(path)
    except (ValueError, FileNotFoundError):
        return None


def upload_data() -> None:
    """Upload local data files to the GitHub release.

    Steps:
        1. Authenticate using ``RELEASE_DATA_MANAGER_TOKEN``.
        2. Get or create the release tagged ``latest-data``.
        3. Compare local .sig timestamps with remote ones; skip files where the
           remote version is the same or newer.
        4. Delete stale remote assets with the same name.
        5. Upload new files.
        6. Log the ``curl`` download command for each uploaded file.

    Raises:
        EnvironmentError: If the GitHub token is not set.
        HTTPError: If any GitHub API call fails.
    """
    token = _get_github_token()
    headers = _auth_headers(token)
    release = _get_or_create_release(token)
    release_id = release["id"]
    remote_sigs = _remote_sig_data(release)

    # Determine which files need uploading by comparing timestamps
    files_to_upload: list[str] = []
    for sig_file in SIG_FILES:
        local_data = _local_sig_data(sig_file)
        if local_data is None:
            _logger.warning("Local sig file missing, skipping: %s", sig_file)
            continue

        local_ts = _parse_sig_timestamp(local_data)
        remote_data = remote_sigs.get(sig_file)
        remote_ts = _parse_sig_timestamp(remote_data) if remote_data else None

        if local_ts is not None and (remote_ts is None or local_ts > remote_ts):
            json_file = sig_file.removesuffix(".sig")
            files_to_upload.extend([json_file, sig_file])
        else:
            if _LOG_INFO:
                _logger.info("Remote is same or newer, skipping upload: %s", sig_file)

    if not files_to_upload:
        _logger.info("All files are up to date. Nothing to upload.")
        return

    # Build a lookup of existing asset names to IDs for deletion
    existing_assets: dict[str, int] = {
        asset["name"]: asset["id"] for asset in release.get("assets", [])
    }

    for filename in files_to_upload:
        filepath = join(FILES_FOLDER, filename)
        if not exists(filepath):
            _logger.warning("Local file not found, skipping: %s", filepath)
            continue

        # Delete old asset if it exists
        if filename in existing_assets:
            asset_id = existing_assets[filename]
            del_resp = requests_delete(
                f"{_API_BASE}/releases/assets/{asset_id}", headers=headers, timeout=30
            )
            del_resp.raise_for_status()
            _logger.info("Deleted old asset: %s (id=%d)", filename, asset_id)

        # Upload new asset
        upload_url = f"{_UPLOAD_BASE}/releases/{release_id}/assets?name={filename}"
        upload_headers = {**headers, "Content-Type": "application/octet-stream"}
        with open(filepath, "rb") as f:
            up_resp = post(upload_url, headers=upload_headers, data=f, timeout=120)
        up_resp.raise_for_status()
        _logger.info("Uploaded: %s", filename)

        # Log the curl download command
        download_url = f"https://github.com/{REPO_NAME}/releases/download/{TAG_NAME}/{filename}"
        _logger.info("curl -L -o %s %s", filename, download_url)


def download_data() -> bool:
    """Download data files from the GitHub release if remote versions are newer.

    Uses public (unauthenticated) access. Compares local .sig file timestamps
    with remote ones and only downloads files where the remote timestamp is
    strictly newer than the local one.  Network failures are handled
    gracefully — a warning is logged and local data is used as a fallback.

    Returns:
        True if any files were downloaded, False otherwise.
    """
    base_url = f"https://github.com/{REPO_NAME}/releases/download/{TAG_NAME}"

    # First, fetch remote .sig files to compare timestamps
    remote_sigs: dict[str, dict[str, Any]] = {}
    for sig_file in SIG_FILES:
        url = f"{base_url}/{sig_file}"
        try:
            resp = get(url, timeout=30)
            resp.raise_for_status()
            remote_sigs[sig_file] = loads(resp.text)
        except (RequestsConnectionError, Timeout) as exc:
            _logger.warning(
                "Network error fetching remote sig file %s: %s. Using local data.", sig_file, exc
            )
            return False
        except (HTTPError, RequestException, ValueError) as exc:
            _logger.warning(
                "Failed to fetch remote sig file %s: %s. Using local data.", sig_file, exc
            )
            return False

    # Determine which files need downloading by comparing timestamps
    files_to_download: list[str] = []
    for sig_file in SIG_FILES:
        remote_data = remote_sigs.get(sig_file)
        remote_ts = _parse_sig_timestamp(remote_data) if remote_data else None

        local_data = _local_sig_data(sig_file)
        local_ts = _parse_sig_timestamp(local_data) if local_data else None

        if remote_ts is not None and (local_ts is None or remote_ts > local_ts):
            json_file = sig_file.removesuffix(".sig")
            files_to_download.extend([json_file, sig_file])
        else:
            if _LOG_INFO:
                _logger.info("Local is same or newer, skipping download: %s", sig_file)

    if not files_to_download:
        _logger.info("All local files are up to date. Nothing to download.")
        return False

    # Ensure destination folder exists (important for fresh environments)
    makedirs(FILES_FOLDER, exist_ok=True)

    # Download the files
    downloaded = False
    for filename in files_to_download:
        url = f"{base_url}/{filename}"
        filepath = join(FILES_FOLDER, filename)
        try:
            resp = get(url, timeout=60)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
            _logger.info("Downloaded: %s", filename)
            downloaded = True
        except (RequestsConnectionError, Timeout) as exc:
            _logger.warning(
                "Network error downloading %s: %s. Using local data if available.",
                filename,
                exc,
            )
        except (HTTPError, RequestException) as exc:
            _logger.warning(
                "Failed to download %s: %s. Using local data if available.", filename, exc
            )

    return downloaded


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Manage Erasmus GP data files on GitHub releases.")
    parser.add_argument(
        "action",
        choices=["upload", "download", "sync"],
        help="Action to perform: upload, download, or sync (both).",
    )
    args = parser.parse_args()

    if args.action in ("download", "sync"):
        download_data()
    if args.action in ("upload", "sync"):
        upload_data()
