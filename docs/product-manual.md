# Product manual

## What the join changed: COST

**Publication result: the joined desk has not produced a final report.** Its
latest practice attempt stopped at worksheet judgment validation. This table
therefore makes a provisional comparison with the saved joined intermediates.
Those intermediates are not presented as an accepted final report. No missing
report has been assembled by hand and no failed run has been relabeled complete.

The name is Costco Wholesale (COST). The annual period is the 52 weeks ended
August 30, 2026. The quarter is the 16 weeks ended on that date. B means USD
billions; M means USD millions. Percentages are rounded for display. Comparisons
and arithmetic were checked before rounding.

- **Parts alone, frozen pre-join baseline:** the [November 5 verified team report](../equity_research_output/COSTCO%20WHOLESALE%20CORP%20_NEW%2C%202026-11-05%2C%2009-43-44%2C%20report%2011/verified_report.md)
  and [November 12 standalone worksheet](../equity_research_output/COSTCO%20WHOLESALE%20CORP%20_NEW%2C%202026-11-05%2C%2009-43-44%2C%20report%2011/Spinoff%20worksheet%2C%20COST%2C%202026-11-12%2C%2009-22-40.444799.md), saved together in report 11.
  These are the selected Week 4 baseline artifacts; they were not rerun or edited.
- **Joined candidate:** the [November 17 practice state](../runs/practice/COST_2026-11-17_17-50-49.261915/desk_run.json)
  records failure in `worksheet`: `Worksheet judgment failed: Unsupported numeric judgment`.
  Its [verified team report](../runs/practice/COST_2026-11-17_17-50-49.261915/verified_report.md) exists. Its
  [worksheet output](../runs/practice/COST_2026-11-17_17-50-49.261915/Spinoff%20worksheet%2C%20COST%2C%202026-11-17%2C%2017-50-49.261915.md) is a rejected intermediate. The judgment's
  Insight typed the year “2026”; this run never reached `final_report.md`.
- **Filing control:** the saved 10-K, 10-Q, and earnings exhibit are byte-identical
  between the two selected folders. The [evidence record](cost-join-comparison-evidence.json)
  contains their SHA-256 hashes, output identities, and recomputed values. This
  rules out a changed filing copy as the explanation for these comparisons.
- **Reading the table:** every second-column value below is provisional because
  no joined final report exists. In column one, Team and Worksheet are shown
  together. “—” means the worksheet does not report that core measure; it does
  not mean zero. The [audit checklist](../audit_checklist.md) defines rows 1–11.
  “View” and its deciding number in rows 12–13 mean the worksheet's value-versus-price
  view. The team's investment rating is identified separately.

Filing references below use the saved [10-K](../equity_research_output/COSTCO%20WHOLESALE%20CORP%20_NEW%2C%202026-11-05%2C%2009-43-44%2C%20report%2011/10-K.txt)
and [earnings exhibit](../equity_research_output/COSTCO%20WHOLESALE%20CORP%20_NEW%2C%202026-11-05%2C%2009-43-44%2C%20report%2011/earnings_release_Ex99-1.txt). The filed accessions are
[10-K 0000909832-26-000093](https://www.sec.gov/Archives/edgar/data/909832/000090983226000093/cost-20260830.htm)
and [8-K 0000909832-26-000084, Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/909832/000090983226000084/costex9918-k92426.htm).
A ratio or valuation is a calculation from filing inputs, not a figure the
filing directly states. The worksheet rate is an authored assumption.

| Parts alone: team / worksheet | Joined desk: final report **not produced**; saved intermediates only | Filing and check |
|---|---|---|
| **1. FY total revenue**<br>Team $303.154B / Worksheet — | Saved team $303.154B. No numeric change. | 10-K L1164–1167: total revenue $303,154M and $275,235M. |
| **2. FY revenue growth**<br>Team 10.1437% / Worksheet — | Saved team 10.1437%. No numeric change. | Same 10-K columns: (303,154 ÷ 275,235 − 1) × 100 = 10.1436953876%. |
| **3. FY operating income and margin**<br>Team $11.685B and 3.8545% / Worksheet — | Saved team $11.685B and 3.8545%. No numeric change. | 10-K L1177–1180 and L1164–1167: $11,685M ÷ $303,154M × 100 = 3.8544766027%. |
| **4. FY net income attributable to the company**<br>Team $9.226B / Worksheet $9.226B after-tax earnings | Saved team and worksheet $9.226B. No numeric change. | 10-K L1204–1210: net income $9,226M. The cached SEC companyfacts metadata identifies `NetIncomeLoss` as attributable to the parent. |
| **5. FY GAAP diluted EPS**<br>Team $20.76 / Worksheet — | Saved team $20.76. No numeric change. | 10-K L1219–1223: Diluted, $20.76 for FY2026 and $18.21 for FY2025. |
| **6. FY return on average equity**<br>Team 28.4021% / Worksheet — | Saved team 28.4021%. No numeric change. | 10-K L1204–1208 and L1386–1388: 9,226 ÷ ((35,803 + 29,164) ÷ 2) × 100 = 28.4021118414%. This uses average, not closing, equity. |
| **7. FY debt to equity**<br>Team 0.172108× / Worksheet — | Saved team 0.172108×. No numeric change. | 10-K L1331–1333, L1341–1343, L1386–1388: (2,248 + 3,914) ÷ 35,803 = 0.1721084825. This is long-term debt including its current portion, not every liability. |
| **8. FY free cash flow**<br>Team $9.382B / Worksheet — | Saved team $9.382B. No numeric change. | 10-K L1703–1711: $15,817M operating cash flow − $6,435M property/equipment spending = $9,382M. The worksheet's owner-cash-flow average is a different measure. |
| **9. Q4 total revenue**<br>Team 95,723 “USD as shown” / Worksheet — | 95,723 remains in the saved team's quarter-growth calculation inputs and quoted source. It is not a separate quarter-revenue statement. Value retained; presentation changed. | Exhibit L57–67 sets millions and the 16-week columns; L83–87 gives total revenue $95,723M, not rounded quarterly net sales. |
| **10. Q4 total-revenue growth**<br>Team 11.1043% / Worksheet — | Saved team 11.1043%. No numeric change. | Exhibit L83–87: (95,723 ÷ 86,156 − 1) × 100 = 11.1042759645%. This differs from the release's headline net-sales growth because the measure differs. |
| **11. Q4 GAAP diluted EPS**<br>Team $6.75, citing the Basic row at L137; its Verifier flags that citation / Worksheet — | $6.75 appears in the release quote attached to the saved team's refund calculation, at L44. It is not a separate Q4-EPS claim. Value retained; source/presentation changed. | Exhibit L44 explicitly says fourth-quarter per-diluted-share earnings $6.75. L144–148 labels Diluted and gives $6.75. Basic at L135–139 also happens to be $6.75, but is the wrong row for a diluted-EPS citation. The new supporting citation is appropriate. |
| **12. Worksheet view**<br>Team rating Hold / Worksheet **less than the price** | Saved team Hold. The rejected worksheet's code-computed view is **less than the price**. Both views are unchanged, but neither is a published joined final report. | A filing does not state an investment view. The low value in row 13 is below both saved worksheet-date closes. Those prices come from the saved reader, not the filing. |
| **13. Number deciding the worksheet view**<br>Worksheet low value **$115.737463073489/share** | Rejected worksheet low value **$115.737463073489/share**. The stored values match exactly. | 10-K L86–87 gives 443,129,349 shares. L1204–1210, L1660–1663, L1708–1717 supply the annual inputs. Owner cash flows $5,465M, $5,027M, $4,894M average $5,128.666667M. Divide by the [authored 10% rate and share count](../runs/practice/COST_2026-11-17_17-50-49.261915/inputs/Repos/Analyst/spinoff-rules.md#L16-L18): $115.737463073489/share. The rate and averaging policy are assumptions, not filing facts. |

### What changed, and what did not

The thirteen financial/view values show **no numerical transformation** in the
saved intermediates. On those quantities the join has pipeline behavior; this
table does not demonstrate a new numerical tool. Rows 9 and 11 show changed
presentation: direct claims became supporting calculation/source text. The
Q4 diluted-EPS source is more appropriate, although the value is unchanged.

The team's **deciding metric** did change outside the worksheet's deciding-number
row. The standalone team chose free cash flow of $9.382B; the joined team chose
P/E of 43.18304431599229×. Both rated Hold. The new P/E equals a saved pre-filing
LSEG close of $896.48 on September 24 divided by filed annual EPS of $20.76.
The [saved price provenance](../runs/practice/COST_2026-11-17_17-50-49.261915/market_price.json) puts that close at
16:00 Eastern, before the release's accepted time of 16:17:37. The price is not
from the filing. This is a changed selection with supported arithmetic, not a
correction of the original free-cash-flow number. The comparison also includes
changed reader availability, prompt changes, and fresh model calls. It does not
isolate the join as the cause of that selection change.

The worksheet-date prices also differ: $1,087.61 on November 11 in the standalone
worksheet and $1,113.74 on November 16 in the joined intermediate. Both exceed
the same low value. This is a different observation date, not a changed valuation
formula. The view is unchanged. Do not confuse either worksheet-date price with
the pre-filing close used by the team's P/E.

The material operational change is **publication availability**: the standalone
parts delivered saved outputs; the joined command withheld its final report.
The latest failure is the judgment's bare year, not a changed financial input.
An intermediate comparison cannot establish the behavior of a published joined
report. Until an accepted final exists, the requested final-to-standalone
comparison remains incomplete. The table records that limit rather than
substituting a successful team substage for the joined result.

This is a learning exercise, not financial advice.

AI assistance: OpenAI Codex. Codex checked the cited saved evidence and recalculated the figures in Python.

Any remaining errors are my own.
