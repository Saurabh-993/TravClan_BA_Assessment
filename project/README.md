# TravClan — Weather-Cancellation Analyzer

Fetches 2024 historical daily weather for **Goa** and **Manali** from the Open-Meteo ERA5 API and measures whether rainy check-in days drive higher hotel cancellation rates.

## Usage

```bash
python project/weather_analyzer.py
```

## Output

| File | Description |
|---|---|
| `project/insight.md` | Quantified finding with city-level breakdown |
| `project/output/s4_weather_cancellation.png` | Rainy vs clear cancellation rate chart |

## Dependencies

```
requests>=2.28
pandas>=1.5
matplotlib>=3.6
```

Install: `pip install requests pandas matplotlib`

## Data sources

- Hotel bookings: `hotel_bookings (1).csv` (scoped to Goa + Manali, 2024 check-ins)
- Weather: [Open-Meteo ERA5 Historical API](https://open-meteo.com/en/docs/historical-weather-api) — no API key required
