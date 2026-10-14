"""Protect the public package identity during CI/build-system migration."""

from importlib import metadata
from importlib import resources
from pathlib import Path


def test_version_comes_from_existing_version_file():
    expected = Path("pymyenergi/VERSION").read_text(encoding="utf-8").strip()
    assert metadata.version("pymyenergi") == expected


def test_runtime_dependencies_are_not_replaced_by_ci_tools():
    requirements = metadata.requires("pymyenergi") or []
    assert sorted(requirements) == ["httpx", "pycognito"]


def test_published_python_requirement_is_preserved():
    assert metadata.metadata("pymyenergi")["Requires-Python"] == ">=3.6"


def test_console_entry_point_is_preserved():
    distribution = metadata.distribution("pymyenergi")
    matches = [
        entry.value
        for entry in distribution.entry_points
        if entry.group == "console_scripts" and entry.name == "myenergi"
    ]
    assert matches == ["pymyenergi.cli:cli"]


def test_version_file_is_available_in_installed_package():
    assert resources.files("pymyenergi").joinpath("VERSION").is_file()
