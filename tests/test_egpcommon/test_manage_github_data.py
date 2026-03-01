"""Unit tests for egpcommon.manage_github_data.

Tests cover upload_data(), download_data(), and supporting helper functions.
All HTTP interactions are mocked to avoid real network calls.
"""

from json import dumps
from os import path
from os.path import join
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch

from requests import ConnectionError as ReqConnError

from egpcommon.manage_github_data import (
    ALL_FILES,
    JSON_FILES,
    SIG_FILES,
    _get_github_token,
    _local_sig_data,
    _parse_sig_timestamp,
    _remote_sig_data,
    download_data,
    upload_data,
)

# Reusable timestamp constants
_TS_OLD = "2026-01-01T00:00:00+00:00"
_TS_NEW = "2026-02-28T12:00:00+00:00"


def _make_sig(timestamp: str = _TS_OLD, file_hash: str = "abc123") -> dict:
    """Build a minimal sig data dict for testing."""
    return {
        "file_hash": file_hash,
        "signature": "sig",
        "algorithm": "Ed25519",
        "creator_uuid": "uuid",
        "timestamp": timestamp,
    }


class TestGetGitHubToken(TestCase):
    """Tests for _get_github_token()."""

    @patch.dict("os.environ", {"RELEASE_DATA_MANAGER_TOKEN": "test-token-123"})
    def test_returns_token_when_set(self) -> None:
        """Token is returned when the environment variable is set."""
        self.assertEqual(_get_github_token(), "test-token-123")

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_when_token_missing(self) -> None:
        """EnvironmentError is raised when the token is not set."""
        with self.assertRaises(EnvironmentError):
            _get_github_token()


class TestParseSigTimestamp(TestCase):
    """Tests for _parse_sig_timestamp()."""

    def test_parses_valid_iso_timestamp(self) -> None:
        """Returns a datetime for a valid ISO timestamp."""
        result = _parse_sig_timestamp({"timestamp": _TS_OLD})
        self.assertIsNotNone(result)

    def test_returns_none_for_missing_timestamp(self) -> None:
        """Returns None when the timestamp key is absent."""
        self.assertIsNone(_parse_sig_timestamp({}))

    def test_returns_none_for_invalid_timestamp(self) -> None:
        """Returns None when the timestamp value is not valid ISO."""
        self.assertIsNone(_parse_sig_timestamp({"timestamp": "not-a-date"}))


class TestLocalSigData(TestCase):
    """Tests for _local_sig_data()."""

    def test_returns_none_for_missing_file(self) -> None:
        """Returns None when the sig file does not exist."""
        with patch("egpcommon.manage_github_data.FILES_FOLDER", "/nonexistent"):
            result = _local_sig_data("codons.json.sig")
        self.assertIsNone(result)

    def test_returns_data_for_existing_file(self) -> None:
        """Returns the parsed sig data dict from a valid local .sig file."""
        sig_data = _make_sig()
        with TemporaryDirectory() as tmpdir:
            sig_path = join(tmpdir, "codons.json.sig")
            with open(sig_path, "w", encoding="utf-8") as f:
                f.write(dumps(sig_data))
            with patch("egpcommon.manage_github_data.FILES_FOLDER", tmpdir):
                result = _local_sig_data("codons.json.sig")
        assert result is not None, "Expected sig data dict, got None"
        self.assertEqual(result["file_hash"], "abc123")
        self.assertEqual(result["timestamp"], _TS_OLD)


class TestRemoteSigData(TestCase):
    """Tests for _remote_sig_data()."""

    def test_extracts_sig_data_from_release_assets(self) -> None:
        """Correctly parses full sig data from remote .sig assets."""
        release = {
            "assets": [
                {
                    "name": "codons.json.sig",
                    "browser_download_url": "https://example.com/codons.json.sig",
                },
                {
                    "name": "codons.json",
                    "browser_download_url": "https://example.com/codons.json",
                },
            ]
        }
        sig = _make_sig()
        mock_resp = MagicMock()
        mock_resp.json.return_value = sig
        mock_resp.raise_for_status = MagicMock()

        with patch("egpcommon.manage_github_data.get", return_value=mock_resp):
            result = _remote_sig_data(release)

        self.assertIn("codons.json.sig", result)
        self.assertEqual(result["codons.json.sig"]["file_hash"], "abc123")

    def test_empty_assets(self) -> None:
        """Returns empty dict when release has no assets."""
        result = _remote_sig_data({"assets": []})
        self.assertEqual(result, {})


class TestDownloadData(TestCase):
    """Tests for download_data()."""

    @patch("egpcommon.manage_github_data.get")
    @patch("egpcommon.manage_github_data._local_sig_data")
    def test_skips_download_when_local_is_newer(
        self, mock_local_data: MagicMock, mock_get: MagicMock
    ) -> None:
        """Returns False when local timestamp is newer than remote."""
        sig_resp = MagicMock()
        sig_resp.text = dumps(_make_sig(timestamp=_TS_OLD))
        sig_resp.raise_for_status = MagicMock()
        mock_get.return_value = sig_resp

        mock_local_data.return_value = _make_sig(timestamp=_TS_NEW)

        result = download_data()
        self.assertFalse(result)

    @patch("egpcommon.manage_github_data.get")
    @patch("egpcommon.manage_github_data._local_sig_data")
    def test_skips_download_when_timestamps_equal(
        self, mock_local_data: MagicMock, mock_get: MagicMock
    ) -> None:
        """Returns False when local and remote timestamps are identical."""
        sig_resp = MagicMock()
        sig_resp.text = dumps(_make_sig(timestamp=_TS_OLD))
        sig_resp.raise_for_status = MagicMock()
        mock_get.return_value = sig_resp

        mock_local_data.return_value = _make_sig(timestamp=_TS_OLD)

        result = download_data()
        self.assertFalse(result)

    @patch("egpcommon.manage_github_data.get")
    def test_returns_false_on_network_error(self, mock_get: MagicMock) -> None:
        """Returns False and logs warning on connection error."""
        mock_get.side_effect = ReqConnError("no network")

        result = download_data()
        self.assertFalse(result)

    @patch("egpcommon.manage_github_data.get")
    @patch("egpcommon.manage_github_data._local_sig_data")
    def test_downloads_when_remote_is_newer(
        self, mock_local_data: MagicMock, mock_get: MagicMock
    ) -> None:
        """Downloads files when remote timestamp is newer than local."""
        mock_local_data.return_value = _make_sig(timestamp=_TS_OLD)

        def side_effect(url: str, **_: object) -> MagicMock:
            resp = MagicMock()
            resp.raise_for_status = MagicMock()
            if url.endswith(".sig"):
                sig_body = dumps(_make_sig(timestamp=_TS_NEW, file_hash="new_hash"))
                resp.text = sig_body
                resp.content = sig_body.encode("utf-8")
            else:
                resp.content = b'[{"test": "data"}]'
            return resp

        mock_get.side_effect = side_effect

        with TemporaryDirectory() as tmpdir:
            with patch("egpcommon.manage_github_data.FILES_FOLDER", tmpdir):
                result = download_data()

        self.assertTrue(result)

    @patch("egpcommon.manage_github_data.get")
    @patch("egpcommon.manage_github_data._local_sig_data")
    def test_downloads_when_no_local_data(
        self, mock_local_data: MagicMock, mock_get: MagicMock
    ) -> None:
        """Downloads files when no local sig data exists."""
        mock_local_data.return_value = None

        def side_effect(url: str, **_: object) -> MagicMock:
            resp = MagicMock()
            resp.raise_for_status = MagicMock()
            if url.endswith(".sig"):
                sig_body = dumps(_make_sig(timestamp=_TS_NEW))
                resp.text = sig_body
                resp.content = sig_body.encode("utf-8")
            else:
                resp.content = b'[{"test": "data"}]'
            return resp

        mock_get.side_effect = side_effect

        with TemporaryDirectory() as tmpdir:
            with patch("egpcommon.manage_github_data.FILES_FOLDER", tmpdir):
                result = download_data()

        self.assertTrue(result)

    @patch("egpcommon.manage_github_data.get")
    @patch("egpcommon.manage_github_data._local_sig_data")
    def test_download_creates_missing_destination_folder(
        self, mock_local_data: MagicMock, mock_get: MagicMock
    ) -> None:
        """Creates FILES_FOLDER when it does not already exist."""
        mock_local_data.return_value = None

        def side_effect(url: str, **_: object) -> MagicMock:
            resp = MagicMock()
            resp.raise_for_status = MagicMock()
            if url.endswith(".sig"):
                sig_body = dumps(_make_sig(timestamp=_TS_NEW))
                resp.text = sig_body
                resp.content = sig_body.encode("utf-8")
            else:
                resp.content = b'[{"test": "data"}]'
            return resp

        mock_get.side_effect = side_effect

        with TemporaryDirectory() as tmpdir:
            missing_folder = join(tmpdir, "missing", "data")
            self.assertFalse(path.exists(missing_folder))

            with patch("egpcommon.manage_github_data.FILES_FOLDER", missing_folder):
                result = download_data()

            self.assertTrue(result)
            self.assertTrue(path.isdir(missing_folder))
            self.assertTrue(path.exists(join(missing_folder, "codons.json")))
            self.assertTrue(path.exists(join(missing_folder, "codons.json.sig")))
            self.assertTrue(path.exists(join(missing_folder, "types_def.json")))
            self.assertTrue(path.exists(join(missing_folder, "types_def.json.sig")))


class TestUploadData(TestCase):
    """Tests for upload_data()."""

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_without_token(self) -> None:
        """Raises EnvironmentError when token is not set."""
        with self.assertRaises(EnvironmentError):
            upload_data()

    @patch("egpcommon.manage_github_data.post")
    @patch("egpcommon.manage_github_data.requests_delete")
    @patch("egpcommon.manage_github_data._remote_sig_data")
    @patch("egpcommon.manage_github_data._get_or_create_release")
    @patch("egpcommon.manage_github_data._get_github_token", return_value="fake-token")
    @patch("egpcommon.manage_github_data._local_sig_data")
    def test_skips_upload_when_remote_is_newer(
        self,
        mock_local_data: MagicMock,
        _: MagicMock,
        mock_release: MagicMock,
        mock_remote_data: MagicMock,
        mock_delete: MagicMock,
        mock_post: MagicMock,
    ) -> None:
        """Does not upload when remote timestamps are newer."""
        mock_release.return_value = {"id": 1, "assets": []}
        mock_local_data.return_value = _make_sig(timestamp=_TS_OLD)
        mock_remote_data.return_value = {s: _make_sig(timestamp=_TS_NEW) for s in SIG_FILES}

        upload_data()

        mock_post.assert_not_called()
        mock_delete.assert_not_called()

    @patch("egpcommon.manage_github_data.post")
    @patch("egpcommon.manage_github_data.requests_delete")
    @patch("egpcommon.manage_github_data._remote_sig_data")
    @patch("egpcommon.manage_github_data._get_or_create_release")
    @patch("egpcommon.manage_github_data._get_github_token", return_value="fake-token")
    @patch("egpcommon.manage_github_data._local_sig_data")
    def test_skips_upload_when_timestamps_equal(
        self,
        mock_local_data: MagicMock,
        _: MagicMock,
        mock_release: MagicMock,
        mock_remote_data: MagicMock,
        mock_delete: MagicMock,
        mock_post: MagicMock,
    ) -> None:
        """Does not upload when local and remote timestamps are equal."""
        mock_release.return_value = {"id": 1, "assets": []}
        mock_local_data.return_value = _make_sig(timestamp=_TS_OLD)
        mock_remote_data.return_value = {s: _make_sig(timestamp=_TS_OLD) for s in SIG_FILES}

        upload_data()

        mock_post.assert_not_called()
        mock_delete.assert_not_called()


class TestModuleConstants(TestCase):
    """Tests for module-level constants."""

    def test_json_files_defined(self) -> None:
        """JSON_FILES contains expected files."""
        self.assertIn("codons.json", JSON_FILES)
        self.assertIn("types_def.json", JSON_FILES)

    def test_sig_files_match_json_files(self) -> None:
        """Each SIG_FILE corresponds to a JSON file."""
        for jf in JSON_FILES:
            self.assertIn(jf + ".sig", SIG_FILES)

    def test_all_files_is_union(self) -> None:
        """ALL_FILES is the combination of JSON_FILES and SIG_FILES."""
        self.assertEqual(set(ALL_FILES), set(JSON_FILES) | set(SIG_FILES))

    def test_no_meta_codons_reference(self) -> None:
        """Ensure meta_codons.json is not in the managed file list."""
        for f in ALL_FILES:
            self.assertNotIn("meta_codons", f)
