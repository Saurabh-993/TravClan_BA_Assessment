"""
Generate answers/answers.html — PDF-ready consolidated answers document.
Covers Sections 1, 2, and 3 with embedded charts.

Usage:  python answers/generate_answers.py
Then:   Open answers/answers.html in Chrome/Edge
        → Ctrl+P → Destination: Save as PDF → Save
"""

import os
import base64
import html as _h

ROOT   = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CHARTS = os.path.join(ROOT, 'project', 'output')
SQL_F  = os.path.join(ROOT, 'code', 'schema.sql')
OUT_F  = os.path.join(ROOT, 'answers', 'answers.html')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def embed_chart(filename, caption):
    path = os.path.join(CHARTS, filename)
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    return (
        f'<figure>'
        f'<img src="data:image/png;base64,{b64}" alt="{_h.escape(caption)}">'
        f'<figcaption>{_h.escape(caption)}</figcaption>'
        f'</figure>'
    )

def sql_block(code):
    return f'<pre><code>{_h.escape(code.strip())}</code></pre>'


# ---------------------------------------------------------------------------
# Read and split schema.sql into DDL / Query1 / Query2
# ---------------------------------------------------------------------------
with open(SQL_F, encoding='utf-8') as f:
    full_sql = f.read()

q1_idx = full_sql.find('-- QUERY 1')
q2_idx = full_sql.find('-- QUERY 2')
sep1   = full_sql.rfind('-- ===', 0, q1_idx)
sep2   = full_sql.rfind('-- ===', 0, q2_idx)

ddl_sql = full_sql[:sep1].strip()
q1_sql  = full_sql[sep1:sep2].strip()
q2_sql  = full_sql[sep2:].strip()


# ---------------------------------------------------------------------------
# CSS  (plain string — kept outside f-strings to avoid {{ }} escaping)
# ---------------------------------------------------------------------------
CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px; line-height: 1.68; color: #1a1a2e;
    max-width: 980px; margin: 0 auto; padding: 36px 48px;
}
h1 {
    font-size: 20px; color: #0d47a1;
    border-bottom: 2.5px solid #0d47a1; padding-bottom: 10px; margin-bottom: 6px;
}
.subtitle { color: #555; font-size: 12px; margin-bottom: 20px; }
h2 {
    font-size: 15.5px; color: #fff; background: #1565c0;
    padding: 8px 14px; margin-top: 38px; margin-bottom: 14px; border-radius: 4px;
}
h3 { font-size: 13.5px; color: #1a237e; margin-top: 22px; margin-bottom: 8px; font-weight: 600; }
p  { margin: 8px 0; }
ul { margin: 8px 0 8px 22px; }
li { margin: 4px 0; }

/* Meta info box */
.meta-box {
    background: #e8eaf6; border-left: 5px solid #3949ab;
    border-radius: 0 6px 6px 0; padding: 16px 22px; margin-bottom: 32px;
}
.meta-box table { width: auto; margin: 8px 0 0; }
.meta-box td { padding: 3px 16px 3px 0; border: none; background: transparent; font-size: 13px; }
.meta-box td:first-child { font-weight: 600; color: #1a237e; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 12px; }
thead th {
    background: #1565c0; color: #fff; padding: 8px 11px;
    text-align: left; font-weight: 600;
}
tbody td { padding: 7px 11px; border: 1px solid #e0e0e0; vertical-align: top; }
tbody tr:nth-child(even) td { background: #f5f8ff; }

/* Code blocks */
pre {
    background: #f8f9fa; border: 1px solid #dde;
    border-left: 4px solid #1565c0; border-radius: 0 4px 4px 0;
    padding: 14px 16px; margin: 12px 0;
    font-size: 11px; white-space: pre-wrap;
    font-family: 'Consolas', 'Courier New', monospace;
}
code {
    background: #eef; padding: 1px 5px; border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace; font-size: 12px;
}
pre code { background: transparent; padding: 0; font-size: 11px; }

/* Callout boxes */
.finding {
    background: #e3f2fd; border-left: 4px solid #1976D2;
    padding: 11px 16px; margin: 14px 0; border-radius: 0 4px 4px 0;
}
.verdict {
    background: #e8f5e9; border-left: 4px solid #388e3c;
    padding: 11px 16px; margin: 14px 0; border-radius: 0 4px 4px 0;
}
.recommendation {
    background: #fff8e1; border-left: 4px solid #f9a825;
    padding: 11px 16px; margin: 14px 0; border-radius: 0 4px 4px 0;
}
.recommendation p { margin: 6px 0; }

/* Charts */
figure { margin: 18px 0; text-align: center; }
figure img {
    max-width: 100%; display: inline-block;
    border: 1px solid #e0e0e0; border-radius: 4px;
}
figcaption {
    font-size: 11px; color: #666; margin-top: 6px;
    font-style: italic; text-align: center;
}

/* Section dividers */
hr { border: none; border-top: 1px solid #ddd; margin: 28px 0; }

/* Print */
@media print {
    body { padding: 10px 18px; font-size: 12px; }
    pre  { font-size: 10px; }
    .page-break { page-break-before: always; padding-top: 10px; }
    h2 { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    thead th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    figure img { max-width: 90%; }
}
.page-break { page-break-before: always; padding-top: 10px; }
"""


# ---------------------------------------------------------------------------
# HTML body (f-string — CSS is already resolved before this point)
# ---------------------------------------------------------------------------
BODY = f"""
<!-- ===== HEADER ===== -->
<div class="meta-box">
  <h1>TravClan &mdash; Business Analyst Intern Technical Assessment</h1>
  <p class="subtitle">Submitted by <strong>Saurabh Sharma</strong></p>
  <table>
    <tbody>
      <tr><td>Author</td><td>Saurabh Sharma</td></tr>
      <tr><td>Role</td><td>Business Analyst Intern &mdash; Technical Round</td></tr>
      <tr><td>Dataset</td><td>hotel_bookings (1).csv &mdash; 12,000 records, 28 columns</td></tr>
      <tr><td>Sections</td><td>Section 1: Data Quality &nbsp;|&nbsp; Section 2: Cancellation Case Study &nbsp;|&nbsp; Section 3: SQL</td></tr>
    </tbody>
  </table>
</div>


<!-- ===================================================== -->
<!--  SECTION 1                                            -->
<!-- ===================================================== -->
<h2>Section 1 &mdash; Data Quality Checks</h2>

<h3>A1 &mdash; Invalid Stays Count</h3>
<p><strong>Footnote 1:</strong> A valid hotel stay requires at least one night.
Rows where <code>checkout_date &lt;= checkin_date</code> are data errors.</p>

<div class="finding">
  <strong>Answer: 120 bookings</strong> have <code>checkout_date &lt;= checkin_date</code>.
  These rows are excluded from all downstream revenue, occupancy, and stay-duration calculations.
</div>


<h3>A2 &mdash; Review Rating Range and Mean by Customer Segment</h3>
<p><strong>Footnote 6 (scale mismatch):</strong> Corporate customers rate on a <strong>1&ndash;10</strong> scale;
Individual and Group use <strong>1&ndash;5</strong>. Direct comparison is invalid without normalisation.
Corporate ratings are divided by 2 to bring all segments onto a common 1&ndash;5 scale.</p>

<table>
  <thead>
    <tr><th>Segment</th><th>Raw Min</th><th>Raw Max</th><th>Raw Mean</th><th>Scale</th><th>Normalised Mean</th><th>Reviews</th></tr>
  </thead>
  <tbody>
    <tr><td>Corporate</td><td>3.0</td><td>10.0</td><td>7.25</td><td>1&ndash;10</td><td><strong>3.62 (&divide; 2)</strong></td><td>1,287</td></tr>
    <tr><td>Group</td><td>1.0</td><td>5.0</td><td>3.77</td><td>1&ndash;5</td><td>3.77</td><td>590</td></tr>
    <tr><td>Individual</td><td>1.0</td><td>5.0</td><td>3.77</td><td>1&ndash;5</td><td>3.77</td><td>3,269</td></tr>
  </tbody>
</table>

<div class="finding">
  <strong>Implication:</strong> After normalisation, all three segments fall within 0.15 rating points of each other (3.62&ndash;3.77).
  The apparent Corporate advantage (7.25 vs 3.77) is entirely a scale artefact &mdash; there is no real satisfaction gap between segments.
</div>


<h3>A3 &mdash; Realized Revenue for Luxury Properties</h3>
<p>Three footnote filters must be applied before summing <code>total_amount</code>:</p>

<table>
  <thead><tr><th>Step</th><th>Filter Applied</th><th>Footnote</th><th>Rows Remaining</th></tr></thead>
  <tbody>
    <tr><td>Start</td><td>Full dataset</td><td>&mdash;</td><td>12,000</td></tr>
    <tr><td>1</td><td><code>checkout_date &gt; checkin_date</code></td><td>FN1</td><td>11,880</td></tr>
    <tr><td>2</td><td><code>num_rooms &gt; 0</code></td><td>FN3</td><td>11,821</td></tr>
    <tr><td>3</td><td><code>booking_status = 'Completed'</code></td><td>FN8</td><td>9,198</td></tr>
    <tr><td>4</td><td><code>property_type = 'Luxury'</code></td><td>&mdash;</td><td>1,063</td></tr>
  </tbody>
</table>

<table>
  <thead><tr><th>Metric</th><th>Amount</th></tr></thead>
  <tbody>
    <tr><td>Naive sum (no filters applied)</td><td>Rs. 1,17,431,484.47</td></tr>
    <tr><td><strong>Realized revenue (FN1 + FN3 + FN8 applied)</strong></td><td><strong>Rs. 90,694,052.93</strong></td></tr>
    <tr><td>Overstatement without filters</td><td>Rs. 26,737,431.54 &nbsp;(22.8% of naive total)</td></tr>
  </tbody>
</table>

<div class="finding">
  <strong>Answer: Rs. 90,694,052.93.</strong>
  The naive sum overstates realized revenue by <strong>22.8%</strong> because Cancelled and No-Show bookings carry a
  <code>total_amount</code> that was never collected (Footnote 8). This is the largest single source of revenue inflation.
</div>


<!-- ===================================================== -->
<!--  SECTION 2                                            -->
<!-- ===================================================== -->
<h2 class="page-break">Section 2 &mdash; Case Study: The Cancellation Crisis</h2>

<p>
  <strong>Context:</strong> Platform cancellation rate ~19.15% vs. industry benchmark 12%.
  Board target: reduce by 5 pp to ~14% within two quarters.
  Working dataset: <strong>11,821 rows</strong> (after FN1 + FN3), <strong>2,264 cancelled</strong> (19.15%).
  FN8 was intentionally <em>not</em> applied &mdash; cancel rates require all booking statuses, not only Completed rows.
</p>


<h3>A1 &mdash; Cancellation Landscape</h3>
<p><strong>Visualization 1 &mdash; City &times; Month heatmap:</strong>
Rows = <code>property_city</code>, columns = check-in month, cells = cancellation rate.
A heatmap reveals the worst city-month combination instantly without reading individual values.</p>

{embed_chart('a1_cancellation_heatmap.png', 'Figure 1 — Cancellation Rate by City × Month (darker = higher cancel rate)')}

<p><strong>Visualization 2 &mdash; Lead-time &times; Channel grouped bar:</strong>
X-axis = lead-time bucket (days before check-in), hue = booking channel, Y = cancellation rate.
Tests whether short-notice bookings and specific channels independently drive cancellation.</p>

{embed_chart('a1_leadtime_channel_bar.png', 'Figure 2 — Cancellation Rate by Lead-time Bucket and Booking Channel')}

<table>
  <thead><tr><th>Dimension</th><th>Primary Driver</th><th>Std-dev of Cancel Rate</th></tr></thead>
  <tbody>
    <tr><td><strong>City</strong> (strongest predictor)</td><td>Goa &mdash; highest within-city variance across months</td><td>0.1184</td></tr>
    <tr><td>Month</td><td>June &mdash; highest cross-city variance</td><td>0.1089</td></tr>
    <tr><td>Lead-time (secondary)</td><td>31&ndash;60 day bucket highest at ~23.8%</td><td>Smaller than city-month</td></tr>
  </tbody>
</table>

<div class="finding">
  <strong>A1 Answer:</strong> City &times; month interaction is the primary driver. Goa in Jun/Jul/Aug is the dominant hot zone.
  Lead-time is a secondary, platform-wide pattern &mdash; it does not explain the Goa spike.
</div>


<h3>A2 &mdash; Rate vs. Volume: Two Different Rankings</h3>
<p>Slices with fewer than 20 total bookings excluded to avoid spurious 100% rates on tiny samples.</p>

<table>
  <thead>
    <tr><th colspan="4" style="text-align:center;background:#283593;">Top 3 by Cancellation Rate (worst %)</th></tr>
    <tr><th>City &ndash; Month</th><th>Cancel Rate</th><th>Cancellations</th><th>Total Bookings</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Goa &ndash; Jun</strong></td><td><strong>50.9%</strong></td><td>28</td><td>55</td></tr>
    <tr><td>Goa &ndash; Aug</td><td>44.7%</td><td>38</td><td>85</td></tr>
    <tr><td>Goa &ndash; Jul</td><td>36.9%</td><td>24</td><td>65</td></tr>
  </tbody>
</table>

<table>
  <thead>
    <tr><th colspan="4" style="text-align:center;background:#283593;">Top 3 by Absolute Cancellation Count</th></tr>
    <tr><th>City &ndash; Month</th><th>Cancel Rate</th><th>Cancellations</th><th>Total Bookings</th></tr>
  </thead>
  <tbody>
    <tr><td>Goa &ndash; Aug</td><td>44.7%</td><td><strong>38</strong></td><td>85</td></tr>
    <tr><td>Chennai &ndash; Aug</td><td>22.2%</td><td><strong>37</strong></td><td>167</td></tr>
    <tr><td>Pune &ndash; Feb</td><td>24.0%</td><td><strong>37</strong></td><td>154</td></tr>
  </tbody>
</table>

<div class="finding">
  <strong>A2 Answer:</strong> The two lists are not identical. Goa-Aug appears in both.
  Chennai-Aug and Pune-Feb have moderate cancel rates (22&ndash;24%) but produce the same absolute count (37 each)
  because their booking volumes are 2&ndash;3&times; larger.
  For the board&rsquo;s 5 pp platform-wide target, <strong>volume matters more than rate</strong>.
  Fixing only the high-rate slices (Goa) removes ~90 cancellations;
  the remaining gap requires action on the high-volume slices too.
</div>


<h3>A3 &mdash; Root Cause Hypothesis Testing</h3>
<p><strong>Worst-rate slice:</strong> Goa in June &mdash; 50.9% cancel rate, 28 of 55 bookings cancelled.</p>
<ul>
  <li><strong>H1 &mdash; Lead-time effect:</strong> Are Goa-June bookings made unusually close to check-in?</li>
  <li><strong>H2 &mdash; Channel-mix effect:</strong> Is OTA over-represented in Goa-June?</li>
  <li><strong>H3 &mdash; City-season effect:</strong> Is this unique to the Goa &times; monsoon pairing?</li>
</ul>

{embed_chart('a3_hypothesis_comparison.png', 'Figure 3 — H1 Lead-time, H2 OTA Share, H3 City-Season Interaction')}

<table>
  <thead>
    <tr><th>Hypothesis</th><th>Metric</th><th>Goa &ndash; Jun (Worst)</th><th>Rest of Platform</th><th>Verdict</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>H1 &mdash; Lead-time</td><td>Median lead-time</td>
      <td>15 days</td><td>15 days</td>
      <td><strong>Ruled out</strong> &mdash; identical</td>
    </tr>
    <tr>
      <td>H2 &mdash; Channel mix</td><td>OTA share</td>
      <td>36.4%</td><td>35.4%</td>
      <td><strong>Ruled out</strong> &mdash; negligible gap</td>
    </tr>
    <tr>
      <td>H3 &mdash; City-season</td><td>vs. Goa other months</td>
      <td>50.9%</td><td>24.4%</td>
      <td rowspan="2"><strong>Supported</strong></td>
    </tr>
    <tr>
      <td></td><td>vs. Other cities in June</td>
      <td>50.9%</td><td>19.4%</td>
    </tr>
  </tbody>
</table>

<div class="verdict">
  <strong>A3 Answer &mdash; H3 is the only supported hypothesis.</strong><br>
  Goa in June cancels at 50.9% &mdash; <strong>2&times; its own annual average</strong> (24.4%) and
  <strong>2.6&times; other cities in the same month</strong> (19.4%).
  Lead-time is identical (15d vs 15d) and OTA share is negligible (36.4% vs 35.4%).
  Root cause: <strong>monsoon uncertainty</strong> &mdash; leisure travellers book Goa ahead of the season
  then cancel when monsoon forecasts deteriorate. Channel and advance notice do not explain it.
</div>


<h3>A4 &mdash; Board-Level Recommendation</h3>

<div class="recommendation">
  <p><strong>WHO:</strong> All bookings for Goa properties with check-in in June, July, or August
  (monsoon season &mdash; 205 bookings, 90 cancellations, 43.9% avg cancel rate).</p>
  <p><strong>WHAT:</strong> Require a non-refundable <strong>20% deposit</strong> at booking confirmation.
  Offer an optional <strong>Monsoon Flex add-on at Rs.&nbsp;499</strong> that restores full refundability
  for cancellations &ge; 7 days before check-in. Converts uncertain bookings into committed revenue
  while giving price-sensitive customers an opt-out path.</p>
</div>

<table>
  <thead>
    <tr><th>Scenario</th><th>Goa Jun&ndash;Aug cancellations reduced by</th><th>Prevented</th><th>New platform rate</th><th>Platform-wide reduction</th></tr>
  </thead>
  <tbody>
    <tr><td>Conservative</td><td>30% of 90</td><td>~27</td><td>~18.92%</td><td>~0.23 pp</td></tr>
    <tr><td>Optimistic</td><td>50% of 90</td><td>~45</td><td>~18.77%</td><td>~0.38 pp</td></tr>
  </tbody>
</table>

<p><strong>Risk:</strong> Deposit may suppress new Goa monsoon bookings from price-sensitive leisure travellers.
If OTA conversion in Goa Jun&ndash;Aug drops &gt;15%, lost booking value outweighs cancellation savings.<br>
<strong>Mitigation:</strong> A/B test on 50% of Goa monsoon traffic for 4 weeks; monitor OTA conversion before full rollout.</p>

<div class="finding">
  This single intervention closes <strong>0.23&ndash;0.38 pp</strong> of the 5 pp board target.
  Complementary policies for Chennai-Aug and Pune-Feb (37 cancellations each) would add ~0.47 pp,
  bringing the combined three-slice reduction to ~<strong>0.85 pp</strong>.
</div>


<!-- ===================================================== -->
<!--  SECTION 3                                            -->
<!-- ===================================================== -->
<h2 class="page-break">Section 3 &mdash; SQL Challenge</h2>

<h3>Schema Design: 28-Column CSV &rarr; 4 Normalised Tables</h3>

<table>
  <thead>
    <tr><th>Table</th><th>Primary Key</th><th>Columns extracted from bookings row</th><th>Approx. rows</th></tr>
  </thead>
  <tbody>
    <tr><td><code>customers</code></td><td><code>customer_id</code></td><td>name, segment, signup_date, home_city, loyalty_tier</td><td>~900 unique</td></tr>
    <tr><td><code>properties</code></td><td><code>property_id</code></td><td>name, city, star_rating, property_type, total_rooms</td><td>~60 unique</td></tr>
    <tr><td><code>bookings</code></td><td><code>booking_id</code></td><td>FK to above + all transaction columns</td><td>12,000</td></tr>
    <tr><td><code>reviews</code></td><td><code>review_id</code> (SERIAL)</td><td>review_rating, review_date &mdash; split out because ~34% of bookings have no review</td><td>~5,146</td></tr>
  </tbody>
</table>


<h3>CREATE TABLE Statements</h3>
{sql_block(ddl_sql)}


<h3>Index Justification</h3>
<table>
  <thead>
    <tr><th>Index</th><th>Column</th><th>Justification</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><code>idx_bookings_customer</code></td>
      <td><code>bookings(customer_id)</code></td>
      <td>Every query joining customers to bookings (loyalty reports, frequent-traveller queries) filters or groups on this FK.
      Without the index, each join scans all 12,000 booking rows.</td>
    </tr>
    <tr>
      <td><code>idx_bookings_property</code></td>
      <td><code>bookings(property_id)</code></td>
      <td>Revenue aggregation per property (Query 1) and occupancy reports partition on this column.
      FK columns without indexes cause sequential scans on the fact table.</td>
    </tr>
    <tr>
      <td><code>idx_bookings_status</code></td>
      <td><code>bookings(booking_status)</code></td>
      <td>Every revenue or cancellation query filters <code>WHERE booking_status = 'Completed'</code> (Footnote 8).
      The index reduces the qualifying scan to only the ~77% completed rows, skipping cancelled/no-shows.</td>
    </tr>
    <tr>
      <td><code>idx_bookings_checkin</code></td>
      <td><code>bookings(checkin_date)</code></td>
      <td>Date-range filters (monthly reports, year-over-year) and the <code>ORDER BY checkin_date</code>
      inside the LAG() window in Query 2 both reference this column. The index supports range scans and sort-avoidance.</td>
    </tr>
  </tbody>
</table>


<h3>Query 1 &mdash; Top Revenue Property per City &nbsp;<code>RANK()</code></h3>
<p>
  <strong>Business question:</strong> Which single property in each city generated the highest realized revenue?<br>
  <strong>Window function:</strong> <code>RANK() OVER (PARTITION BY property_city ORDER BY total_revenue DESC)</code>
  partitions results by city and assigns rank 1 to the top property. <code>RANK()</code> is used (not <code>ROW_NUMBER()</code>)
  so that tied properties both receive rank 1.
</p>
{sql_block(q1_sql)}

<table>
  <thead>
    <tr><th>City</th><th>property_id</th><th>Property Name</th><th>Total Revenue</th><th>Completed Bookings</th></tr>
  </thead>
  <tbody>
    <tr><td>Bangalore</td><td>2</td><td>The Grand Plaza</td><td>Rs. 13,957,983.73</td><td>192</td></tr>
    <tr><td>Chennai</td><td>53</td><td>Saffron Heights</td><td>Rs. 14,111,093.22</td><td>196</td></tr>
    <tr><td>Delhi</td><td>49</td><td>Mango Retreat</td><td>Rs. 4,153,549.17</td><td>150</td></tr>
    <tr><td>Goa</td><td>23</td><td>Sapphire Retreat</td><td>Rs. 19,481,171.66</td><td>169</td></tr>
    <tr><td>Jaipur</td><td>30</td><td>Ivory Retreat</td><td>Rs. 1,798,347.49</td><td>168</td></tr>
    <tr><td>Kochi</td><td>1</td><td>The Grand Plaza</td><td>Rs. 6,631,787.86</td><td>174</td></tr>
    <tr><td>Manali</td><td>10</td><td>Lotus Manor</td><td>Rs. 4,320,055.00</td><td>193</td></tr>
    <tr><td>Mumbai</td><td>11</td><td>Coral Palace</td><td>Rs. 10,575,127.65</td><td>191</td></tr>
    <tr><td>Pune</td><td>34</td><td>Velvet Palace</td><td>Rs. 5,921,213.85</td><td>161</td></tr>
    <tr><td>Udaipur</td><td>6</td><td>Hilltop Inn</td><td>Rs. 15,669,688.12</td><td>181</td></tr>
  </tbody>
</table>
<p><em>Note (Footnote 4):</em> &ldquo;The Grand Plaza&rdquo; appears for both Bangalore (id=2) and Kochi (id=1)
&mdash; same name, different cities, different IDs. This is why the query groups by <code>property_id</code>,
never by <code>property_name</code>.</p>


<h3>Query 2 &mdash; Frequent Customers &nbsp;<code>LAG()</code></h3>
<p>
  <strong>Business question:</strong> Which customers book repeatedly with an average gap of fewer than 30 days between completed check-in dates?<br>
  <strong>Window function:</strong> <code>LAG(checkin_date) OVER (PARTITION BY customer_id ORDER BY checkin_date)</code>
  retrieves the previous check-in date for the same customer. The date difference gives the gap in days.
  The first stay per customer yields NULL (no prior row) and is excluded by <code>WHERE gap_days IS NOT NULL</code>.
  <code>HAVING COUNT(gap_days) &ge; 1</code> requires at least two completed stays.
</p>
{sql_block(q2_sql)}

<p><strong>Result: 432 customers</strong> with avg inter-booking gap &lt; 30 days (of ~900 unique customers). Top 5:</p>
<table>
  <thead>
    <tr><th>customer_id</th><th>Name</th><th>Segment</th><th>Loyalty Tier</th><th>Total Stays</th><th>Avg Gap (days)</th></tr>
  </thead>
  <tbody>
    <tr><td>560</td><td>Customer_560</td><td>Individual</td><td>Silver</td><td>17</td><td>15.1</td></tr>
    <tr><td>319</td><td>Customer_319</td><td>Corporate</td><td>None</td><td>17</td><td>15.9</td></tr>
    <tr><td>268</td><td>Customer_268</td><td>Group</td><td>Gold</td><td>15</td><td>16.0</td></tr>
    <tr><td>702</td><td>Customer_702</td><td>Corporate</td><td>Silver</td><td>18</td><td>16.1</td></tr>
    <tr><td>113</td><td>Customer_113</td><td>Individual</td><td>Silver</td><td>22</td><td>16.7</td></tr>
  </tbody>
</table>

"""

# ---------------------------------------------------------------------------
# Assemble final HTML
# ---------------------------------------------------------------------------
DOC = (
    '<!DOCTYPE html>\n'
    '<html lang="en">\n'
    '<head>\n'
    '<meta charset="utf-8">\n'
    '<title>TravClan BA Assessment — Saurabh Sharma</title>\n'
    '<style>\n'
    + CSS +
    '</style>\n'
    '</head>\n'
    '<body>\n'
    + BODY +
    '\n</body>\n</html>\n'
)

os.makedirs(os.path.dirname(OUT_F), exist_ok=True)
with open(OUT_F, 'w', encoding='utf-8') as f:
    f.write(DOC)

size_kb = os.path.getsize(OUT_F) // 1024
print(f'Generated: {OUT_F}  ({size_kb} KB)')
print()
print('Next step:')
print('  1. Open answers/answers.html in Chrome or Edge')
print('  2. Ctrl+P  ->  Destination: Save as PDF')
print('  3. Save as  answers/answers.pdf')
