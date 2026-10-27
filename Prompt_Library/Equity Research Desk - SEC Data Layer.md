# Equity Research Desk: SEC Data Layer

Build the data-collection and calculation layer of an equity-research desk in Python. Model the workflow on Section 3.1 of Francis and Zhang (2026). Do not add analyst or model roles; those will be specified later.

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
4. Fetch XBRL company facts. For the latest fiscal year reported for revenue, print total revenue, operating income, net income, diluted EPS, stockholders' equity, long-term debt, the current portion of long-term debt, cash from operations, and additions to property and equipment. For each fact, print its XBRL tag, period end, filing accession, and prior-year value. Select among candidate tags for each concept by using the tag with the newest latest-year observation. Use the same fiscal year as revenue for all concepts and include the prior fiscal year beside each value.
5. Calculate and print the arithmetic for revenue growth, operating margin, return on average equity, debt to equity with the current portion included, free cash flow (cash from operations minus additions to property and equipment), and P/E using `--price` and diluted EPS. Show the inputs and result for every calculation.
6. From the earnings-release text, print the lines that state quarterly total revenue and diluted EPS.
7. For each peer, print the same XBRL facts and calculate operating margin with the same definition used for the primary ticker.

## Saved outputs

- Save the primary company's facts beside the three text files.
- Include the selected tags, fiscal periods, filing accessions, and prior-year values in the saved facts.
- Save output in the dated company folder created for the run.

## Completion response

When implementation is complete, state the exact command to install any required Python packages and the exact command to run the program with a ticker, peers, and a price.
