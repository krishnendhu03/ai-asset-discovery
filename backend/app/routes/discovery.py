from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pathlib import Path
from urllib.parse import urlparse
import shutil
import subprocess
import tempfile

from app.services.discovery_engine import (
    discover_ai_assets,
    aggregate_application_assets,
)


router = APIRouter(
    prefix="/discovery",
    tags=["AI Discovery"],
)


class DiscoveryRequest(BaseModel):
    repository_url: str | None = None
    repository_path: str | None = None


def clone_repository(
    repository_url: str,
    target_directory: str,
):
    """
    Clone a remote GitHub repository into a temporary directory.
    """

    repository_url = repository_url.strip()

    parsed_url = urlparse(repository_url)

    # -----------------------------------------------------
    # URL validation
    # -----------------------------------------------------

    if parsed_url.scheme.lower() != "https":
        raise ValueError(
            "Repository URL must use HTTPS."
        )

    if parsed_url.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise ValueError(
            "Only GitHub repository URLs are supported."
        )

    # -----------------------------------------------------
    # Extract repository path
    # -----------------------------------------------------

    repository_path = (
        parsed_url.path
        .strip("/")
        .removesuffix(".git")
    )

    parts = repository_path.split("/")

    if len(parts) != 2:
        raise ValueError(
            "Invalid GitHub repository URL. "
            "Use https://github.com/owner/repository"
        )

    owner, repository = parts

    if not owner or not repository:
        raise ValueError(
            "Invalid GitHub repository URL."
        )

    # -----------------------------------------------------
    # Clone repository
    # -----------------------------------------------------

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
            "Git is not installed or is not available "
            "on the server."
        )

    except subprocess.TimeoutExpired:

        raise ValueError(
            "Repository clone timed out."
        )

    except subprocess.CalledProcessError as error:

        message = (
            error.stderr.strip()
            or error.stdout.strip()
            or "Unknown Git error."
        )

        if (
            "repository not found" in message.lower()
            or "not found" in message.lower()
        ):
            raise ValueError(
                "GitHub repository was not found. "
                "Check the owner and repository name."
            )

        if (
            "authentication" in message.lower()
            or "permission" in message.lower()
            or "could not read username" in message.lower()
        ):
            raise ValueError(
                "This repository may be private or "
                "requires authentication."
            )

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

        raw_assets = discover_ai_assets(
            scan_path
        )
        assets = aggregate_application_assets(
            raw_assets,
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