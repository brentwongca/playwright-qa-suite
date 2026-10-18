# Defects found

Two defects found in the Restful Booker API while writing the API layer. Both
are reproducible from a clean state against the public instance at
`https://restful-booker.herokuapp.com`, last confirmed 2026-10-18.

Each one has a test behind it in `tests/api/test_booking_validation.py`, marked
`xfail(strict=True)`. The suite stays green while the defect stands and turns
red the moment it is fixed, which is the signal to come back and update this
page.

---

## BUG-01 — A booking with a missing required field returns 500, not 400

| | |
|---|---|
| **Severity** | Medium |
| **Endpoint** | `POST /booking` |
| **Test** | API-25, `test_missing_field_is_a_client_error_not_a_server_error` |
| **Status** | Open |

**Steps to reproduce**

1. `POST /booking` with a payload that omits `firstname`:

   ```json
   {
     "lastname": "Tester",
     "totalprice": 275,
     "depositpaid": true,
     "bookingdates": { "checkin": "2026-11-01", "checkout": "2026-11-04" }
   }
   ```

**Expected** — `400 Bad Request` with a body naming the missing field, so the
caller can correct the request.

**Actual** — `500 Internal Server Error` with an HTML error page.

**Why it matters** — the booking is correctly not created, so no bad data is
stored. The problem is the signal: a client cannot tell a payload it can fix
from an outage it must wait out. Retry logic built on status codes will retry a
request that can never succeed, and monitoring that alerts on 5xx will page
somebody for ordinary user error.

---

## BUG-02 — A booking whose checkout precedes its checkin is accepted

| | |
|---|---|
| **Severity** | High |
| **Endpoint** | `POST /booking` |
| **Test** | API-23, `test_checkout_before_checkin_is_rejected` |
| **Status** | Open |

**Steps to reproduce**

1. `POST /booking` with the dates reversed:

   ```json
   {
     "firstname": "Kai",
     "lastname": "Tester",
     "totalprice": 275,
     "depositpaid": true,
     "bookingdates": { "checkin": "2026-11-04", "checkout": "2026-11-01" }
   }
   ```
2. Note the `bookingid` in the response.
3. `GET /booking/{bookingid}`.

**Expected** — `400 Bad Request`: a stay cannot end before it starts.

**Actual** — `200 OK`. The booking is created and reads back with the reversed
dates intact.

**Why it matters** — this one does store bad data. A stay of negative length
will break any downstream consumer that subtracts the dates: occupancy counts,
nightly rate calculations, housekeeping schedules. Because it is stored, the
damage outlives the request, and every report built on the table inherits it.

**Note on scope** — the same reversed dates are also accepted by
`PUT /booking/{id}`, so the missing check is on the booking record rather than
on the create path alone.

---

## Checked and found working

Worth recording so the next person does not re-test them:

- `totalprice` sent as the string `"275"` is coerced and stored as the number
  `275`, and reads back as a number.
- A deleted booking returns `404` on a subsequent `GET`; the delete is real.
- `PUT` and `DELETE` without a token are refused with `403` and leave the
  record untouched.
