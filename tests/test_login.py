"""Authentication behaviour, including the accounts the demo site locks out."""
import pytest

from pages import LoginPage


@pytest.mark.smoke
@pytest.mark.login
def test_valid_credentials_reach_the_product_list(login_page: LoginPage, credentials):
    inventory = login_page.login_expecting_success(
        credentials["user"], credentials["password"]
    )
    inventory.expect_item_count(6)


@pytest.mark.login
@pytest.mark.parametrize(
    "user,secret,message",
    [
        ("standard_user", "wrong_password", "Username and password do not match"),
        ("no_such_user", "secret_sauce", "Username and password do not match"),
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("", "", "Username is required"),
    ],
    ids=["wrong-password", "unknown-user", "no-username", "no-password", "empty-form"],
)
def test_rejected_logins_show_the_right_message(login_page: LoginPage, user, secret, message):
    login_page.login(user, secret).expect_error(message)


@pytest.mark.login
def test_locked_out_account_is_refused(login_page: LoginPage, credentials):
    login_page.login("locked_out_user", credentials["password"]).expect_error(
        "Sorry, this user has been locked out"
    )


@pytest.mark.login
def test_error_can_be_dismissed_and_login_retried(login_page: LoginPage, credentials):
    login_page.login("standard_user", "wrong_password").expect_error(
        "Username and password do not match"
    )
    login_page.page.locator(".error-button").click()
    login_page.expect_no_error()
    inventory = login_page.login_expecting_success(
        credentials["user"], credentials["password"]
    )
    inventory.expect_item_count(6)
