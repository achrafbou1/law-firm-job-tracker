import os
import platform
import sys
from pathlib import Path

from pydantic_settings import BaseSettings

def get_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / 'pyproject.toml').exists():
            return parent
    raise RuntimeError('Project root not found')

PROJECT_ROOT = get_project_root()

def _is_local_machine() -> bool:
    """Detect if running on local dev machine (Windows or .env file exists)."""
    return platform.system() == 'Windows' or (PROJECT_ROOT / '.env').exists()

def _select_env_file() -> str:
    # prefer explicit flag, then common indicators that we're running under pytest
    if os.environ.get('ENV') == 'test':
        return '.env.test'
    if 'PYTEST_CURRENT_TEST' in os.environ:
        return '.env.test'
    if any(('pytest' or 'test_') in str(arg) for arg in sys.argv) :
        return '.env.test'
    return '.env'

class Settings(BaseSettings):

    airtable_token: str
    apify_api_key: str
    law_firm_db_id: str = 'app5hiJRe4T8LcPie'
    sendgrid_api_key: str
    sender_email: str
    receiver_email: str

    @property
    def is_dev(self) -> bool:
        """Returns True if running on local dev machine."""
        return _is_local_machine()

    class Config:
        env_file = PROJECT_ROOT / _select_env_file()
        env_file_encoding = 'utf-8'


settings = Settings()
