# Section 4 — Weather-Cancellation Insight

## Key Finding

Hotel bookings with a **rainy check-in day (precipitation > 5 mm/day)** cancelled at **29.2%**, compared to **21.0%** on clear days — a **8.2 percentage-point higher** cancellation rate on rainy days.

## City-Level Breakdown

| City | Rainy Day Cancel Rate | Clear Day Cancel Rate | Difference |
|---|---|---|---|
| Goa | 35.5% (n=313) | 20.8% (n=563) | +14.7 pp |
| Manali | 21.3% (n=249) | 21.2% (n=457) | +0.1 pp |

## Methodology

- Source: `hotel_bookings (1).csv` — Goa + Manali, check-in year 2024 (1582 bookings with matched weather)
- Weather: Open-Meteo ERA5 historical API — daily `precipitation_sum` (mm) and `temperature_2m_max` (°C)
- Rainy threshold: `precipitation_sum > 5.0 mm/day` (562 rainy-day bookings, 1020 clear-day bookings)
- Cancellation: `booking_status == 'Cancelled'`; data-quality filters FN1 + FN3 applied before analysis
- One API call per city (batch by city + full date range); merged on `property_city` + `checkin_date`

## Business Implication

The precipitation effect is concentrated in **Goa during the monsoon window (Jun–Aug)**, consistent with the root-cause finding in Section 2 (H3 — city-season interaction). Weather data quantifies the mechanism: guests cancel on the actual rainy check-in day, not only during the advance booking window. This reinforces the Section 2 recommendation of a **non-refundable 20% deposit for Goa Jun–Aug bookings** as the primary intervention — it internalises the cost of last-minute weather-driven cancellations rather than absorbing them as lost revenue.
