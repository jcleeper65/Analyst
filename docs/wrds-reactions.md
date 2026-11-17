# WRDS release reactions

Work in `Repos/Analyst`. The command is `wrds_reactions.py`; its optional packages
are in `requirements-wrds.txt`. It uses `wrds.Connection` and the WRDS login in
this repo's `.env`. It does not run the research agents or use a model.

```bash
python3.13 -m venv --system-site-packages .venv-wrds
.venv-wrds/bin/python -m pip install -r requirements-wrds.txt
```

Set `WRDS_USERNAME` and `WRDS_PASSWORD` locally in `.env`. Do not paste them in
chat or commit the file. To use another local credential file, pass `--env PATH`.

The saved Costco run read earnings 8-K `0000909832-26-000084`, Accepted on
September 24, 2026. The public manifest
`docs/reaction-releases/COST-before-2026-09-24.json` lists its eight immediately
preceding earnings releases, with each exact Accepted time and its EDGAR index
URL. These are SEC facts, not licensed CRSP observations.

Run the prepared release set locally:

```bash
.venv-wrds/bin/python wrds_reactions.py COST \
  --releases docs/reaction-releases/COST-before-2026-09-24.json \
  --output "$HOME/Library/Application Support/Analyst/CRSP/COST-prior-releases.txt" \
  --check
```

The output file must be outside the repository and must not already exist.
It is created with owner-only permissions. The `--check` output prints only
counts and PASS/NOT COMPUTED. The private file contains exactly one row per
release, followed by the median absolute reaction. Each row names the ticker,
Accepted time, two session close times, two prices and the signed reaction.
For a different company, supply its ticker and a manifest or a list of quoted
Accepted timestamps directly after the ticker.

The command selects exact US equity sessions, including holidays and early
closes. Before means strictly before the Accepted time; after means strictly
after. It queries CRSP CIZ `dsf_v2`, joined to the historical ticker intervals
in `stksecurityinfohist`. `--schema crsp_m_stock` can select a subscription's
monthly-update schema instead of `crsp`. There is no silent legacy-file fallback.
Both observations must have the same unambiguous security identifier, positive
finite prices, and the closing-trade flag. Bid/ask averages and substitute dates
are rejected. The reaction is `(after / before - 1) * 100`, using raw closing
prices, not CRSP total returns or dividend-adjusted returns. The median uses the
absolute reactions and is not computed unless every supplied release has both
valid closes. This exposes subscription/date-coverage gaps instead of silently
changing the sample.

## Under the hit-rate table in the product manual

Put the historical median absolute reaction under the hit-rate table, as the
[project page](https://cinderzhang.github.io/FIN67110-Fall2026/project.html)
requires for the base rate. State the sample, event window and CRSP source.
The licensed numeric result is deliberately absent from this repository and
chat. A team member can view the private output and place the permitted result
in the manual under the applicable license.

Status, November 16, 2026: WRDS authentication succeeded and the real pull ran
from Analyst. The accessible `crsp` annual schema supplied valid close pairs for
six of the eight releases. The March 5 and May 28, 2026 releases have no complete
pair in that pull. The command wrote all eight release rows and left the median
uncomputed; it did not silently use six observations for an eight-release median.

Monthly and quarterly access checks on `crsp_m_stock`, `crsp_q_stock`, `crspm`
and `crspq` all returned permission denied. A complete result requires CRSP
access covering the two missing releases. No other price source was substituted.
The private file named in the command above now exists and is owner-readable.
Choose a new output filename for a later run; the command does not overwrite it.
The public [execution status](reaction-releases/COST-before-2026-09-24-status.json)
contains only counts, public SEC identifiers and status, never CRSP price or
reaction values. No real median has been computed or claimed.

```bash
.venv-wrds/bin/python -m unittest discover -s tests -p test_wrds_reactions.py
```
