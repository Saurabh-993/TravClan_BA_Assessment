# Section 3 — SQL Challenge: Answers

**File:** `code/schema.sql`
**Database:** PostgreSQL 14+

---

## Part 1 — Schema Design

### Normalization: 28-column CSV → 4 tables

The source CSV is fully denormalized — every booking row duplicates customer and property attributes. Normalization removes that redundancy and enforces data integrity at the database level.

| Table | Natural key | Columns extracted from CSV | Rows (approx.) |
|---|---|---|---|
| `customers` | `customer_id` | customer_name, segment, signup_date, home_city, loyalty_tier | ~900 unique |
| `properties` | `property_id` | property_name, city, star_rating, property_type, total_rooms | ~60 unique |
| `bookings` | `booking_id` | booking_date, checkin/checkout, rooms, channel, amounts, status | 12,000 |
| `reviews` | `review_id` (SERIAL) | review_rating, review_date | ~5,146 (those with a review) |

Reviews are split into their own table because ~34% of bookings carry no review. Keeping nullable `review_rating` and `review_date` on every booking row wastes space and forces semantically empty NULLs on the majority of rows.

---

### Constraints and Footnote Mapping

| Constraint | Table | Clause | Footnote |
|---|---|---|---|
| Valid stay | `bookings` | `CHECK (checkout_date > checkin_date)` | FN1 |
| Non-zero rooms | `bookings` | `CHECK (num_rooms > 0)` | FN3 |
| Booking status enum | `bookings` | `CHECK (booking_status IN ('Completed','Cancelled','No-Show'))` | — |
| Non-negative amounts | `bookings` | `CHECK (adr >= 0)`, `CHECK (total_amount >= 0)` | — |
| Customer segment enum | `customers` | `CHECK (customer_segment IN ('Individual','Group','Corporate'))` | FN6 |
| Loyalty tier enum | `customers` | `CHECK (customer_loyalty_tier IN ('None','Silver','Gold','Platinum'))` | FN7 |
| Star rating range | `properties` | `CHECK (property_star_rating BETWEEN 1 AND 5)` | — |
| Total rooms positive | `properties` | `CHECK (property_total_rooms > 0)` | — |
| One review per booking | `reviews` | `UNIQUE (booking_id)` | FN5 |
| Review rating range | `reviews` | `CHECK (review_rating BETWEEN 1 AND 10)` | FN6 |

**Constraints NOT enforced at DB level (and why):**

- **FN2 (booking before signup):** PostgreSQL `CHECK` clauses cannot reference other tables via subquery. 163 rows in the source data violate this. Enforce at application layer or via a `BEFORE INSERT` trigger.
- **FN5 (cancelled + review):** Requires cross-table lookup (bookings.booking_status ≠ 'Cancelled' for any row in reviews). Same limitation — enforce via application layer or trigger.

**Footnote 4 (property name collision):**
`The Grand Plaza` exists in both Bangalore (`property_id = 2`) and Kochi (`property_id = 1`). No `UNIQUE` constraint is placed on `property_name` alone. The only safe identity is `property_id`.

---

## Part 2 — Query 1: Top Revenue Property per City

### Business question
Which single property in each city generated the highest realized revenue (completed bookings only)?

### How the window function works

```
RANK() OVER (PARTITION BY property_city ORDER BY total_revenue DESC)
```

1. The `WITH property_revenue` CTE aggregates `SUM(total_amount)` per `(city, property_id, property_name)`, filtering by `booking_status = 'Completed'` (FN8).
2. The `ranked` CTE applies `RANK()`. `PARTITION BY property_city` resets the rank counter for each city. `ORDER BY total_revenue DESC` assigns rank 1 to the highest-revenue property in that city.
3. The outer `SELECT` filters `WHERE revenue_rank = 1`.

`RANK()` is used instead of `ROW_NUMBER()` because ties both receive rank 1 (if two properties in the same city had identical revenue, both would appear). `ROW_NUMBER()` would arbitrarily pick one.

### Expected output (computed from source data)

| property_city | property_id | property_name | total_revenue | completed_bookings | revenue_rank |
|---|---|---|---|---|---|
| Bangalore | 2 | The Grand Plaza | Rs. 13,957,983.73 | 192 | 1 |
| Chennai | 53 | Saffron Heights | Rs. 14,111,093.22 | 196 | 1 |
| Delhi | 49 | Mango Retreat | Rs. 4,153,549.17 | 150 | 1 |
| Goa | 23 | Sapphire Retreat | Rs. 19,481,171.66 | 169 | 1 |
| Jaipur | 30 | Ivory Retreat | Rs. 1,798,347.49 | 168 | 1 |
| Kochi | 1 | The Grand Plaza | Rs. 6,631,787.86 | 174 | 1 |
| Manali | 10 | Lotus Manor | Rs. 4,320,055.00 | 193 | 1 |
| Mumbai | 11 | Coral Palace | Rs. 10,575,127.65 | 191 | 1 |
| Pune | 34 | Velvet Palace | Rs. 5,921,213.85 | 161 | 1 |
| Udaipur | 6 | Hilltop Inn | Rs. 15,669,688.12 | 181 | 1 |

**10 rows — one per city.**

> Note: "The Grand Plaza" appears for both Bangalore and Kochi with different `property_id` values, directly demonstrating why Footnote 4 requires grouping by `property_id` and not `property_name`.

---

## Part 3 — Query 2: Frequent Customers

### Business question
Which customers book repeatedly with an average inter-booking gap of fewer than 30 days between completed check-in dates?

### How the window function works

```
LAG(checkin_date) OVER (PARTITION BY customer_id ORDER BY checkin_date)
```

1. `completed_stays` CTE: filters to `booking_status = 'Completed'` (FN8).
2. `booking_gaps` CTE: for every completed stay, `LAG()` looks back one row in the same customer's history (ordered by `checkin_date`) and returns the previous check-in date. The difference in days is `gap_days`. The very first stay per customer produces `NULL` (no prior row exists).
3. `customer_avg_gaps` CTE: filters out `NULL` gaps, then averages the remaining gaps per customer. `HAVING COUNT(gap_days) >= 1` requires at least two completed stays (one computable gap).
4. Outer query joins back to `customers` and filters `avg_gap_days < 30`.

### Expected output (top 10 of 432 frequent customers, sorted by avg gap ASC)

| customer_id | customer_name | customer_segment | customer_loyalty_tier | total_stays | avg_gap_days |
|---|---|---|---|---|---|
| 560 | Customer_560 | Individual | Silver | 17 | 15.1 |
| 319 | Customer_319 | Corporate | None | 17 | 15.9 |
| 268 | Customer_268 | Group | Gold | 15 | 16.0 |
| 702 | Customer_702 | Corporate | Silver | 18 | 16.1 |
| 707 | Customer_707 | Individual | None | 16 | 16.7 |
| 754 | Customer_754 | Individual | Platinum | 21 | 16.7 |
| 113 | Customer_113 | Individual | Silver | 22 | 16.7 |
| 324 | Customer_324 | Individual | None | 16 | 16.9 |
| 633 | Customer_633 | Group | None | 19 | 16.9 |
| 181 | Customer_181 | Corporate | Gold | 20 | 16.9 |

**Total result set: 432 customers** with avg_gap_days < 30 (out of ~900 unique customers).

Customer_113 (22 stays, 16.7d avg gap) and Customer_754 (21 stays, 16.7d avg gap) are the highest-frequency bookers by stay count among the top-10 frequent customers.

---

## Summary

| Item | Detail |
|---|---|
| Tables | 4 (`customers`, `properties`, `bookings`, `reviews`) |
| PKs | Natural integers (`customer_id`, `property_id`, `booking_id`) + `SERIAL` for `review_id` |
| FKs | `bookings → customers`, `bookings → properties`, `reviews → bookings` |
| CHECK constraints | 9 across 4 tables, tied to FN1, FN3, FN5, FN6, FN7 |
| Q1 result | 10 rows (1 per city) — top property by realized revenue |
| Q2 result | 432 customers with avg inter-booking gap < 30 days |
| Window functions | `RANK() OVER (PARTITION BY ... ORDER BY ...)` and `LAG() OVER (PARTITION BY ... ORDER BY ...)` |
