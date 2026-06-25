import os
import shutil
from abc import ABC, abstractmethod
from config import Config
from logger import logger

class BaseUploader(ABC):
    """
    Abstract base class for image uploaders.
    """
    @abstractmethod
    def upload_image(self, image_path: str) -> str:
        """
        Uploads the given image and returns a publicly accessible URL.
        """
        pass

class GithubPagesUploader(BaseUploader):
    """
    Prepares the image for GitHub Pages by copying it to the docs/ directory.
    Note: The actual git commit and push are handled by the GitHub Actions workflow,
    keeping this application platform-independent.
    """
    def upload_image(self, image_path: str) -> str:
        logger.info(f"GitHubPagesUploader: Preparing image for GitHub Pages from {image_path}")
        
        # Ensure docs folder exists
        docs_dir = "docs"
        os.makedirs(docs_dir, exist_ok=True)
        
        # Extract the dynamic filename (e.g. airdrop_date_time.png) from the path
        filename = os.path.basename(image_path)
        target_path = os.path.join(docs_dir, filename)
        
        # 1. Copy the file into the GitHub Pages directory
        shutil.copy(image_path, target_path)
        logger.info(f"Copied image to {target_path} for GitHub Actions to commit.")
        
        # 2. Build public URL
        # URL structure: https://{GITHUB_USERNAME}.github.io/{GITHUB_REPOSITORY}/docs/{filename}
        public_url = f"https://{Config.GITHUB_USERNAME}.github.io/{Config.GITHUB_REPOSITORY}/docs/{filename}"
        logger.info(f"Expected public URL generated: {public_url}")
        
        return public_url

def get_uploader() -> BaseUploader:
    """
    Factory function to return the correct uploader based on configuration.
    Currently defaults to GitHub Pages.
    """
    return GithubPagesUploader()

def upload_image(output_path: str) -> str:
    """
    Main entry point for uploading an image.
    Uses the configured BaseUploader implementation.
    """
    uploader = get_uploader()
    return uploader.upload_image(output_path)
