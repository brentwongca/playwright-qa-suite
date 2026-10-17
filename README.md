# Playwright + pytest test suite — Swag Labs demo storefront

An end-to-end suite I wrote to practise the testing craft on a public demo
application: [saucedemo.com](https://www.saucedemo.com). 26 automated cases
across login, the product list, the cart and checkout, with page objects, a
written test plan, a traceability table, and CI that runs the suite on every
push and once a night.

Nothing here touches private data: the site is a demo storefront and the
credentials are the ones it publishes on its own login page.

## Run it

```bash
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
python -m playwright install chromium
pytest                                               # all 26 cases, headless
```

Useful variations:

```bash
pytest -m smoke                 # the four cases that must pass before anything else
pytest -m "login or checkout"   # one area at a time
pytest --headed --slowmo 300    # watch it run
pytest -n 4                     # in parallel
pytest --base-url-override https://staging.example.com
```

Every run writes `reports/report.html`, with a full-page screenshot attached to
any failure.

## What is covered

| Area | Cases | File |
|---|---|---|
| Login, including the locked-out account and five rejected inputs | 8 | `tests/test_login.py` |
| Product list: catalogue size, four sort orders, cart badge, prices | 8 | `tests/test_inventory.py` |
| Cart: contents, persistence across navigation, removal | 4 | `tests/test_cart.py` |
| Checkout: three required-field errors, totals arithmetic, two completed orders | 6 | `tests/test_checkout.py` |

`docs/TEST_CASES.md` maps every case ID to the test that covers it, and lists
the three cases I decided to keep manual and why.

## How it is put together

```
pages/        one class per screen: locators and actions, no assertions in tests about raw selectors
tests/        one file per area, markers for selective runs
conftest.py   fixtures (base URL, credentials, an already-logged-in session) and failure screenshots
docs/         test plan, case list with traceability, defect report template
.github/      CI workflow: install, run, publish the HTML report as an artifact
```

Decisions worth naming:

- **Locators prefer `data-test` attributes and roles** over CSS classes, so a
  restyle does not break the suite.
- **No fixed sleeps.** Playwright's `expect` retries until the application
  settles, which is what keeps the suite from flaking.
- **Each test creates its own state.** The only shared setup is "already logged
  in", which keeps the login tests independent of everything else.
- **A nightly scheduled run** exists because the application is a third-party
  site: it tells me when the site changed, not when I did.

## Current state

26 passing locally and in CI. The three manual cases in `docs/TEST_CASES.md`
are deliberate, not a backlog.
