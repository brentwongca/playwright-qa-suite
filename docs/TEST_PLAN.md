# Test plan — Swag Labs demo storefront

## 1. Why this exists
This is a personal practice suite. The application under test is
[saucedemo.com](https://www.saucedemo.com), a public demo storefront kept online
for exactly this purpose, so the suite can run in CI without anyone's data being
involved.

## 2. Scope
In scope: login, the product list, the cart, and checkout through to the order
confirmation, on desktop Chromium.

Out of scope: payment (the demo takes none), email, mobile layouts, load and
security testing, and the accounts the site provides to simulate performance
problems (`performance_glitch_user`, `visual_user`) — they make timings
unreliable in CI and are better explored by hand.

## 3. Environment
| Item | Value |
|---|---|
| URL | https://www.saucedemo.com (override with `--base-url-override` or `QA_BASE_URL`) |
| Browser | Chromium, headless in CI, `--headed` locally |
| Accounts | the demo credentials the site publishes on its own login page; override with `QA_USER` / `QA_PASSWORD` |
| Runner | pytest 8 with pytest-playwright |

## 4. Approach
- **Page objects** hold every locator and action, so a change in the application
  is fixed in one file rather than in each test.
- **Data-driven cases** cover the input combinations that matter (five rejected
  login attempts, three missing checkout fields) without repeating the test body.
- **Assertions through Playwright's `expect`**, which retries until the
  application settles, rather than fixed sleeps.
- **A screenshot is attached to the HTML report for every failure** so a failed
  run can be read without re-running it.
- **Markers** (`smoke`, `login`, `inventory`, `cart`, `checkout`) allow a short
  confidence run before a longer one.

## 5. Risks
| Risk | Handling |
|---|---|
| The demo site changes without notice | A nightly scheduled CI run surfaces it as a failure before a real run needs the suite |
| Locators tied to styling break | Locators use `data-test` attributes and roles, not CSS classes, wherever the site offers them |
| Flakiness from timing | No fixed sleeps; `expect` retries, and each test starts from a fresh browser context |
| Tests depending on each other | State is created inside each test; the only shared setup is "already logged in" |

## 6. What "done" looks like
Every case in `TEST_CASES.md` is automated and green in CI, and any failure
produces a report that names the case, the expected result and a screenshot.
