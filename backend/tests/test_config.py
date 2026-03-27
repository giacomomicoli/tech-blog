"""Tests for settings and Docker secret handling."""

from unittest.mock import patch

from src.config import Settings


class TestSettings:
    @patch("src.config._read_secret")
    def test_injects_redis_password_from_secret(self, mock_read_secret):
        def _secret(name: str) -> str | None:
            if name == "redis_password":
                return "p@ss:word/with?#[ ]"
            return None

        mock_read_secret.side_effect = _secret

        settings = Settings(redis_url="redis://redis:6379/0")

        expected = "redis://:p%40ss%3Aword%2Fwith%3F%23%5B%20%5D@redis:6379/0"
        assert settings.redis_url == expected

    @patch("src.config._read_secret", return_value=None)
    def test_keeps_redis_url_when_secret_missing(self, _mock_read_secret):
        settings = Settings(redis_url="redis://redis:6380/1")
        assert settings.redis_url == "redis://redis:6380/1"
