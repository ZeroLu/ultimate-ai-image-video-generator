"""Shared constants for CyberBara CLI."""

DEFAULT_BASE_URL = "https://cyberbara.com"
API_KEY_PAGE_URL = f"{DEFAULT_BASE_URL}/settings/apikeys"
FINAL_TASK_STATUSES = {"success", "failed", "canceled"}
DEFAULT_OUTPUT_DIR = "media_outputs"
DEFAULT_HTTP_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
