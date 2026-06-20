-- =============================================================================
-- TravClan Hotel Bookings — Normalized PostgreSQL Schema
-- Section 3 — SQL Challenge
-- Source: hotel_bookings (1).csv  |  12,000 rows, 28 columns
-- Target DB: PostgreSQL 14+
-- =============================================================================

-- -----------------------------------------------------------------------
-- Drop in reverse FK dependency order (safe to re-run)
-- -----------------------------------------------------------------------
DROP TABLE IF EXISTS reviews    CASCADE;
DROP TABLE IF EXISTS bookings   CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS customers  CASCADE;


-- -----------------------------------------------------------------------
-- TABLE: customers
-- One row per unique customer_id.
-- Removes: customer_name, customer_segment, customer_signup_date,
--          customer_home_city, customer_loyalty_tier from bookings.
-- -----------------------------------------------------------------------
CREATE TABLE customers (
    customer_id           INTEGER      PRIMARY KEY,
    customer_name         VARCHAR(120) NOT NULL,
    customer_segment      VARCHAR(20)  NOT NULL
        CHECK (customer_segment IN ('Individual', 'Group', 'Corporate')),
    customer_signup_date  DATE         NOT NULL,
    customer_home_city    VARCHAR(60),
    customer_loyalty_tier VARCHAR(10)  NOT NULL
        CHECK (customer_loyalty_tier IN ('None', 'Silver', 'Gold', 'Platinum'))
);


-- -----------------------------------------------------------------------
-- TABLE: properties
-- One row per unique property_id.
-- Removes: property_name, property_city, property_star_rating,
--          property_type, property_total_rooms from bookings.
--
-- Footnote 4 guard: property_name is NOT globally unique.
--   "The Grand Plaza" exists in both Bangalore (id=2) and Kochi (id=1).
--   No UNIQUE constraint on property_name alone for this reason.
--   UNIQUE(property_id) is the only safe identity key.
-- -----------------------------------------------------------------------
CREATE TABLE properties (
    property_id          INTEGER      PRIMARY KEY,
    property_name        VARCHAR(120) NOT NULL,
    property_city        VARCHAR(60)  NOT NULL,
    property_star_rating SMALLINT     NOT NULL
        CHECK (property_star_rating BETWEEN 1 AND 5),
    property_type        VARCHAR(30)  NOT NULL,
    property_total_rooms INTEGER      NOT NULL
        CHECK (property_total_rooms > 0)
);


-- -----------------------------------------------------------------------
-- TABLE: bookings
-- One row per unique booking_id.
-- FKs to customers and properties enforce referential integrity.
--
-- Constraint rationale:
--   chk_valid_stay       — Footnote 1: checkout must be strictly after checkin
--   num_rooms > 0        — Footnote 3: zero-room bookings are data errors
--   booking_status IN    — only the three known statuses are accepted
--   adr / total_amount   — amounts cannot be negative
--
-- Known data-quality violation (NOT enforced here):
--   Footnote 2: 163 rows have booking_date < customer_signup_date.
--   PostgreSQL CHECK constraints cannot reference other tables via subquery.
--   Enforce at the application layer or via a BEFORE INSERT trigger.
-- -----------------------------------------------------------------------
CREATE TABLE bookings (
    booking_id      INTEGER        PRIMARY KEY,
    customer_id     INTEGER        NOT NULL
        REFERENCES customers(customer_id)  ON DELETE RESTRICT,
    property_id     INTEGER        NOT NULL
        REFERENCES properties(property_id) ON DELETE RESTRICT,
    booking_date    DATE           NOT NULL,
    checkin_date    DATE           NOT NULL,
    checkout_date   DATE           NOT NULL,
    room_type       VARCHAR(30),
    num_rooms       SMALLINT       NOT NULL
        CHECK (num_rooms > 0),                              -- Footnote 3
    nights          SMALLINT       NOT NULL
        CHECK (nights > 0),
    booking_channel VARCHAR(30),
    adr             DECIMAL(10,2)
        CHECK (adr >= 0),
    discount_amount DECIMAL(10,2)  NOT NULL DEFAULT 0
        CHECK (discount_amount >= 0),
    coupon_code     VARCHAR(30),
    total_amount    DECIMAL(12,2)
        CHECK (total_amount >= 0),
    payment_method  VARCHAR(30),
    booking_status  VARCHAR(15)    NOT NULL
        CHECK (booking_status IN ('Completed', 'Cancelled', 'No-Show')),

    CONSTRAINT chk_valid_stay
        CHECK (checkout_date > checkin_date)                -- Footnote 1
);

CREATE INDEX idx_bookings_customer ON bookings(customer_id);
CREATE INDEX idx_bookings_property ON bookings(property_id);
CREATE INDEX idx_bookings_status   ON bookings(booking_status);
CREATE INDEX idx_bookings_checkin  ON bookings(checkin_date);


-- -----------------------------------------------------------------------
-- TABLE: reviews
-- One review per booking at most (UNIQUE on booking_id).
-- Separated from bookings because ~34% of bookings have no review (NULL).
-- Storing review columns on every booking row wastes space and forces
-- nullable columns that carry no semantic meaning for unreviewd bookings.
--
-- Footnote 5: Cancelled bookings must not carry a review.
--   Cannot be enforced by a simple CHECK in PostgreSQL (requires cross-table
--   lookup). Enforce via application-layer validation or a trigger.
--
-- Footnote 6: Corporate segment uses 1–10 scale; Individual/Group use 1–5.
--   Column stores raw value. Normalize (Corporate ÷ 2) at query time.
--   CHECK allows the full 1–10 range to accommodate Corporate ratings.
-- -----------------------------------------------------------------------
CREATE TABLE reviews (
    review_id     SERIAL       PRIMARY KEY,
    booking_id    INTEGER      NOT NULL UNIQUE
        REFERENCES bookings(booking_id) ON DELETE CASCADE,
    review_rating DECIMAL(3,1) NOT NULL
        CHECK (review_rating BETWEEN 1 AND 10),             -- Footnote 6
    review_date   DATE         NOT NULL
);


-- =============================================================================
-- QUERY 1 — Top-Revenue Property per City
-- =============================================================================
-- Business question:
--   Which single property in each city generated the highest realized revenue?
--
-- Window function: RANK() OVER (PARTITION BY property_city ORDER BY revenue DESC)
--   Partitions the result set by city so each city gets its own rank sequence.
--   RANK() is used (not ROW_NUMBER()) so ties both receive rank = 1.
--
-- Footnote guards:
--   FN8  — booking_status = 'Completed' (realized revenue only)
--   FN1  — guaranteed by chk_valid_stay; retained in WHERE for explicitness
--   FN3  — guaranteed by CHECK num_rooms > 0; retained for explicitness
-- =============================================================================

WITH property_revenue AS (
    SELECT
        p.property_city,
        p.property_id,
        p.property_name,
        SUM(b.total_amount)  AS total_revenue,
        COUNT(*)             AS completed_bookings
    FROM      bookings   b
    JOIN      properties p ON b.property_id = p.property_id
    WHERE     b.booking_status  = 'Completed'               -- FN8
      AND     b.checkout_date   > b.checkin_date            -- FN1 (schema-guaranteed)
      AND     b.num_rooms       > 0                         -- FN3 (schema-guaranteed)
    GROUP BY  p.property_city, p.property_id, p.property_name
),
ranked AS (
    SELECT
        property_city,
        property_id,
        property_name,
        total_revenue,
        completed_bookings,
        RANK() OVER (
            PARTITION BY property_city
            ORDER BY     total_revenue DESC
        )                    AS revenue_rank
    FROM property_revenue
)
SELECT
    property_city,
    property_id,
    property_name,
    ROUND(total_revenue, 2)  AS total_revenue,
    completed_bookings,
    revenue_rank
FROM   ranked
WHERE  revenue_rank = 1
ORDER  BY property_city;


-- =============================================================================
-- QUERY 2 — Frequent Customers (avg inter-booking gap < 30 days)
-- =============================================================================
-- Business question:
--   Which customers book repeatedly and frequently, with fewer than 30 days
--   on average between consecutive completed check-in dates?
--
-- Window function: LAG(checkin_date) OVER (PARTITION BY customer_id ORDER BY checkin_date)
--   For each completed stay, LAG() retrieves the previous stay's check-in date
--   for the same customer. The difference is the gap in days.
--   The first stay per customer produces NULL (no prior row) — excluded by
--   WHERE gap_days IS NOT NULL.
--
-- HAVING COUNT(gap_days) >= 1 requires at least 2 completed stays so that
-- one computable gap exists (a single stay cannot produce an average).
--
-- Footnote guards:
--   FN8  — booking_status = 'Completed'
--   FN1 + FN3 guaranteed by schema constraints
-- =============================================================================

WITH completed_stays AS (
    SELECT
        customer_id,
        checkin_date
    FROM  bookings
    WHERE booking_status = 'Completed'                      -- FN8
),
booking_gaps AS (
    SELECT
        customer_id,
        checkin_date,
        LAG(checkin_date) OVER (
            PARTITION BY customer_id
            ORDER BY     checkin_date
        )                                     AS prev_checkin,
        checkin_date - LAG(checkin_date) OVER (
            PARTITION BY customer_id
            ORDER BY     checkin_date
        )                                     AS gap_days
    FROM completed_stays
),
customer_avg_gaps AS (
    SELECT
        customer_id,
        COUNT(gap_days)                       AS gap_count,
        COUNT(gap_days) + 1                   AS total_stays,
        ROUND(AVG(gap_days), 1)              AS avg_gap_days
    FROM  booking_gaps
    WHERE gap_days IS NOT NULL
    GROUP BY customer_id
    HAVING COUNT(gap_days) >= 1                             -- at least 2 completed stays
)
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.customer_loyalty_tier,
    cag.total_stays,
    cag.avg_gap_days
FROM  customer_avg_gaps cag
JOIN  customers         c ON cag.customer_id = c.customer_id
WHERE cag.avg_gap_days < 30
ORDER BY cag.avg_gap_days ASC, cag.total_stays DESC;
