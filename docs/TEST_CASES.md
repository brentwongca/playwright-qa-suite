# Test cases and traceability

Each case states what is being checked, the expected result, and the automated
test that covers it. The ID is what I would quote in a defect report.

## Login — `tests/ui/test_login.py`
| ID | Case | Expected result | Automated test |
|---|---|---|---|
| LOG-01 | Valid credentials | Product list opens with 6 products | `test_valid_credentials_reach_the_product_list` |
| LOG-02 | Correct username, wrong password | Error: "Username and password do not match" | `test_rejected_logins_show_the_right_message[wrong-password]` |
| LOG-03 | Unknown username | Same generic error, no hint that the user does not exist | `test_rejected_logins_show_the_right_message[unknown-user]` |
| LOG-04 | Username left blank | Error: "Username is required" | `test_rejected_logins_show_the_right_message[no-username]` |
| LOG-05 | Password left blank | Error: "Password is required" | `test_rejected_logins_show_the_right_message[no-password]` |
| LOG-06 | Both fields blank | Error names the username first | `test_rejected_logins_show_the_right_message[empty-form]` |
| LOG-07 | Locked-out account | Error: "Sorry, this user has been locked out" | `test_locked_out_account_is_refused` |
| LOG-08 | Dismiss the error and log in again | Error clears; second attempt succeeds | `test_error_can_be_dismissed_and_login_retried` |

## Product list — `tests/ui/test_inventory.py`
| ID | Case | Expected result | Automated test |
|---|---|---|---|
| INV-01 | Catalogue size | 6 products listed | `test_six_products_are_listed` |
| INV-02 | Sort A to Z | Names ascending | `test_sort_by_name_ascending` |
| INV-03 | Sort Z to A | Names descending | `test_sort_by_name_descending` |
| INV-04 | Sort price low to high | Prices ascending | `test_sort_by_price_low_to_high` |
| INV-05 | Sort price high to low | Prices descending | `test_sort_by_price_high_to_low` |
| INV-06 | Cart badge increments | Badge shows 1 then 2 | `test_cart_badge_counts_each_product_added` |
| INV-07 | Cart badge decrements | Badge disappears at zero | `test_removing_a_product_lowers_the_badge` |
| INV-08 | Every product priced | 6 prices, all above zero | `test_every_product_shows_a_price` |

## Cart — `tests/ui/test_cart.py`
| ID | Case | Expected result | Automated test |
|---|---|---|---|
| CRT-01 | Added product appears | One row, quantity 1 | `test_added_product_appears_in_the_cart` |
| CRT-02 | Contents survive navigation | Still there after Continue Shopping | `test_cart_keeps_its_contents_when_shopping_continues` |
| CRT-03 | Remove from inside the cart | Two rows become one, the right one remains | `test_product_can_be_removed_from_inside_the_cart` |
| CRT-04 | Empty cart | No rows | `test_empty_cart_has_no_rows` |

## Checkout — `tests/ui/test_checkout.py`
| ID | Case | Expected result | Automated test |
|---|---|---|---|
| CHK-01 | First name missing | Error: "First Name is required" | `test_checkout_requires_every_field[no-first-name]` |
| CHK-02 | Last name missing | Error: "Last Name is required" | `test_checkout_requires_every_field[no-last-name]` |
| CHK-03 | Postal code missing | Error: "Postal Code is required" | `test_checkout_requires_every_field[no-postcode]` |
| CHK-04 | One-item order | Confirmation: "Thank you for your order!" | `test_single_item_order_completes` |
| CHK-05 | Totals arithmetic | Tax is 8% of the subtotal; total is subtotal plus tax | `test_overview_totals_add_up` |
| CHK-06 | Five-item order | Order completes with 5 products | `test_order_can_be_placed_for_the_whole_catalogue` |

## API — auth — `tests/api/test_auth.py`
| ID | Case | Expected result | Automated test |
|---|---|---|---|
| API-01 | Service health | `GET /ping` answers 201 | `test_health_endpoint_reports_the_service_is_up` |
| API-02 | Valid credentials | A non-empty token is issued | `test_valid_credentials_return_a_token` |
| API-03 | Bad credentials, three variants | No token; reason "Bad credentials" | `test_bad_credentials_do_not_return_a_token[...]` |
| API-04 | Update with no token | 403, and the record is unchanged | `test_update_without_a_token_is_rejected` |
| API-05 | Delete with no token | 403, and the record survives | `test_delete_without_a_token_is_rejected` |

## API — booking lifecycle — `tests/api/test_booking_crud.py`
| ID | Case | Expected result | Automated test |
|---|---|---|---|
| API-10 | Create a booking | An integer id, and the sent values echoed back | `test_create_returns_an_id_and_echoes_the_booking` |
| API-11 | Read it back | 200, correct shape and values | `test_created_booking_can_be_read_back` |
| API-12 | Appears in the list | The new id is in `GET /booking` | `test_new_booking_appears_in_the_list` |
| API-13 | Filter by name | Filtering by firstname and lastname returns the id | `test_list_can_be_filtered_by_name` |
| API-14 | Full update (PUT) | Every field is replaced as sent | `test_full_update_replaces_every_field` |
| API-15 | Partial update (PATCH) | Named field changes; the others do not | `test_partial_update_changes_only_the_named_fields` |
| API-16 | Delete | 201, and a later read returns 404 | `test_deleted_booking_is_gone` |

## API — validation and negative cases — `tests/api/test_booking_validation.py`
| ID | Case | Expected result | Automated test |
|---|---|---|---|
| API-20 | Unknown booking id | 404 | `test_unknown_booking_id_returns_not_found` |
| API-21 | Delete an unknown id | Not reported as 201 Created | `test_deleting_an_unknown_booking_is_not_reported_as_success` |
| API-22 | Missing required field | The booking is not stored | `test_booking_without_required_fields_is_rejected` |
| API-23 | Checkout before checkin | Rejected — **fails: BUG-02**, `xfail(strict)` | `test_checkout_before_checkin_is_rejected` |
| API-24 | Price type | `totalprice` reads back as a number | `test_price_is_stored_as_a_number` |
| API-25 | Bad input is a client error | 4xx, not 500 — **fails: BUG-01**, `xfail(strict)` | `test_missing_field_is_a_client_error_not_a_server_error` |

## Not automated, checked by hand
| ID | Case | Why it is not automated |
|---|---|---|
| MAN-01 | `performance_glitch_user` login | Deliberately slow; timings would make CI unreliable |
| MAN-02 | `visual_user` layout faults | Needs a human eye or image comparison, which this suite does not do |
| MAN-03 | Browser back button through checkout | Worth exploring by hand before deciding what to pin down |
