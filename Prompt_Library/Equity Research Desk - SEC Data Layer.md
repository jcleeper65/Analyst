# Equity Research Desk: SEC Data Layer

Build the data-collection, calculation, and model-analysis layer of an equity-research desk in Python. Model the workflow on Section 3.1 of Francis and Zhang (2026).

## Inputs and request settings

- Accept a ticker as the positional command-line argument.
- Accept an optional `--peers` list of ticker symbols.
- Accept an optional `--price` number for the P/E calculation.
- Accept an optional `--step` value from 1 to 7. When supplied, run only that step.
- Read `SEC_USER_AGENT` from the `.env` file in the project folder. Send this User-Agent on every SEC request. Do not hard-code a company name or ticker in the program.

## Seven workflow steps

Print each step as it runs.

1. Resolve the input ticker to its CIK using SEC's `company_tickers.json`.
2. List the company's EDGAR filings through the submissions API. Select the latest 10-K, latest 10-Q, and latest 8-K whose filing document reports Item 2.02. For each filing, print its accession number and the `Accepted` time shown on its EDGAR index page.
3. Download the selected 10-K and 10-Q documents, plus Exhibit 99.1 from the selected 8-K as the earnings release. Convert each document to plain text. Save the three text files in a folder named with the company name and the run date and time.
4. Fetch XBRL company facts. For the latest fiscal year reported for revenue, print total revenue, operating income, consolidated net income, net income attributable to the parent, noncontrolling-interest income when reported, diluted EPS, parent stockholders' equity, long-term debt, the current portion of long-term debt, separate short-term borrowings, cash from operations, and additions to property and equipment. Use full-year 10-K duration facts for duration concepts; exclude quarter and year-to-date facts and any dimensional facts. For revenue, prefer the `Revenues` tag when it reports total revenue for the latest fiscal year. Do not treat a net-sales tag as total revenue when a total-revenue fact is available. If `Revenues` is not available for the latest fiscal year, choose the supported top-line candidate with the newest period end and print its tag. For debt, include complete-total concepts such as `LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities` when the filer uses them. For each fact, print its XBRL tag, period end, filing accession, and prior-year value. Use the same fiscal year as revenue for all concepts. For each prior-year value, require a period end exactly one calendar year before the current period end; if no fact exists for that exact date, print `n/a`. Map February 29 to February 28 when the prior year is not a leap year. Use parent-attributable net income with parent equity for ROE. If parent-attributable net income is not directly tagged but noncontrolling-interest income is tagged, compute it as consolidated net income minus noncontrolling-interest income and cite both inputs.
5. Calculate and print the arithmetic for revenue growth, operating margin, return on average equity, debt to equity, free cash flow (cash from operations minus additions to property and equipment), and P/E using `--price` and diluted EPS. Show the inputs and result for every calculation. Label ROE as the program's computed method: reported net income divided by the simple average of current and prior year-end stockholders' equity. State that this can differ from reported average common ROE when equity includes preferred stock or the issuer uses a year-average denominator. For debt to equity, use `LongTermDebt` as the complete amount when present and do not add current maturities again. Otherwise use `LongTermDebtNoncurrent + LongTermDebtCurrent`. Also use a supported complete-total debt concept when the issuer uses a different tag. Add separately reported short-term borrowings only when a complete long-term debt base is available. If long-term debt is unavailable, print `n/a`; do not report short-term borrowings alone as total debt. Define the standard ratio to exclude repos and other secured financings, and state this exclusion in the output. If a financial institution has no operating-income line, label operating margin as not applicable to that financial institution; do not substitute pre-tax income.
6. From the earnings release, print actual results for the latest reported quarter: reported revenue and GAAP diluted EPS. Exclude forecasts and guidance. If the release reports these values in a table, identify the latest quarter chronologically, use the reported (not managed) revenue row, and use the diluted EPS row. Do not select adjusted or non-GAAP EPS in place of GAAP diluted EPS. If the release also reports adjusted EPS, flag it separately and state that it was not used.
7. For each peer, print the same XBRL facts and calculate operating margin with the same definition used for the primary ticker.

## Saved outputs

- Save the primary company's facts beside the three text files.
- Include the selected tags, fiscal periods, filing accessions, and prior-year values in the saved facts.
- Save output in the dated company folder created for the run.

## Source and calculation rules

- Label every derived ratio or amount as `Computed`.
- Print the source for every input beside the calculation. For SEC facts, include the XBRL tag, period end, and filing accession. For price, identify the `--price` command-line argument as the source.
- Do not present a computed number if any numeric input has no source. A Manager role added later must refuse to compile a computed number when any of its inputs lacks a source.

## Model roles and report

- After the seven SEC data steps, use the official OpenAI Python SDK. Read `API_KEY` from the project `.env`; allow `OPENAI_MODEL` to select the model, with `gpt-5.5` as the default. Store prompts in code and keep each call independent.
- Run four separate roles: Research Analyst, Financial Analyst, Investment Advisor, and Strategy Manager. Print each role name as it runs.
- Give each role its own instructions. Send each role only a Strategy Manager task envelope encoded as JSON with `task`, `context`, and `expected_output`.
- Research Analyst uses the 10-K Business and MD&A sections and earnings release. Cover business model, competitive position, catalysts, and recent developments. Quote and cite a source line for every factual claim.
- Financial Analyst uses only the Step 4 facts, Step 5 calculator outputs, Step 6 quarter, and Step 7 peers. Cite every number to its filing accession and XBRL tag with period end, or to an earnings-release line. Show the supplied arithmetic for each ratio. Do not calculate in the model. It may request another ratio from the Python calculator.
- Investment Advisor receives only the Research Analyst and Financial Analyst outputs. Give a thesis, a Buy, Hold, or Sell rating, and one cited deciding number.
- Strategy Manager checks that Overview; Market Positioning and Growth Outlook; Valuation Insights; Future Developments and Strategic Recommendations; and Investment Recommendation are present and consistent. Send each failing part to its role once, then compile the report.
- Save the Markdown report in the run folder. Its first line lists the filings read and their accession numbers. Its second line gives the run time. Print the report path.

## Completion response

When implementation is complete, state the exact command to install any required Python packages and the exact command to run the program with a ticker, peers, and a price.
