from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pathlib import Path
from urllib.parse import urlparse
import shutil
import subprocess
import tempfile

from app.services.discovery_engine import discover_ai_assets


router = APIRouter(
    prefix="/discovery",
    tags=["AI Discovery"],
)


class DiscoveryRequest(BaseModel):
    repository_url: str | None = None
    repository_path: str | None = None


def clone_repository(repository_url: str, target_directory: str):
    """
    Clone a remote Git repository into a temporary directory.
    """

    parsed_url = urlparse(repository_url)

    if parsed_url.scheme != "https":
        raise ValueError(
            "Repository URL must use HTTPS."
        )

    if not parsed_url.netloc:
        raise ValueError(
            "Invalid repository URL."
        )

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                repository_url,
                target_directory,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )

    except FileNotFoundError:
        raise ValueError(
            "Git is not installed or is not available on the server."
        )

    except subprocess.TimeoutExpired:
        raise ValueError(
            "Repository clone timed out."
        )

    except subprocess.CalledProcessError as error:
        message = error.stderr.strip()

        raise ValueError(
            f"Unable to clone repository: {message}"
        )


@router.post("/scan")
def scan_repository(request: DiscoveryRequest):

    if not request.repository_url and not request.repository_path:
        raise HTTPException(
            status_code=400,
            detail=(
                "Provide either repository_url "
                "or repository_path."
            ),
        )

    temporary_directory = None

    try:

        # =================================================
        # REMOTE REPOSITORY
        # =================================================

        if request.repository_url:

            temporary_directory = tempfile.mkdtemp(
                prefix="ai-discovery-"
            )

            repository_directory = str(
                Path(temporary_directory) / "repository"
            )

            clone_repository(
                request.repository_url,
                repository_directory,
            )

            scan_path = repository_directory

        # =================================================
        # LOCAL REPOSITORY
        # =================================================

        else:

            scan_path = request.repository_path

        # =================================================
        # RUN EXISTING DISCOVERY ENGINE
        # =================================================

        assets = discover_ai_assets(
            scan_path
        )

        # =================================================
        # MARK ACTUAL DISCOVERY SOURCE
        # =================================================

        if request.repository_url:
            for asset in assets:
                asset.discovery_source = "Git Repository"
        else:
            for asset in assets:
                asset.discovery_source = "Local Repository"

        return {
            "repository_url": request.repository_url,
            "repository_path": request.repository_path,
            "asset_count": len(assets),
            "assets": assets,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Discovery failed: {error}",
        )

    finally:

        # =================================================
        # CLEAN UP TEMPORARY REPOSITORY
        # =================================================

        if temporary_directory:

            shutil.rmtree(
                temporary_directory,
                ignore_errors=True,
            )