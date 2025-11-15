from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import os


@dataclass
class PortalConfig:
    """
    Configuration container for portal automation settings.

    Environment variables keep credentials outside of the repository.
    """

    home_url: str = "https://vswsonline.ap.gov.in/#/home"
    dashboard_url: str = "https://vswsonline.ap.gov.in/#/suomoto"
    username_env: str = "PORTAL_USERNAME"
    password_env: str = "PORTAL_PASSWORD"
    chrome_profile: Optional[Path] = None
    wait_seconds: int = 30

    def credentials(self) -> Tuple[str, str]:
        """Read credentials from environment variables."""
        username = os.getenv(self.username_env)
        password = os.getenv(self.password_env)
        if not username or not password:
            raise RuntimeError(
                "Missing portal credentials. "
                f"Set {self.username_env} and {self.password_env} environment variables."
            )
        return username, password


def resolve_profile(path: Optional[str]) -> Optional[Path]:
    """Resolve a user provided Chrome profile path."""
    if not path:
        return None
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Chrome profile path does not exist: {resolved}")
    return resolved
