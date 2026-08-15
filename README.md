# HCES-2022-23
An analysis of Household consumption of Indian households- Data from Household Consumption Expenditure survey 2022-23 
# India Household Consumption Expenditure Dashboard: HCES 2022-23

An end-to-end market research analytics project built on India's official **Household
Consumption Expenditure Survey (HCES) 2022-23** — the same dataset MoSPI/NSSO uses to
publish the country's headline poverty and consumption statistics.

The project covers the full pipeline: raw government survey files → Python ETL →
MySQL → Power BI dashboard, with a strong emphasis on **data validation** as some values are checked against officially published figures, not
just assumed correct.

---

## What this project answers

- How does household spending differ between the poorest and richest income segments?
- How does the *category mix* of spending shift as income rises (food vs. durable
  goods vs. education vs. housing)?
- How do rural and urban India differ in spending patterns?
- Which states have the highest/lowest average consumption expenditure?

---

## Tech stack

| Layer | Tools |
|---|---|
| Extract & Transform | Python, pandas, NumPy |
| Storage / Querying | MySQL |
| Visualization | Power BI |
| Source data | HCES 2022-23 unit-level microdata, MoSPI/NSSO (via microdata.gov.in) |

---

## Pipeline architecture

```
explore_extract.ipynb              -- loads & caches raw HCES level files (CSV -> Parquet)
hces_column_mapping.py  -- renames ~460 cryptic survey column codes to readable names
transform.py            -- computes MPCE using the official MoSPI formula,
                            applies survey weights, builds income quintiles
category_analysis.py    -- builds category-wise spend breakdown by segment
analyics.sql  -- SQL queries (GROUP BY, JOINs, window functions, CTEs)

```

Each script has a single responsibility (separation of concerns) and is independently
testable — `extract.py` doesn't know about MPCE math, `transform.py` doesn't know
about file formats.

---

## Methodology & data validation (the core of this project)
Data validation was done at various points

1. **Official MPCE formula** — implemented MoSPI's exact estimation formula
   (`TE = E1 + (E2/P2)×P1 + (E3/P3)×P1`) from the published *Survey Methodology &
   Estimation Procedure* document, rather than simply summing item-level values.

2. **Mixed Reference Period correction** — HCES records different item categories
   over different recall windows (7-day, 30-day, or 365-day). An initial
   section-number-based assumption about which items were 365-day was tested,
   found wrong, and corrected by tracing the issue back to the **actual government
   questionnaire** (Appendix A, FDQ/CSQ/DGQ schedules) and its official item-level
   summary table — correcting several real misclassifications (e.g., fuel & light
   and processed food were being incorrectly annualized; education and medical
   hospitalisation expenses were not being annualized when they should have been).

3. **Outlier treatment** — extreme high-value households (large durable goods
   purchases, imputed housing values) were identified, investigated (confirmed as
   legitimate values, not data errors, tied to the survey's deliberate oversampling
   of wealthy urban households), and handled via documented, sector-specific
   winsorization — with category-level values scaled consistently to avoid a single
   outlier household distorting the category-share breakdown.

4. **Validation against published figures** — final computed MPCE landed within
   **2.2% of the official rural figure and 2.2%/0.9% of the official urban figure**
   (₹3,773 rural / ₹6,459 urban, per the official HCES 2022-23 report), depending on
   configuration. A known, disclosed gap remains in the rural estimate (~19.6%),
   attributed to a documented simplification (using the first-visit survey weight as
   an approximation for the official "third-visit" weight, since visit-order data
   wasn't available at the household level).

---

## Key findings

- **Engel's Law holds clearly**: food's share of household budget falls sharply from
  the poorest to richest quintile in both rural and urban India.
- **Durable goods and "Conveyance/Services/Rent" spending rise sharply with income**
  — in the richest quintile, these categories can account for 45%+ of total spend.
- **Education & institutional medical spend** shows the steepest relative growth
  across quintiles, more than tripling as a budget share from poorest to richest.
- Urban households consistently show higher MPCE than rural households across every
  quintile, with the gap widening at higher income levels.

---

## Dashboard

Built in Power BI, includes:
- KPI cards (overall / rural / urban weighted average MPCE, households represented)
- Category spend share by MPCE quintile (stacked bar, rural/urban toggle)
- MPCE by quintile (rural vs. urban comparison)
- MPCE by state (ranked, with state names)
- Interactive sector slicer driving all visuals via a shared dimension table

<img width="1373" height="741" alt="image" src="https://github.com/user-attachments/assets/24c77d91-84d4-4117-9ac0-a7f1b80596c5" />

---

## Known limitations

- Rural MPCE estimate is ~19.6% below the officially published figure; urban is
  within ~1-2%. See Methodology section above for the documented cause.
- Item-code-to-category mapping for durable goods sections (13-14) is based on the
  general official reference-period rule.
  item-by-item check the way sections 5-12 were.
- State names use a general code lookup

---

## Data source

Household Consumption Expenditure Survey (HCES) 2022-23, Ministry of Statistics and
Programme Implementation (MoSPI), Government of India. Unit-level data accessed via
[microdata.gov.in](https://microdata.gov.in).
