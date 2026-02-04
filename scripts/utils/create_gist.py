#!/usr/bin/env python3
"""
Script to create GitHub Gists from files.
Usage: python scripts/create_gist.py [OPTIONS] FILE_PATH
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load environment variables from .env file
load_dotenv()

console = Console()

GITHUB_API_URL = "https://api.github.com"


def get_github_token() -> str:
    """
    Retrieve GITHUB_TOKEN from environment variables.
    """
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        console.print("[red]Error: GITHUB_TOKEN environment variable not set.[/red]")
        console.print(
            "Please set GITHUB_TOKEN in your .env file or export it in your shell."
        )
        console.print(
            "You can generate a token at: https://github.com/settings/tokens (scope: gist)"
        )
        raise typer.Exit(code=1)
    return token


def main(
    file_path: Path = typer.Argument(
        ...,
        help="Path to the file to upload as a gist.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    description: str = typer.Option(
        None, "--description", "-d", help="Description of the gist."
    ),
    public: bool = typer.Option(
        False, "--public", help="Create a public gist (default is secret)."
    ),
    filename: Optional[str] = typer.Option(
        None,
        "--filename",
        "-f",
        help="Custom filename for the gist file (defaults to the local filename).",
    ),
):
    """
    Create a new GitHub Gist from the specified file.
    """
    token = get_github_token()

    # Determine description and filename
    gist_filename = filename or file_path.name
    gist_description = description or f"Gist created from {file_path.name}"

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[bold red]Failed to read file:[/bold red] {e}")
        raise typer.Exit(code=1)

    # Check for empty content
    if not content.strip():
        console.print("[yellow]Warning: File content is empty.[/yellow]")

    payload = {
        "description": gist_description,
        "public": public,
        "files": {gist_filename: {"content": content}},
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    with console.status(
        f"[bold green]Creating gist from {file_path.name}...[/bold green]"
    ):
        try:
            response = requests.post(
                f"{GITHUB_API_URL}/gists", json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()

            html_url = data.get("html_url")
            console.print(
                Panel(
                    f"[bold green]Gist created successfully![/bold green]\n\n"
                    f"URL: [link={html_url}]{html_url}[/link]\n"
                    f"Visibility: {'Public' if public else 'Secret'}",
                    title="Success",
                    border_style="green",
                )
            )

        except requests.exceptions.HTTPError as e:
            console.print(f"[bold red]HTTP Error:[/bold red] {e}")
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    console.print(
                        f"[red]API Message: {error_data.get('message', 'No message')}[/red]"
                    )
                    if "errors" in error_data:
                        console.print(f"[red]Errors: {error_data['errors']}[/red]")
                except ValueError:
                    console.print(f"[red]Response Text: {e.response.text}[/red]")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
            raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
