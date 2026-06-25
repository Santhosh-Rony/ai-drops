import os
import sys
from dotenv import load_dotenv
from logger import logger

# Load environment variables from .env file if present
load_dotenv()

class Config:
    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_FALLBACK_API_KEY = os.getenv("OPENROUTER_FALLBACK_API_KEY")
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")

    # GitHub Actions sets GITHUB_REPOSITORY to "owner/repo" by default. We only want "repo".
    GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
    raw_repo = os.environ.get("GITHUB_REPOSITORY")
    GITHUB_REPOSITORY = raw_repo.split("/")[-1] if raw_repo else None

    # Font Configuration
    FONT_PATH = "assets/Montserrat-VariableFont_wght.ttf"
    FONT_ITALIC_PATH = "assets/Montserrat-Italic-VariableFont_wght.ttf"

    # Template Directories
    TEMPLATES_DIR = "templates"
    OUTPUT_DIR = "output"

    @classmethod
    def validate(cls):
        """Validates that all necessary environment variables are set."""
        missing = []
        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        if not cls.INSTAGRAM_ACCESS_TOKEN:
            missing.append("INSTAGRAM_ACCESS_TOKEN")
        if not cls.INSTAGRAM_BUSINESS_ID:
            missing.append("INSTAGRAM_BUSINESS_ID")
        if not cls.GITHUB_USERNAME:
            missing.append("GITHUB_USERNAME")
        if not cls.GITHUB_REPOSITORY:
            missing.append("GITHUB_REPOSITORY")

        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            sys.exit(1)
        logger.info("Configuration validated successfully.")
