"""Shared fixtures and command-line options.

Run against the default environment:      pytest
Run one marker only:                      pytest -m smoke
Run headed, slowed down, to watch it:     pytest --headed --slowmo 300
Run in parallel:                          pytest -n 4
Point at another environment:             pytest --base-url https://example.com
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from pages import InventoryPage, LoginPage

DEFAULT_BASE_URL = "https://www.saucedemo.com"

# Credentials published by the demo site on its own login page. They are not
# anyone's personal credentials; override with env vars for another environment.
STANDARD_USER = os.getenv("QA_USER", "standard_user")
STANDARD_PASSWORD = os.getenv("QA_PASSWORD", "secret_sauce")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url-override",
        action="store",
        default=os.getenv("QA_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL of the environment under test.",
    )


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--base-url-override")


@pytest.fixture(scope="session")
def credentials() -> dict[str, str]:
    return {"user": STANDARD_USER, "password": STANDARD_PASSWORD}


@pytest.fixture()
def login_page(page, base_url: str) -> LoginPage:
    return LoginPage(page, base_url).open()


@pytest.fixture()
def inventory_page(login_page: LoginPage, credentials: dict[str, str]) -> InventoryPage:
    """A session that is already past login, for tests that are not about login."""
    return login_page.login_expecting_success(
        credentials["user"], credentials["password"]
    )


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the HTML report whenever a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page = item.funcargs.get("page")
    if page is None:
        return
    Path("reports").mkdir(exist_ok=True)
    target = Path("reports") / f"{item.name}.png"
    try:
        page.screenshot(path=str(target), full_page=True)
    except Exception:  # a closed page cannot be captured; the report still stands
        return
    extras = getattr(report, "extras", [])
    try:
        import pytest_html

        extras.append(pytest_html.extras.image(str(target.name)))
        report.extras = extras
    except ImportError:
        pass
