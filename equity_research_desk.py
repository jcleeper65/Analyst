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
    "revenue": {"tags": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet", "RevenueFromContractWithCustomerIncludingAssessedTax"], "kind": "duration", "unit": "USD"},
    "operating_income": {"tags": ["OperatingIncomeLoss"], "kind": "duration", "unit": "USD"},
    "net_income": {"tags": ["NetIncomeLoss", "ProfitLoss"], "kind": "duration", "unit": "USD"},
    "diluted_eps": {"tags": ["EarningsPerShareDiluted"], "kind": "duration", "unit": "USD/shares"},
    "stockholders_equity": {"tags": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "kind": "instant", "unit": "USD"},
    "long_term_debt": {"tags": ["LongTermDebtNoncurrent", "LongTermDebtAndFinanceLeaseObligationsNoncurrent", "LongTermDebt"], "kind": "instant", "unit": "USD"},
    "current_portion_of_long_term_debt": {"tags": ["LongTermDebtCurrent", "LongTermDebtAndFinanceLeaseObligationsCurrent", "ShortTermBorrowings"], "kind": "instant", "unit": "USD"},
    "cash_from_operations": {"tags": ["NetCashProvidedByUsedInOperatingActivities"], "kind": "duration", "unit": "USD"},
    "additions_to_property_and_equipment": {"tags": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"], "kind": "duration", "unit": "USD"},
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
            start = row.get("start")
            if kind == "duration" and (not start or not (300 <= (datetime.fromisoformat(row["end"]) - datetime.fromisoformat(start)).days <= 400)):
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
        return output, target_end, target_fy

    @staticmethod
    def number(value: Any) -> str:
        return "n/a" if value is None else f"{value:,.4f}" if isinstance(value, float) else f"{value:,.2f}"

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
        facts = self.get_company_facts(self.cik)
        self.print_facts(facts, self.ticker)

    def step5(self) -> None:
        print("Step 5/7: Calculate financial ratios and free cash flow.", flush=True)
        if not self.facts:
            self.facts, self.report_period, _ = self.compile_facts(self.get_company_facts(self.cik or self.resolve_ticker(self.ticker)[0]))
        f = self.facts
        rev, prev_rev = f["revenue"]["value"], f["revenue"]["prior_value"]
        op, net, eq = f["operating_income"]["value"], f["net_income"]["value"], f["stockholders_equity"]["value"]
        prev_eq = f["stockholders_equity"]["prior_value"]
        debt = f["long_term_debt"]["value"]
        current_debt = f["current_portion_of_long_term_debt"]["value"]
        cfo, capex = f["cash_from_operations"]["value"], f["additions_to_property_and_equipment"]["value"]
        def ratio(a: Any, b: Any) -> float | None:
            return a / b if a is not None and b not in (None, 0) else None
        growth = ratio(rev - prev_rev, prev_rev) if rev is not None and prev_rev not in (None, 0) else None
        op_margin = ratio(op, rev)
        avg_equity = (eq + prev_eq) / 2 if eq is not None and prev_eq is not None else None
        roe = ratio(net, avg_equity)
        total_debt = (debt or 0) + (current_debt or 0) if debt is not None or current_debt is not None else None
        debt_equity = ratio(total_debt, eq)
        fcf = cfo - capex if cfo is not None and capex is not None else None
        diluted_eps = f["diluted_eps"]["value"]
        pe = ratio(self.price, diluted_eps) if self.price is not None else None
        print("  Calculator (amounts in USD; ratios shown as percentages where stated).")
        print(f"  Revenue growth = (revenue {self.number(rev)} - prior revenue {self.number(prev_rev)}) / prior revenue {self.number(prev_rev)} = {self.number(growth * 100 if growth is not None else None)}%")
        print(f"  Operating margin = operating income {self.number(op)} / revenue {self.number(rev)} = {self.number(op_margin * 100 if op_margin is not None else None)}%")
        print(f"  Return on average equity = net income {self.number(net)} / ((equity {self.number(eq)} + prior equity {self.number(prev_eq)}) / 2) = {self.number(roe * 100 if roe is not None else None)}%")
        print(f"  Debt to equity = (long-term debt {self.number(debt)} + current portion {self.number(current_debt)}) / equity {self.number(eq)} = {self.number(debt_equity)}")
        print(f"  Free cash flow = cash from operations {self.number(cfo)} - additions to property and equipment {self.number(capex)} = {self.number(fcf)}")
        print(f"  P/E = price {self.number(self.price)} / diluted EPS {self.number(diluted_eps)} = {self.number(pe)}")

    def step6(self) -> None:
        print("Step 6/7: Extract quarterly revenue and diluted EPS from the earnings release.", flush=True)
        if "8-K" not in self.filings:
            self.step2()
        release = self.html_to_text(self.get(self.filings["8-K"].release_url).content)
        lines = release.splitlines()
        revenue_hits = [line for line in lines if not re.search(r"fiscal year|annual", line, re.I) and (re.search(r"quarter(?:ly)?\s+revenue", line, re.I) or re.search(r"revenue\s+of\s+\$\s*[\d,.]+\s*(?:billion|million)", line, re.I)) and re.search(r"\$\s*[\d,.]+", line)]
        eps_hits = [line for line in lines if re.search(r"diluted", line, re.I) and re.search(r"earnings\s+per\s+share|\bEPS\b|per-share", line, re.I) and re.search(r"\$\s*[\d,.]+|\b\d+\.\d+\b", line)]
        hits = list(dict.fromkeys(revenue_hits + eps_hits))
        def first_amount_after(start: int) -> str | None:
            for candidate in lines[start + 1:]:
                value = candidate.strip().replace("$", "").replace(",", "")
                if re.fullmatch(r"\d+(?:\.\d+)?", value):
                    return candidate.strip().replace("$", "").strip()
            return None
        if not revenue_hits:
            total_revenue_i = next((i for i, line in enumerate(lines) if re.fullmatch(r"Total revenue", line.strip(), re.I)), None)
            total_revenue = first_amount_after(total_revenue_i) if total_revenue_i is not None else None
            if total_revenue:
                hits.append(f"Total revenue (quarterly, in millions): {total_revenue}")
        if not eps_hits:
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
            margin = op / revenue if op is not None and revenue not in (None, 0) else None
            print(f"  {peer}: fiscal year {fy}, period end {end}, operating income {self.number(op)} / revenue {self.number(revenue)} = {self.number(margin * 100 if margin is not None else None)}%")
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
