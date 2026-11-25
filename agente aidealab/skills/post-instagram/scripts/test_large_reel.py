import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

import publish_next as publisher


class LargeReelTests(unittest.TestCase):
    def test_resumable_failure_uses_drive_without_reencoding(self):
        with tempfile.TemporaryDirectory() as temp:
            video = Path(temp) / "reel.mp4"
            video.write_bytes(b"original")
            with patch.object(publisher, "LIMITE_STORAGE_MB", 0), \
                 patch.object(publisher.requests, "post", side_effect=requests.RequestException("recusado")), \
                 patch.object(publisher, "publish_reel_por_drive", return_value="post-123") as fallback:
                result = publisher.publish_reel(video, "drive-123", None, "Legenda", "ig-123")
        self.assertEqual(result, "post-123")
        fallback.assert_called_once_with("drive-123", None, "Legenda", "ig-123")

    def test_drive_permission_is_temporary(self):
        permissions = Mock()
        permissions.json.return_value = {"permissions": []}
        created = Mock()
        created.json.return_value = {"id": "permission-123"}
        container = Mock()
        container.json.return_value = {"id": "container-123"}
        revoked = Mock(status_code=204)
        with patch.object(publisher, "token_drive", return_value="drive-token"), \
             patch.object(publisher.requests, "get", return_value=permissions), \
             patch.object(publisher.requests, "post", side_effect=[created, container]), \
             patch.object(publisher.requests, "delete", return_value=revoked) as delete, \
             patch.object(publisher, "raise_checked"), \
             patch.object(publisher, "publicar_container", return_value="post-123"):
            result = publisher.publish_reel_por_drive("drive-123", None, "Legenda", "ig-123")
        self.assertEqual(result, "post-123")
        delete.assert_called_once()
        self.assertIn("permission-123", delete.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
