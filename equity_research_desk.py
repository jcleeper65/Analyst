#!/usr/bin/env python3
"""SEC data collection and calculations for an equity research desk."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


SEC_BASE = "https://www.sec.gov"
DATA_BASE = "https://data.sec.gov"
COMPANY_TICKERS_URL = f"{SEC_BASE}/files/company_tickers.json"
CONCEPTS: dict[str, dict[str, Any]] = {
    # Prefer total Revenues when a filer reports it. Fall back to other
    # standard revenue concepts when that tag is unavailable for a peer.
    "revenue": {"tags": ["Revenues", "RevenuesNetOfInterestExpense", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet", "RevenueFromContractWithCustomerIncludingAssessedTax"], "kind": "duration", "unit": "USD"},
    "operating_income": {"tags": ["OperatingIncomeLoss"], "kind": "duration", "unit": "USD"},
    "net_income": {"tags": ["ProfitLoss", "NetIncomeLoss"], "kind": "duration", "unit": "USD"},
    "noncontrolling_interest_income": {"tags": ["NetIncomeLossAttributableToNonredeemableNoncontrollingInterest", "NetIncomeLossAttributableToRedeemableNoncontrollingInterest"], "kind": "duration", "unit": "USD"},
    "net_income_attributable_to_parent": {"tags": ["NetIncomeLossAttributableToParent", "NetIncomeLoss"], "kind": "duration", "unit": "USD"},
    "diluted_eps": {"tags": ["EarningsPerShareDiluted"], "kind": "duration", "unit": "USD/shares"},
    "stockholders_equity": {"tags": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "kind": "instant", "unit": "USD"},
    "long_term_debt": {"tags": ["LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", "LongTermDebtNoncurrent", "LongTermDebtAndFinanceLeaseObligationsNoncurrent"], "kind": "instant", "unit": "USD"},
    "current_portion_of_long_term_debt": {"tags": ["LongTermDebtCurrent", "LongTermDebtAndFinanceLeaseObligationsCurrent"], "kind": "instant", "unit": "USD"},
    "short_term_borrowings": {"tags": ["ShortTermBorrowings"], "kind": "instant", "unit": "USD"},
    "cash_from_operations": {"tags": ["NetCashProvidedByUsedInOperatingActivities"], "kind": "duration", "unit": "USD"},
    "additions_to_property_and_equipment": {"tags": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "PaymentsForProceedsFromProductiveAssets"], "kind": "duration", "unit": "USD"},
}


@dataclass
class Filing:
    form: str
    accession: str
    filed: str
    primary_document: str
    accepted: str = ""
    index_url: str = ""
    document_url: str = ""
    release_document: str = ""
    release_url: str = ""


class Desk:
    def __init__(self, ticker: str, peers: list[str], price: float | None):
        load_dotenv(Path(__file__).with_name(".env"))
        user_agent = os.getenv("SEC_USER_AGENT", "").strip()
        if not user_agent:
            raise ValueError("SEC_USER_AGENT is missing or empty in .env")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
        self.ticker = ticker.upper()
        self.peers = [p.upper() for p in peers]
        self.price = price
        self.company_tickers: dict[str, dict[str, Any]] = {}
        self.cik = ""
        self.company = ""
        self.submissions: dict[str, Any] = {}
        self.filings: dict[str, Filing] = {}
        self.facts: dict[str, Any] = {}
        self.report_period = ""
        self.output_dir: Path | None = None

    def get(self, url: str) -> requests.Response:
        response = self.session.get(url, timeout=45)
        response.raise_for_status()
        return response

    def resolve_ticker(self, ticker: str) -> tuple[str, str]:
        if not self.company_tickers:
            data = self.get(COMPANY_TICKERS_URL).json()
            self.company_tickers = {str(row["ticker"]).upper(): {"cik": str(row["cik_str"]).zfill(10), "name": row["title"]} for row in data.values()}
        result = self.company_tickers.get(ticker.upper())
        if not result:
            raise ValueError(f"Ticker {ticker} was not found in SEC company_tickers.json")
        return result["cik"], result["name"]

    def get_submissions(self, cik: str) -> dict[str, Any]:
        data = self.get(f"{DATA_BASE}/submissions/CIK{cik}.json").json()
        recent = data.get("filings", {}).get("recent", {})
        records = [{k: recent[k][i] for k in recent} for i in range(len(recent.get("form", [])))]
        for old in data.get("filings", {}).get("files", []):
            older = self.get(f"{DATA_BASE}/submissions/{old['name']}").json()
            block = older.get("filings", older)
            rec = block.get("recent", block)
            records.extend({k: rec[k][i] for k in rec} for i in range(len(rec.get("form", []))))
        data["_records"] = records
        return data

    @staticmethod
    def archive_root(cik: str, accession: str) -> str:
        return f"{SEC_BASE}/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}"

    def index_info(self, cik: str, accession: str) -> tuple[str, list[dict[str, str]]]:
        url = f"{self.archive_root(cik, accession)}/{accession}-index.html"
        soup = BeautifulSoup(self.get(url).content, "html.parser")
        text = soup.get_text(" ", strip=True)
        match = re.search(r"Accepted\s*:?\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", text, re.I)
        accepted = match.group(1) if match else "Not shown on index page"
        files: list[dict[str, str]] = []
        for row in soup.select("table tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue
            link = cells[2].find("a", href=True)
            if not link:
                continue
            files.append({"name": link.get_text(" ", strip=True), "href": link["href"], "description": cells[3].get_text(" ", strip=True) if len(cells) > 3 else ""})
        return accepted, files

    def step1(self) -> None:
        print("Step 1/7: Resolve ticker to CIK.", flush=True)
        self.cik, self.company = self.resolve_ticker(self.ticker)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", self.company).strip("_")
        self.output_dir = Path(__file__).with_name("equity_research_output") / f"{safe_name}_{stamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"  {self.ticker} resolves to CIK {self.cik} ({self.company}).")

    def step2(self) -> None:
        print("Step 2/7: Find latest 10-K, 10-Q, and qualifying earnings 8-K.", flush=True)
        if not self.cik:
            self.cik, self.company = self.resolve_ticker(self.ticker)
        self.submissions = self.get_submissions(self.cik)
        records = sorted(self.submissions["_records"], key=lambda x: x.get("filed", ""), reverse=True)
        chosen: dict[str, Filing] = {}
        for row in records:
            form = row.get("form", "")
            if form not in {"10-K", "10-Q", "8-K"} or form in chosen:
                continue
            accession = row["accessionNumber"]
            accepted, files = self.index_info(self.cik, accession)
            root = self.archive_root(self.cik, accession)
            primary = row.get("primaryDocument", "")
            doc_url = f"{root}/{primary}" if primary else ""
            filing = Filing(form, accession, row.get("filingDate", ""), primary, accepted, f"{root}/{accession}-index.html", doc_url)
            if form == "8-K":
                primary_text = BeautifulSoup(self.get(doc_url).content, "html.parser").get_text(" ", strip=True) if doc_url else ""
                if not re.search(r"Item\s*2\.02\b", primary_text, re.I):
                    continue
                exhibit = next((f for f in files if re.search(r"EX-99\.1|99\.1", f["description"] + " " + f["name"], re.I)), None)
                if not exhibit:
                    continue
                filing.release_document = exhibit["name"]
                filing.release_url = f"{root}/{exhibit['name']}"
            chosen[form] = filing
        missing = {f for f in ("10-K", "10-Q", "8-K") if f not in chosen}
        if missing:
            raise RuntimeError(f"Could not find required filings: {', '.join(sorted(missing))}")
        self.filings = chosen
        print("  Latest qualifying filings (accession | EDGAR Accepted time):")
        for form in ("10-K", "10-Q", "8-K"):
            f = chosen[form]
            print(f"  {form} | {f.accession} | {f.accepted} | filed {f.filed}")

    @staticmethod
    def html_to_text(content: bytes) -> str:
        soup = BeautifulSoup(content, "html.parser")
        for node in soup(["script", "style", "ix:header"]):
            node.decompose()
        return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())

    def ensure_output(self) -> None:
        if self.output_dir is None:
            _, company = self.resolve_ticker(self.ticker)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", company).strip("_")
            self.output_dir = Path(__file__).with_name("equity_research_output") / f"{safe_name}_{stamp}"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def step3(self) -> None:
        print("Step 3/7: Download filings, convert to plain text, and save them.", flush=True)
        if not self.filings:
            self.step2()
        self.ensure_output()
        names = {"10-K": "10-K.txt", "10-Q": "10-Q.txt", "8-K": "earnings_release_Ex99-1.txt"}
        saved = {}
        for form, filing in self.filings.items():
            url = filing.release_url if form == "8-K" else filing.document_url
            txt = self.html_to_text(self.get(url).content)
            path = self.output_dir / names[form]
            path.write_text(txt, encoding="utf-8")
            saved[form] = str(path)
            print(f"  Saved {form}: {path}")
        print(f"  Downloaded and converted 3 filing documents to plain text in {self.output_dir}.")

    def get_company_facts(self, cik: str) -> dict[str, Any]:
        return self.get(f"{DATA_BASE}/api/xbrl/companyfacts/CIK{cik}.json").json()

    @staticmethod
    def fact_rows(facts: dict[str, Any], tag: str, unit: str, kind: str) -> list[dict[str, Any]]:
        concept = facts.get("facts", {}).get("us-gaap", {}).get(tag)
        if not concept:
            return []
        rows = concept.get("units", {}).get(unit, [])
        out = []
        for row in rows:
            if row.get("form") != "10-K" or not row.get("fy"):
                continue
            # Company Facts normally exposes standard, entity-wide facts only.
            # Keep this guard for payloads that include dimensional metadata.
            if row.get("segment") or row.get("dimensions"):
                continue
            start = row.get("start")
            # Keep full-year 10-K durations only. This excludes quarterly and
            # year-to-date contexts that can share the same fiscal-year end.
            if kind == "duration" and (not start or not (350 <= (datetime.fromisoformat(row["end"]) - datetime.fromisoformat(start)).days <= 380)):
                continue
            out.append(row)
        return out

    def select_fact(self, facts: dict[str, Any], metric: str) -> tuple[str | None, list[dict[str, Any]]]:
        spec = CONCEPTS[metric]
        candidates = []
        for tag in spec["tags"]:
            rows = self.fact_rows(facts, tag, spec["unit"], spec["kind"])
            if rows:
                candidates.append((max(r["end"] for r in rows), tag, rows))
        if not candidates:
            return None, []
        _, tag, rows = max(candidates, key=lambda x: (x[0], -spec["tags"].index(x[1])))
        return tag, rows

    def get_fy_fact(self, rows: list[dict[str, Any]], target_end: str, previous: bool = False) -> dict[str, Any] | None:
        if not rows:
            return None
        if not previous:
            # Require the exact revenue period end so every current metric
            # belongs to the same fiscal year-end.
            matches = [r for r in rows if r.get("end") == target_end]
        else:
            target_date = datetime.fromisoformat(target_end).date()
            try:
                prior_end = target_date.replace(year=target_date.year - 1).isoformat()
            except ValueError:
                # A February 29 period end maps to February 28 in a non-leap year.
                prior_end = target_date.replace(year=target_date.year - 1, day=28).isoformat()
            matches = [r for r in rows if r.get("end") == prior_end]
        if not matches:
            return None
        return max(matches, key=lambda r: r.get("filed", ""))

    def compile_facts(self, facts: dict[str, Any]) -> tuple[dict[str, Any], str, int]:
        _, rev_rows = self.select_fact(facts, "revenue")
        if not rev_rows:
            raise RuntimeError("No annual revenue fact was found in company facts")
        rev_latest = max(rev_rows, key=lambda r: (r["end"], r.get("filed", "")))
        target_end, target_fy = rev_latest["end"], int(rev_latest["fy"])
        output: dict[str, Any] = {}
        for metric, spec in CONCEPTS.items():
            tag, rows = self.select_fact(facts, metric)
            current = self.get_fy_fact(rows, target_end) if rows else None
            prior = self.get_fy_fact(rows, target_end, previous=True) if rows else None
            output[metric] = {"tag": tag, "period_end": current.get("end") if current else target_end, "fy": target_fy, "filing": current.get("accn") if current else None, "value": current.get("val") if current else None, "prior_period_end": prior.get("end") if prior else None, "prior_filing": prior.get("accn") if prior else None, "prior_value": prior.get("val") if prior else None}
        parent = output["net_income_attributable_to_parent"]
        if parent["value"] is None:
            consolidated = output["net_income"]
            nci = output["noncontrolling_interest_income"]
            if consolidated["value"] is not None and nci["value"] is not None:
                parent["value"] = consolidated["value"] - nci["value"]
                parent["tag"] = f"computed from {consolidated['tag']} less {nci['tag']}"
                parent["period_end"] = consolidated["period_end"]
                accessions = list(dict.fromkeys(x for x in (consolidated["filing"], nci["filing"]) if x))
                parent["filing"] = ", ".join(accessions) or None
                if consolidated["prior_value"] is not None and nci["prior_value"] is not None and consolidated["prior_period_end"] == nci["prior_period_end"]:
                    parent["prior_value"] = consolidated["prior_value"] - nci["prior_value"]
                    parent["prior_period_end"] = consolidated["prior_period_end"]
                    prior_accessions = list(dict.fromkeys(x for x in (consolidated["prior_filing"], nci["prior_filing"]) if x))
                    parent["prior_filing"] = ", ".join(prior_accessions) or None
                    parent["tag"] += f"; prior computed from {consolidated['tag']} less {nci['tag']}"
            elif consolidated["value"] is not None:
                # No noncontrolling-interest income fact was reported, so use
                # consolidated net income as parent-attributable net income.
                parent.update({"value": consolidated["value"], "tag": f"{consolidated['tag']} (no NCI income fact reported)", "period_end": consolidated["period_end"], "filing": consolidated["filing"], "prior_value": consolidated["prior_value"], "prior_period_end": consolidated["prior_period_end"], "prior_filing": consolidated["prior_filing"]})
        return output, target_end, target_fy

    @staticmethod
    def number(value: Any) -> str:
        return "n/a" if value is None else f"{value:,.4f}" if isinstance(value, float) else f"{value:,.2f}"

    @staticmethod
    def fact_source(item: dict[str, Any], prior: bool = False) -> str:
        tag = item.get("tag")
        period_end = item.get("prior_period_end" if prior else "period_end")
        accession = item.get("prior_filing" if prior else "filing")
        if not tag or not period_end or not accession:
            return "source unavailable"
        return f"XBRL tag {tag}, period end {period_end}, filing {accession}"

    @classmethod
    def has_fact_source(cls, item: dict[str, Any], prior: bool = False) -> bool:
        return cls.fact_source(item, prior) != "source unavailable"

    @classmethod
    def input_value(cls, item: dict[str, Any], prior: bool = False) -> str:
        value_key = "prior_value" if prior else "value"
        value = item.get(value_key)
        if value is None or not cls.has_fact_source(item, prior):
            return "n/a"
        return cls.number(value)

    def print_facts(self, facts: dict[str, Any], ticker: str, peer: bool = False) -> dict[str, Any]:
        result, end, fy = self.compile_facts(facts)
        if not peer:
            self.report_period = end
            self.facts = result
        print(f"  {ticker}: fiscal year {fy}, period end {end}")
        for metric, item in result.items():
            print(f"    {metric}: {self.number(item['value'])} (prior: {self.number(item['prior_value'])}) | tag={item['tag']} | period end={item['period_end']} | filing={item['filing']}")
        return result

    def step4(self) -> None:
        print("Step 4/7: Fetch and print annual XBRL facts and prior-year values.", flush=True)
        if not self.cik:
            self.cik, self.company = self.resolve_ticker(self.ticker)
        if not self.submissions:
            self.submissions = self.get(f"{DATA_BASE}/submissions/CIK{self.cik}.json").json()
        facts = self.get_company_facts(self.cik)
        self.print_facts(facts, self.ticker)

    def is_financial_institution(self) -> bool:
        if not self.submissions:
            if not self.cik:
                self.cik, self.company = self.resolve_ticker(self.ticker)
            self.submissions = self.get(f"{DATA_BASE}/submissions/CIK{self.cik}.json").json()
        description = self.submissions.get("sicDescription", "")
        return bool(re.search(r"bank|broker|dealer|securities|investment management", description, re.I))

    def step5(self) -> None:
        print("Step 5/7: Calculate financial ratios and free cash flow.", flush=True)
        if not self.facts:
            self.facts, self.report_period, _ = self.compile_facts(self.get_company_facts(self.cik or self.resolve_ticker(self.ticker)[0]))
        f = self.facts
        rev, prev_rev = f["revenue"]["value"], f["revenue"]["prior_value"]
        op = f["operating_income"]["value"]
        parent_net = f["net_income_attributable_to_parent"]["value"]
        eq = f["stockholders_equity"]["value"]
        prev_eq = f["stockholders_equity"]["prior_value"]
        cfo, capex = f["cash_from_operations"]["value"], f["additions_to_property_and_equipment"]["value"]
        def ratio(a: Any, b: Any) -> float | None:
            return a / b if a is not None and b not in (None, 0) else None
        revenue_sourced = self.has_fact_source(f["revenue"])
        prior_revenue_sourced = self.has_fact_source(f["revenue"], prior=True)
        op_sourced = self.has_fact_source(f["operating_income"])
        parent_net_sourced = self.has_fact_source(f["net_income_attributable_to_parent"])
        equity_sourced = self.has_fact_source(f["stockholders_equity"])
        prior_equity_sourced = self.has_fact_source(f["stockholders_equity"], prior=True)
        debt_item = f["long_term_debt"]
        current_debt_item = f["current_portion_of_long_term_debt"]
        short_debt_item = f["short_term_borrowings"]
        debt_components: list[dict[str, Any]] = []
        long_tag = debt_item.get("tag")
        if self.has_fact_source(debt_item):
            if long_tag in {"LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"}:
                # These concepts are complete totals; do not add current maturities again.
                debt_components.append(debt_item)
            elif self.has_fact_source(current_debt_item):
                debt_components.extend((debt_item, current_debt_item))
        # Short-term borrowings alone are only a partial funding measure.
        # Report D/E only when the long-term debt base is available.
        long_term_base_complete = bool(debt_components)
        if long_term_base_complete and self.has_fact_source(short_debt_item):
            debt_components.append(short_debt_item)
        debt_inputs_sourced = bool(debt_components) and all(self.has_fact_source(item) for item in debt_components)
        current_debt_sourced = self.has_fact_source(f["current_portion_of_long_term_debt"])
        cfo_sourced = self.has_fact_source(f["cash_from_operations"])
        capex_sourced = self.has_fact_source(f["additions_to_property_and_equipment"])
        eps_sourced = self.has_fact_source(f["diluted_eps"])
        growth = ratio(rev - prev_rev, prev_rev) if revenue_sourced and prior_revenue_sourced and rev is not None and prev_rev not in (None, 0) else None
        op_margin = ratio(op, rev) if op_sourced and revenue_sourced else None
        avg_equity = (eq + prev_eq) / 2 if eq is not None and prev_eq is not None else None
        roe = ratio(parent_net, avg_equity) if parent_net_sourced and equity_sourced and prior_equity_sourced else None
        total_debt = sum(item["value"] for item in debt_components) if debt_inputs_sourced and all(item.get("value") is not None for item in debt_components) else None
        debt_equity = ratio(total_debt, eq) if debt_inputs_sourced and equity_sourced else None
        fcf = cfo - capex if cfo_sourced and capex_sourced and cfo is not None and capex is not None else None
        diluted_eps = f["diluted_eps"]["value"]
        pe = ratio(self.price, diluted_eps) if self.price is not None and eps_sourced else None
        print("  Calculator (amounts in USD; ratios shown as percentages where stated).")
        print(f"  Computed revenue growth = ({self.input_value(f['revenue'])} - {self.input_value(f['revenue'], prior=True)}) / {self.input_value(f['revenue'], prior=True)} = {self.number(growth * 100 if growth is not None else None)}% | inputs: revenue [{self.fact_source(f['revenue'])}]; prior revenue [{self.fact_source(f['revenue'], prior=True)}]")
        if op_margin is not None:
            print(f"  Computed operating margin = {self.input_value(f['operating_income'])} / {self.input_value(f['revenue'])} = {self.number(op_margin * 100)}% | inputs: operating income [{self.fact_source(f['operating_income'])}]; revenue [{self.fact_source(f['revenue'])}]")
        elif self.is_financial_institution():
            print("  Computed operating margin = n/a (not applicable to this financial institution; its income statement has no operating income line). No pre-tax income was substituted.")
        else:
            print(f"  Computed operating margin = n/a | inputs: operating income [{self.fact_source(f['operating_income'])}]; revenue [{self.fact_source(f['revenue'])}]")
        print(f"  Computed ROE (program method: reported net income fact / simple average of current and prior year-end stockholders' equity; equity may include preferred stock, so this may differ from reported average common ROE) = {self.input_value(f['net_income_attributable_to_parent'])} / (({self.input_value(f['stockholders_equity'])} + {self.input_value(f['stockholders_equity'], prior=True)}) / 2) = {self.number(roe * 100 if roe is not None else None)}% | inputs: reported net income fact [{self.fact_source(f['net_income_attributable_to_parent'])}]; stockholders' equity [{self.fact_source(f['stockholders_equity'])}]; prior stockholders' equity [{self.fact_source(f['stockholders_equity'], prior=True)}]")
        debt_formula = " + ".join(self.input_value(item) for item in debt_components) if debt_components else "n/a"
        debt_sources = "; ".join(self.fact_source(item) for item in debt_components) if debt_components else "source unavailable"
        if not long_term_base_complete:
            print(f"  Computed debt to equity = n/a (complete long-term debt base unavailable; short-term borrowings alone are not reported as total debt) | inputs: long-term debt [{self.fact_source(debt_item)}]; current portion [{self.fact_source(current_debt_item)}]")
        else:
            print(f"  Computed debt to equity = ({debt_formula}) / {self.input_value(f['stockholders_equity'])} = {self.number(debt_equity)} | inputs: borrowings [{debt_sources}]; equity [{self.fact_source(f['stockholders_equity'])}]; definition: uses LongTermDebt or a complete equivalent including current maturities, or noncurrent plus current debt; includes separate short-term borrowings when reported; excludes repos and other secured financings")
        print(f"  Computed free cash flow = {self.input_value(f['cash_from_operations'])} - {self.input_value(f['additions_to_property_and_equipment'])} = {self.number(fcf)} | inputs: cash from operations [{self.fact_source(f['cash_from_operations'])}]; additions to property and equipment [{self.fact_source(f['additions_to_property_and_equipment'])}]")
        price_input = self.number(self.price) if self.price is not None else "n/a"
        print(f"  Computed P/E = {price_input} / {self.input_value(f['diluted_eps'])} = {self.number(pe)} | inputs: price [command-line argument --price]; diluted EPS [{self.fact_source(f['diluted_eps'])}]")

    def step6(self) -> None:
        print("Step 6/7: Extract quarterly revenue and diluted EPS from the earnings release.", flush=True)
        if "8-K" not in self.filings:
            self.step2()
        response = self.get(self.filings["8-K"].release_url)
        soup = BeautifulSoup(response.content, "html.parser")
        release = self.html_to_text(response.content)
        lines = release.splitlines()
        table_revenue_hit = None
        table_eps_hit = None
        quarter_pattern = re.compile(r"(?:Q[1-4]\s*['’]?\s*\d{2}|[1-4]\s*Q\s*['’]?\s*\d{2})", re.I)
        for table in soup.find_all("table"):
            table_rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])] for row in table.find_all("tr")]
            headers = [row for row in table_rows if sum(bool(quarter_pattern.fullmatch(cell.strip())) for cell in row) >= 2]
            if not headers:
                continue
            # A multi-row table header may first list comparison periods
            # (for example, 3Q25 and 4Q24), then the full row with 4Q25.
            header = max(headers, key=lambda row: sum(bool(quarter_pattern.fullmatch(cell.strip())) for cell in row))
            period_columns = [(i, cell.strip(), quarter_pattern.fullmatch(cell.strip())) for i, cell in enumerate(header) if quarter_pattern.fullmatch(cell.strip())]
            actual_period_indexes = [(i, label, match) for i, label, match in period_columns if not re.search(r"forecast|estimate|guidance", label, re.I)]
            if not period_columns or not actual_period_indexes:
                continue
            # Releases often order columns as current quarter, year-ago
            # quarter, then prior quarter. Select by quarter/year, not by
            # whichever column happens to appear last in the HTML.
            def quarter_key(label: str) -> tuple[int, int] | None:
                match = re.fullmatch(r"Q([1-4])\s*['’]?\s*(\d{2})", label, re.I)
                if match:
                    return int(match.group(2)), int(match.group(1))
                match = re.fullmatch(r"([1-4])\s*Q\s*['’]?\s*(\d{2})", label, re.I)
                return (int(match.group(2)), int(match.group(1))) if match else None
            selected_col, latest_actual_period, _ = max(actual_period_indexes, key=lambda x: quarter_key(x[1]) or (-1, -1))
            period_ordinal = [i for i, _, _ in actual_period_indexes].index(selected_col)
            unit_match = next((re.search(r"\b(millions|thousands|billions)\b", cell, re.I) for cell in header if re.search(r"\b(millions|thousands|billions)\b", cell, re.I)), None)
            unit = f"USD {unit_match.group(1).lower()}" if unit_match else "amounts as reported"
            local_revenue_hit = None
            local_eps_hit = None
            data_rows = table_rows[table_rows.index(header) + 1:]
            for row_index, row in enumerate(data_rows):
                if not row:
                    continue
                label = row[0].strip()
                # Release tables often split each value into currency and
                # amount cells, while the header uses different column spans.
                # Match the chronological quarter ordinal to the numeric values.
                numbers = [cell.strip().replace("$", "").replace(",", "") for cell in row[1:] if re.fullmatch(r"\s*\$?\s*\d[\d,]*(?:\.\d+)?\s*", cell)]
                if period_ordinal >= len(numbers):
                    continue
                value = numbers[period_ordinal]
                if local_revenue_hit is None and re.fullmatch(r"(?:(?:total|net)\s+)?revenues?(?:\s*[-–]\s*reported)?", label, re.I):
                    local_revenue_hit = f"Reported revenue ({latest_actual_period} actual, {unit}): {value}"
                previous_label = data_rows[row_index - 1][0].strip() if row_index else ""
                eps_label = bool(re.fullmatch(r"(?:diluted\s+(?:EPS|earnings\s+per\s+share)|(?:EPS|earnings\s+per\s+share)\s*[-–]\s*diluted)", label, re.I)) or (re.fullmatch(r"diluted", label, re.I) and re.search(r"earnings\s+per\s+share|EPS", previous_label, re.I))
                if local_eps_hit is None and eps_label:
                    local_eps_hit = f"GAAP diluted EPS ({latest_actual_period} actual): ${value}"
            if local_revenue_hit and local_eps_hit:
                table_revenue_hit, table_eps_hit = local_revenue_hit, local_eps_hit
                break

        # Some releases label columns by the date range and year instead of
        # a quarter token (for example, "Three Months Ended September 30")
        # and group a GAAP/Adjusted EPS pair beneath a shared row heading.
        if not (table_revenue_hit and table_eps_hit):
            year_pattern = re.compile(r"\b20\d{2}\b")
            for table in soup.find_all("table"):
                table_rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])] for row in table.find_all("tr")]
                three_months_row = next((i for i, row in enumerate(table_rows) if re.search(r"Three\s+Months\s+Ended", " ".join(row), re.I)), None)
                if three_months_row is None:
                    continue
                year_row_index = next((i for i in range(three_months_row + 1, min(three_months_row + 4, len(table_rows))) if sum(bool(year_pattern.fullmatch(cell.strip())) for cell in table_rows[i]) >= 2), None)
                if year_row_index is None:
                    continue
                # Limit the year columns to the "Three Months Ended" group;
                # later columns in the same table may show year-to-date values.
                nine_months_col = next((i for i, cell in enumerate(table_rows[three_months_row]) if re.search(r"Nine\s+Months\s+Ended", cell, re.I)), len(table_rows[year_row_index]))
                year_cols = [(i, int(cell.strip())) for i, cell in enumerate(table_rows[year_row_index]) if i < nine_months_col and year_pattern.fullmatch(cell.strip())]
                if not year_cols:
                    continue
                latest_year = max(year for _, year in year_cols)
                quarter_ordinal = [year for _, year in year_cols].index(latest_year)
                unit_match = re.search(r"\bin (millions|thousands|billions)\b", " ".join(cell for row in table_rows for cell in row), re.I)
                quarter_unit = f"USD {unit_match.group(1).lower()}" if unit_match else "USD as shown"
                local_revenue_hit = None
                local_eps_hit = None
                expect_gaap_eps = False
                for row in table_rows[year_row_index + 1:]:
                    if not row:
                        continue
                    label = row[0].strip()
                    if re.search(r"diluted\s+earnings\s+per\s+(?:common\s+)?share", label, re.I):
                        expect_gaap_eps = True
                        continue
                    numbers = [cell.strip().replace("$", "").replace(",", "") for cell in row[1:] if re.fullmatch(r"\s*\$?\s*\d[\d,]*(?:\.\d+)?\s*", cell)]
                    if quarter_ordinal >= len(numbers):
                        expect_gaap_eps = False
                        continue
                    value = numbers[quarter_ordinal]
                    if local_revenue_hit is None and re.match(r"(?:(?:total|net)\s+)?revenues?\b", label, re.I):
                        local_revenue_hit = f"Reported revenue ({latest_year} latest three-month period, {quarter_unit}): {value}"
                    if expect_gaap_eps and re.fullmatch(r"GAAP", label, re.I):
                        local_eps_hit = f"GAAP diluted EPS ({latest_year} latest three-month period): ${value}"
                    expect_gaap_eps = False
                if local_revenue_hit and local_eps_hit:
                    table_revenue_hit, table_eps_hit = local_revenue_hit, local_eps_hit
                    break

        revenue_hits = [] if table_revenue_hit else [line for line in lines if not re.search(r"fiscal year|annual|forecast|guidance|expect|project", line, re.I) and (re.search(r"quarter(?:ly)?\s+(?:net\s+)?revenue", line, re.I) or re.search(r"(?:net\s+)?revenues?\s+of\s+\$\s*[\d,.]+\s*(?:billion|million)", line, re.I)) and re.search(r"\$\s*[\d,.]+", line)]
        eps_hits = [] if table_eps_hit else [line for line in lines if not re.search(r"forecast|guidance|expect|project", line, re.I) and (re.search(r"diluted", line, re.I) and re.search(r"earnings\s+per\s+share|per\s+diluted\s+share|per-share", line, re.I) or re.search(r"\bEPS\s+of\s+\$", line, re.I)) and re.search(r"\$\s*[\d,.]+|\b\d+\.\d+\b", line)]
        hits = ([table_revenue_hit] if table_revenue_hit else revenue_hits) + ([table_eps_hit] if table_eps_hit else eps_hits)
        hits = list(dict.fromkeys(hits))
        def first_amount_after(start: int) -> str | None:
            for candidate in lines[start + 1:]:
                value = candidate.strip().replace("$", "").replace(",", "")
                if re.fullmatch(r"\d+(?:\.\d+)?", value):
                    return candidate.strip().replace("$", "").strip()
            return None
        if not table_revenue_hit and not revenue_hits:
            total_revenue_i = next((i for i, line in enumerate(lines) if re.fullmatch(r"Total revenue", line.strip(), re.I)), None)
            total_revenue = first_amount_after(total_revenue_i) if total_revenue_i is not None else None
            if total_revenue:
                hits.append(f"Total revenue (quarterly, in millions): {total_revenue}")
        if not table_eps_hit and not eps_hits:
            diluted_i = next((i for i, line in enumerate(lines) if re.search(r"diluted\s+net income per common share", line, re.I)), None)
            if diluted_i is None:
                income_i = next((i for i, line in enumerate(lines) if re.search(r"NET INCOME PER COMMON SHARE", line, re.I)), None)
                diluted_i = next((i for i, line in enumerate(lines) if income_i is not None and i > income_i and re.fullmatch(r"Diluted", line.strip(), re.I)), None)
            diluted_eps = first_amount_after(diluted_i) if diluted_i is not None else None
            if diluted_eps:
                hits.append(f"Diluted earnings per share (quarterly): ${diluted_eps}")
        print("  Release lines that state quarterly total revenue and diluted EPS:")
        for line in hits:
            print(f"  {line}")
        adjusted_eps_lines = [line for line in lines if len(line) <= 150 and ((re.search(r"reported\s+EPS\s+from\s+\$?[\d.]+\s+to\s+\$?[\d.]+", line, re.I) and re.search(r"excluding|non-GAAP|adjusted", line, re.I)) or re.search(r"GAAP.*\$[\d.]+.*\$[\d.]+.*adjusted", line, re.I))]
        for line in adjusted_eps_lines:
            print(f"  Flagged adjusted/non-GAAP figure (not used for diluted EPS): {line}")
        if not hits:
            print("  No lines matched revenue or diluted EPS terms. Review the saved release text.")

    def step7(self) -> None:
        print("Step 7/7: Fetch peer facts and calculate operating margins.", flush=True)
        if not self.facts:
            self.facts, self.report_period, _ = self.compile_facts(self.get_company_facts(self.cik or self.resolve_ticker(self.ticker)[0]))
        print("  Operating margin uses operating income divided by revenue.")
        self.peer_results: dict[str, Any] = {}
        for peer in self.peers:
            cik, _ = self.resolve_ticker(peer)
            peer_facts = self.get_company_facts(cik)
            result, end, fy = self.compile_facts(peer_facts)
            revenue, op = result["revenue"]["value"], result["operating_income"]["value"]
            margin = op / revenue if self.has_fact_source(result["operating_income"]) and self.has_fact_source(result["revenue"]) and op is not None and revenue not in (None, 0) else None
            print(f"  {peer}: fiscal year {fy}, period end {end}")
            print(f"    Computed operating margin = {self.input_value(result['operating_income'])} / {self.input_value(result['revenue'])} = {self.number(margin * 100 if margin is not None else None)}% | inputs: operating income [{self.fact_source(result['operating_income'])}]; revenue [{self.fact_source(result['revenue'])}]")
            for metric, item in result.items():
                print(f"    {metric}: {self.number(item['value'])} (prior: {self.number(item['prior_value'])}) | tag={item['tag']} | period end={item['period_end']} | filing={item['filing']}")
            self.peer_results[peer] = {"cik": cik, "report_period": end, "facts": result, "operating_margin": margin}

    def save_facts(self) -> None:
        if not self.facts:
            return
        self.ensure_output()
        payload = {"ticker": self.ticker, "company": self.company, "cik": self.cik, "report_period": self.report_period, "facts": self.facts, "peers": getattr(self, "peer_results", {})}
        (self.output_dir / "facts.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def run(self, only_step: int | None) -> None:
        methods = [self.step1, self.step2, self.step3, self.step4, self.step5, self.step6, self.step7]
        if only_step is None:
            for method in methods:
                method()
            self.save_facts()
        else:
            methods[only_step - 1]()
            self.save_facts()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect SEC filings and XBRL facts for an equity research desk.")
    parser.add_argument("ticker", help="Company ticker symbol")
    parser.add_argument("--peers", nargs="*", default=[], help="Peer ticker symbols")
    parser.add_argument("--price", type=float, help="Share price for the P/E calculation")
    parser.add_argument("--step", type=int, choices=range(1, 8), metavar="1-7", help="Run one step only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        peers = [ticker.strip() for group in args.peers for ticker in group.split(",") if ticker.strip()]
        Desk(args.ticker, peers, args.price).run(args.step)
    except (ValueError, RuntimeError, requests.RequestException, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
