# UI and API test suite — pytest, Playwright and requests

[![tests](https://github.com/brentwongca/playwright-qa-suite/actions/workflows/tests.yml/badge.svg)](https://github.com/brentwongca/playwright-qa-suite/actions/workflows/tests.yml)

A portfolio test suite I wrote to practise the testing craft against two public
practice applications, in the two layers most jobs ask for:

- **UI** — 26 end-to-end cases against [saucedemo.com](https://www.saucedemo.com),
  driven with Playwright and organised behind page objects.
- **API** — 20 cases against the
  [Restful Booker](https://restful-booker.herokuapp.com) REST API, driven with
  `requests`: token auth, the full booking lifecycle, response-shape checks and
  negative cases.

Both layers share one test plan, one traceability table and one CI pipeline
that runs on every push and once a night. **Two real defects** found in the API
are written up in [`docs/BUG_REPORTS.md`](docs/BUG_REPORTS.md), each with a
failing test pinned to it.

Nothing here touches private data: both are public practice services and the
credentials are the ones they publish in their own documentation.

## Run it

```bash
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
python -m playwright install chromium
pytest                                               # all 46 cases
```

Useful variations:

```bash
pytest tests/api                # API only - no browser needed, runs in ~15s
pytest tests/ui                 # UI only
pytest -m smoke                 # the handful that must pass before anything else
pytest -m "login or checkout"   # one area at a time
pytest --headed --slowmo 300    # watch the UI cases run
pytest -n 4                     # in parallel
pytest --base-url-override https://staging.example.com
BOOKER_BASE_URL=https://booker.internal pytest tests/api
```

Every run writes `reports/report.html`, with a full-page screenshot attached to
any failure.

## What is covered

**UI layer**

| Area | Cases | File |
|---|---|---|
| Login, including the locked-out account and five rejected inputs | 8 | `tests/ui/test_login.py` |
| Product list: catalogue size, four sort orders, cart badge, prices | 8 | `tests/ui/test_inventory.py` |
| Cart: contents, persistence across navigation, removal | 4 | `tests/ui/test_cart.py` |
| Checkout: three required-field errors, totals arithmetic, two completed orders | 6 | `tests/ui/test_checkout.py` |

**API layer**

| Area | Cases | File |
|---|---|---|
| Health check, token issuing, three rejected credential sets, writes refused without a token | 6 | `tests/api/test_auth.py` |
| Booking lifecycle: create, read back, list, filter by name, full update, partial update, delete | 7 | `tests/api/test_booking_crud.py` |
| Negative cases: unknown ids, missing fields, reversed dates, stored types | 7 | `tests/api/test_booking_validation.py` |

Two of the negative cases are `xfail(strict=True)` against the defects in
`docs/BUG_REPORTS.md`: the suite stays green while a defect stands and turns
red the moment it is fixed, which is the signal to revisit the write-up.

`docs/TEST_CASES.md` maps every case ID to the test that covers it, and lists
the three cases I decided to keep manual and why.

## How it is put together

```
pages/           one class per screen: locators and actions, no raw selectors in the tests
tests/ui/        the browser layer, one file per area
tests/api/       the HTTP layer: client.py wraps the endpoints, schema.py checks response shape
conftest.py      UI fixtures (base URL, credentials, a logged-in session) and failure screenshots
docs/            test plan, case list with traceability, defect reports, report template
.github/         CI: an API job that needs no browser, and a UI job that does
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
