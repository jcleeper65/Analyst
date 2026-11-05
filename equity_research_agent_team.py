"""Fixed-order equity research team implemented as a CrewAI Flow."""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Type

from crewai import Agent, Crew, LLM, Process, Task
from crewai.flow.flow import Flow, listen, start
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from insight_layout import insight_failures
from report_naming import create_run, report_number
from equity_research_desk import Desk


SECTIONS = (
    "Overview",
    "Market Positioning and Growth Outlook",
    "Valuation Insights",
    "Future Developments and Strategic Recommendations",
    "Investment Recommendation",
)
ROLES_DIR = Path(__file__).with_name("roles")
OUTPUT_ROOT = Path(__file__).with_name("equity_research_output")


class NoToolInput(BaseModel):
    """The data-step tools need no model-supplied arguments."""


class DeskStepTool(BaseTool):
    """CrewAI tool adapter for one existing desk step."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    step_number: int
    desk: Any = Field(exclude=True)
    args_schema: Type[BaseModel] = NoToolInput

    def _run(self) -> str:
        method = getattr(self.desk, f"step{self.step_number}")
        method()
        if self.step_number == 4:
            self.desk.save_facts()
        if self.step_number == 7:
            self.desk.save_facts()
        state = {
            1: {"company": self.desk.company, "cik": self.desk.cik},
            2: {name: vars(filing) for name, filing in self.desk.filings.items()},
            3: {"saved_texts": [path.name for path in self.desk.output_dir.glob("*.txt")]},
            4: {"report_period": self.desk.report_period, "facts": self.desk.facts},
            5: self.desk.computed_metrics,
            6: self.desk.quarter_results,
            7: self.desk.peer_results,
        }[self.step_number]
        return json.dumps(state, ensure_ascii=False, default=str)


def _safe_json(text: str, role: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I)
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{role} did not return valid JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise RuntimeError(f"{role} returned JSON that was not an object")
    return result


def numbered_lines(path: Path) -> str:
    return "\n".join(
        f"{path.name}:L{i}: {line}"
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
    )


def numbered_section(path: Path, item: int, next_item: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    # Require a boundary after the item number, but allow attached punctuation.
    start_re = re.compile(rf"^\s*Item\s+{item}(?=\s|[.\-–—:]|$)", re.I)
    end_re = re.compile(rf"^\s*Item\s+{next_item}(?=\s|[.\-–—:]|$)", re.I)
    candidates = []
    for first, line in enumerate(lines):
        if start_re.search(line):
            last = next((i for i in range(first + 1, len(lines)) if end_re.search(lines[i])), len(lines))
            candidates.append((first, last))
    if not candidates:
        return f"{path.name}: Item {item} section was not found in the supplied extraction; this does not establish that the filing omits it."
    # A table-of-contents entry has a much shorter span than the body section.
    first, last = max(candidates, key=lambda span: sum(len(line) for line in lines[span[0]:span[1]]))
    return "\n".join(f"{path.name}:L{i + 1}: {lines[i]}" for i in range(first, last))


def missing_fact_filing_lines(path: Path, facts: dict[str, Any], radius: int = 2) -> dict[str, Any]:
    """Supply filing evidence for absent structured values, without guessing values."""
    missing = [name for name, fact in facts.items() if fact.get("value") is None]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    patterns = {
        "short_term_borrowings": r"short[\s‐‑–—-]*term\s+(?:borrowings|debt)|bank credit|commercial paper",
        "current_portion_of_long_term_debt": r"current (?:portion|maturities).*debt",
        "long_term_debt": r"long[\s‐‑–—-]*term\s+debt",
    }
    selected = set()
    for name in missing:
        pattern = patterns.get(name, re.escape(name.replace("_", " ")))
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.I):
                selected.update(range(max(0, i - radius), min(len(lines), i + radius + 1)))
    return {
        "missing_structured_metrics": missing,
        "availability_note": "A missing structured value is unavailable in supplied XBRL data, not proof of missing disclosure. Use cited filing passages when available. Do not infer an unrestricted zero from a statement limited to particular facilities.",
        "filing_lines": "\n".join(f"{path.name}:L{i + 1}: {lines[i]}" for i in sorted(selected)),
    }


def relevant_release_lines(path: Path) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    chosen: set[int] = set()
    for i, line in enumerate(lines):
        if re.search(r"revenue|diluted|earnings per share|GAAP|adjusted|outlook", line, re.I):
            chosen.update(range(max(0, i - 2), min(len(lines), i + 3)))
    return "\n".join(f"{path.name}:L{i + 1}: {lines[i]}" for i in sorted(chosen))


def calculator_inputs(desk: Desk) -> dict[str, Any]:
    result: dict[str, Any] = {}
    companies = [(desk.ticker, desk.facts)] + [
        (ticker, item.get("facts", {})) for ticker, item in desk.peer_results.items()
    ]
    for ticker, facts in companies:
        for metric, item in facts.items():
            for period, value_key in (("current", "value"), ("prior", "prior_value")):
                value = item.get(value_key)
                source = desk.fact_source(item, prior=period == "prior")
                if value is not None and source != "source unavailable":
                    result[f"{ticker}.{metric}.{period}"] = {"value": value, "source": source}
    return result


class Runtime:
    def __init__(self, desk: Desk | None = None):
        load_dotenv(Path(__file__).with_name(".env"))
        self.api_key = os.getenv("API_KEY", "").strip()
        if not self.api_key:
            raise ValueError("API_KEY is missing or empty in .env")
        self.model = os.getenv("MODEL", "gemini/gemini-3.5-flash-lite").strip()
        base_url = os.getenv("LLM_BASE_URL", "").strip()
        llm_args: dict[str, Any] = {"model": self.model, "api_key": self.api_key}
        if base_url:
            llm_args.update({"base_url": base_url, "custom_openai": True})
        self.llm = LLM(**llm_args)
        self.desk = desk
        self.output_dir: Path | None = desk.output_dir if desk else None
        self.nodes_dir: Path | None = None
        self.role_call_counts: dict[str, int] = {}

    def set_output_dir(self, path: Path) -> None:
        self.output_dir = path
        self.nodes_dir = path / "nodes"
        self.nodes_dir.mkdir(parents=True, exist_ok=True)

    def save_node(self, node: str, direction: str, payload: Any) -> None:
        if self.nodes_dir is None:
            raise RuntimeError("Run folder is not ready")
        folder = self.nodes_dir / re.sub(r"[^A-Za-z0-9_-]+", "_", node)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{direction}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )

    def instructions(self, file_name: str) -> str:
        return (ROLES_DIR / file_name).read_text(encoding="utf-8")

    def role_call(
        self,
        role: str,
        instruction_file: str,
        envelope: dict[str, Any],
    ) -> dict[str, Any]:
        if set(envelope) != {"task", "context", "expected_output"}:
            raise ValueError(f"Invalid {role} envelope")
        current = self.role_call_counts.get(role, 0) + 1
        if current > 2:
            raise RuntimeError(f"Role call limit exceeded for {role}")
        self.role_call_counts[role] = current
        node = f"{role} {current}"
        print(f"Node starting: {node}", flush=True)
        self.save_node(node, "input", envelope)
        prompt = json.dumps(envelope, ensure_ascii=False)
        agent = Agent(
            role=role,
            goal=envelope["task"],
            backstory=self.instructions(instruction_file),
            llm=self.llm,
            max_iter=1,
            max_retry_limit=0,
            allow_delegation=False,
            verbose=False,
        )
        task = Task(
            description="Read and follow this assigned graph-state JSON: {payload}",
            expected_output=envelope["expected_output"],
            agent=agent,
        )
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            memory=False,
            planning=False,
        )
        result = crew.kickoff(inputs={"payload": prompt})
        output = _safe_json(result.raw, role)
        self.save_node(node, "output", output)
        return output

    def research_context(self) -> dict[str, Any]:
        assert self.desk and self.output_dir
        return {
            "ticker": self.desk.ticker,
            "sources": {
                "10k_business": numbered_section(self.output_dir / "10-K.txt", 1, 2),
                "10k_mda": numbered_section(self.output_dir / "10-K.txt", 7, 8),
                "earnings_release": numbered_lines(self.output_dir / "earnings_release_Ex99-1.txt"),
            },
        }

    def financial_context(self) -> dict[str, Any]:
        assert self.desk and self.output_dir
        return {
            "ticker": self.desk.ticker,
            "fiscal_year_end": self.desk.report_period,
            "facts": self.desk.facts,
            "computed_metrics": self.desk.computed_metrics,
            "missing_fact_filing_evidence": missing_fact_filing_lines(
                self.output_dir / "10-K.txt", self.desk.facts
            ),
            "latest_quarter_results": self.desk.quarter_results,
            "earnings_release_citation_lines": relevant_release_lines(
                self.output_dir / "earnings_release_Ex99-1.txt"
            ),
            "peers": self.desk.peer_results,
            "calculation_inputs": calculator_inputs(self.desk),
        }

    @staticmethod
    def envelope(task: str, context: Any, expected_output: str) -> dict[str, Any]:
        return {"task": task, "context": context, "expected_output": expected_output}

    @staticmethod
    def without_advisor_thesis(report: str) -> str:
        output: list[str] = []
        skip = False
        for line in report.splitlines():
            if re.match(r"^#{1,3}\s+Investment Recommendation\s*$", line, re.I):
                skip = True
            elif re.match(
                r"^#{1,3}\s+(Overview|Market Positioning and Growth Outlook|Valuation Insights|Future Developments and Strategic Recommendations)\s*$",
                line,
                re.I,
            ):
                skip = False
            if not skip or line.startswith("Insight:"):
                output.append(line)
        return "\n".join(output)

    def code_checks(self, report: str, facts: dict[str, Any], texts: dict[str, str]) -> list[dict[str, str]]:
        checks: list[dict[str, str]] = []
        fact_groups = {"primary": facts.get("facts", {})}
        fact_groups.update({name: peer.get("facts", {}) for name, peer in facts.get("peers", {}).items()})

        def match_fact(tag: str, period: str, accession: str) -> tuple[bool, Any]:
            for group in fact_groups.values():
                for fact in group.values():
                    if fact.get("tag") == tag and fact.get("period_end") == period and str(fact.get("filing")) == accession:
                        return True, fact.get("value")
                    if fact.get("tag") == tag and fact.get("prior_period_end") == period and str(fact.get("prior_filing")) == accession:
                        return True, fact.get("prior_value")
            return False, None

        def normalize(value: str) -> str:
            return re.sub(r"\s+", " ", value).strip()

        def arithmetic(expression: str) -> float | None:
            try:
                tree = ast.parse(expression, mode="eval")

                def evaluate(node: ast.AST) -> float:
                    if isinstance(node, ast.Expression):
                        return evaluate(node.body)
                    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                        return float(node.value)
                    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                        value = evaluate(node.operand)
                        return value if isinstance(node.op, ast.UAdd) else -value
                    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                        left, right = evaluate(node.left), evaluate(node.right)
                        if isinstance(node.op, ast.Add):
                            return left + right
                        if isinstance(node.op, ast.Sub):
                            return left - right
                        if isinstance(node.op, ast.Mult):
                            return left * right
                        return left / right
                    raise ValueError("Unsupported arithmetic")

                return evaluate(tree)
            except (SyntaxError, ValueError, ZeroDivisionError):
                return None

        for line_number, line in enumerate(report.splitlines(), 1):
            if line_number <= 2:
                # The first two report lines identify filings and the run time.
                continue
            if not re.search(r"\d", line):
                continue
            no_cites = re.sub(r"\[[^\]]*\]", "", line)
            if not re.search(r"\d", no_cites):
                continue
            line_refs = re.findall(r"([A-Za-z0-9_.-]+\.txt):L(\d+)", line)
            xbrl_refs = re.findall(
                r"\[XBRL\s+tag\s+([^,\]]+),\s*period end\s+(\d{4}-\d{2}-\d{2}),\s*filing\s+([^\]]+)\]",
                line,
                re.I,
            )
            formulas = list(re.finditer(r"\[computed using formula\s+(.*?)\s+based on\s+([^\]]+)\]", line, re.I))
            if not line_refs and not xbrl_refs and not formulas:
                checks.append({"claim": line.strip(), "status": "unsupported", "reason": "Number has no source citation", "correction": "", "source": ""})
                continue
            for tag, period, accession in xbrl_refs:
                exists, value = match_fact(tag.strip(), period, accession.strip())
                number_tokens = [float(token.replace(",", "")) for token in re.findall(r"-?\d[\d,]*(?:\.\d+)?", no_cites)]
                correct = exists and value is not None and float(value) in number_tokens
                checks.append({
                    "claim": f"Cited {tag.strip()} value: {value}; period {period}; filing {accession.strip()}",
                    "status": "unsupported" if correct else "wrong" if exists else "unsupported",
                    "reason": "Source value appears in paragraph; claim-to-value association requires model review" if correct else "XBRL value or citation does not match saved facts",
                    "correction": str(value) if exists and not correct else "",
                    "source": f"XBRL tag {tag.strip()}, period end {period}, filing {accession.strip()}",
                })
            for reference in re.finditer(r"([A-Za-z0-9_.-]+\.txt):L(\d+)", line):
                filename, line_value = reference.groups()
                prefix = line[:reference.start()]
                quotes = list(re.finditer(r'["“]([^"”]+)["”]', prefix))
                quote = quotes[-1].group(1) if quotes and not prefix[quotes[-1].end():].strip(" []().,;") else ""
                claim = quote or re.split(r"[.!?]\s+|\]", prefix)[-1].strip()
                if filename not in texts:
                    checks.append({"claim": claim, "status": "unsupported", "reason": "Cited filing line is unavailable", "correction": "", "source": f"{filename}:L{line_value}"})
                    continue
                lines = texts[filename].splitlines()
                index = int(line_value) - 1
                quoted_line = lines[index] if 0 <= index < len(lines) else ""
                exact_quote = bool(quote and quoted_line and normalize(quote) in normalize(quoted_line))
                mismatch = bool(quote and quoted_line and not exact_quote)
                checks.append({
                    "claim": claim,
                    "status": "wrong" if mismatch else "unsupported",
                    "reason": ("Quoted text does not match the cited filing line" if mismatch else
                               "Quote matches; claim meaning, period, and definition require model review" if exact_quote else
                               "Line existence alone does not establish support for this claim"),
                    "correction": quoted_line if mismatch else "",
                    "source": f"{filename}:L{index + 1}: {quoted_line}",
                })
                if mismatch and re.search(r"fiscal year", claim, re.I) and re.search(r"diluted (?:share|EPS)|diluted earnings", claim, re.I):
                    eps = facts.get("facts", {}).get("diluted_eps", {})
                    value = eps.get("value")
                    annual_lines = texts.get("10-K.txt", "").splitlines()
                    for row, text in enumerate(annual_lines):
                        if value is not None and text.strip().replace("$", "").strip() == str(value) and any(
                            re.search(r"^Diluted$", label.strip(), re.I) for label in annual_lines[max(0, row - 3):row]
                        ):
                            label_row = next(j + 1 for j in range(max(0, row - 3), row) if annual_lines[j].strip().lower() == "diluted")
                            checks[-1]["correction"] = f"Annual GAAP diluted EPS: {value}; period end {eps.get('period_end')}; filing {eps.get('filing')}"
                            checks[-1]["source"] = f"10-K.txt:L{row + 1}: {text}; diluted label at 10-K.txt:L{label_row}; period end {eps.get('period_end')}; filing {eps.get('filing')}"
                            break
            for formula_match in formulas:
                expression = formula_match.group(1).replace("$", "").replace(",", "").strip()
                expression_value = arithmetic(expression)
                prefix = line[: formula_match.start()]
                displayed_matches = list(re.finditer(r"-?\d[\d,]*(?:\.\d+)?", prefix))
                displayed_match = displayed_matches[-1] if displayed_matches else None
                displayed = float(displayed_match.group(0).replace(",", "")) if displayed_match else None
                displayed_percent = bool(displayed_match and prefix[displayed_match.end():].lstrip().startswith("%"))
                expected = expression_value
                if expected is not None and displayed_percent and not re.search(r"\*\s*100\b", expression):
                    expected *= 100
                has_formula_sources = bool(re.search(r"XBRL tag|\.txt:L\d+", formula_match.group(2), re.I))
                correct = expected is not None and displayed is not None and has_formula_sources and abs(expected - displayed) <= max(1e-6, abs(expected) * 1e-5)
                checks.append({
                    "claim": f"Arithmetic: {expression} = {displayed}" ,
                    "status": "correct" if correct else "unsupported" if not has_formula_sources else "wrong",
                    "reason": "Arithmetic is correct for the stated inputs; source validity is checked separately. Price provenance is checked separately." if correct else "Ratio formula lacks sources or does not match its displayed value",
                    "correction": "" if correct else str(expected) if expected is not None else "",
                    "source": formula_match.group(2).strip(),
                })
        return checks

    @staticmethod
    def cited_filing_excerpts(report: str, texts: dict[str, str], radius: int = 2) -> dict[str, str]:
        references = re.findall(r"([A-Za-z0-9_.-]+\.txt):L(\d+)", report)
        wanted: dict[str, set[int]] = {}
        for filename, number in references:
            wanted.setdefault(filename, set()).add(int(number) - 1)
        excerpts: dict[str, str] = {}
        for filename, indices in wanted.items():
            source = texts.get(filename)
            if source is None:
                continue
            lines = source.splitlines()
            selected: set[int] = set()
            for index in indices:
                selected.update(range(max(0, index - radius), min(len(lines), index + radius + 1)))
            excerpts[filename] = "\n".join(f"{filename}:L{i + 1}: {lines[i]}" for i in sorted(selected))
        return excerpts

    def verify(self, report_path: Path, output_path: Path) -> Path:
        print("Node starting: Verifier", flush=True)
        assert self.output_dir and self.nodes_dir
        full_report = report_path.read_text(encoding="utf-8")
        report_for_verifier = self.without_advisor_thesis(full_report)
        texts = {path.name: path.read_text(encoding="utf-8", errors="replace") for path in self.output_dir.glob("*.txt")}
        facts_path = self.output_dir / "facts.json"
        facts = json.loads(facts_path.read_text(encoding="utf-8")) if facts_path.exists() else {}
        code_marks = self.code_checks(report_for_verifier, facts, texts)
        self.save_node("Verifier_Code", "output", {"checks": code_marks})
        cited_excerpts = self.cited_filing_excerpts(report_for_verifier, texts)
        # Include 10-K per-share rows even when the draft cites only a release.
        if "10-K.txt" in texts:
            lines = texts["10-K.txt"].splitlines()
            selected = set()
            for i, text in enumerate(lines):
                if re.search(r"diluted|per common share|per share", text, re.I):
                    selected.update(range(max(0, i - 8), min(len(lines), i + 12)))
            cited_excerpts["10-K.txt"] = cited_excerpts.get("10-K.txt", "") + "\n" + "\n".join(
                f"10-K.txt:L{i + 1}: {lines[i]}" for i in sorted(selected))
        task = "Verify every number in every Insight line, including Investment Advisor Insight lines, and every other non-thesis number. Check the stated period and definition, and give source-backed corrections for wrong or unsupported values."
        envelope = self.envelope(
            task,
            {"compiled_report": report_for_verifier, "saved_filing_texts": cited_excerpts, "saved_facts": facts},
            "JSON object with checks. Each check has claim, status (correct, wrong, or unsupported), reason, correction, and source.",
        )
        model_marks = self.role_call("Verifier", "verifier.md", envelope)
        for check in model_marks.get("checks", []):
            reason = str(check.get("reason", ""))
            if check.get("status") == "wrong" and re.search(r"(?:math|arithmetic|calculation) is correct", reason, re.I):
                check.update(status="unsupported", reason="Rejected inconsistent verifier result: wrong status conflicts with a reason that confirms correct arithmetic. Review source validity separately.", correction="")
        marks = ["| Claim | Mark | Reason | Correction and filing source |", "|---|---|---|---|"]
        for mark in code_marks + model_marks.get("checks", []):
            claim = str(mark.get("claim", "")).replace("|", "\\|")
            reason = str(mark.get("reason", "")).replace("|", "\\|")
            correction_source = (str(mark.get("correction", "")) + " " + str(mark.get("source", ""))).replace("|", "\\|")
            status = mark.get("status", "unsupported")
            if status not in {"correct", "wrong", "unsupported"}:
                status = "unsupported"
            marks.append(f"| {claim} | {status} | {reason} | {correction_source} |")
        if not code_marks and not model_marks.get("checks"):
            marks.append("| No non-thesis numeric claims found. | correct | No numeric claims to check. | |")
        report_lines = full_report.splitlines()
        first = report_lines[0] if report_lines else "Filings read: unavailable"
        output_path.write_text(
            first + "\n\n" + "\n".join(marks) + "\n\n" + "\n".join(report_lines[1:]) + "\n",
            encoding="utf-8",
        )
        self.save_node("Verifier", "output", {"code_checks": code_marks, "model_checks": model_marks, "verified_report": str(output_path)})
        return output_path


class EquityResearchFlow(Flow):
    """Full run graph: data -> research -> financial -> advisor -> manager -> verifier."""

    def __init__(self, ticker: str, peers: list[str], price: float | None = None, filed: str | None = None):
        super().__init__()
        self.ticker = ticker
        self.peers = peers
        self.price = None
        self.filed_override = filed
        self.runtime: Runtime | None = None
        self.role_outputs: dict[str, str] = {}
        self.contexts: dict[str, Any] = {}
        self.report_path: Path | None = None

    @start()
    def data_steps(self) -> dict[str, Any]:
        print("Node starting: Seven data steps", flush=True)
        desk = Desk(self.ticker, self.peers, filed=self.filed_override)
        self.runtime = Runtime(desk)
        step_names = (
            "Resolve ticker to CIK",
            "Find required filings",
            "Download filing texts",
            "Fetch XBRL facts",
            "Calculate ratios",
            "Extract quarterly results",
            "Fetch peer facts",
        )
        for step_number, step_name in enumerate(step_names, 1):
            envelope = {"task": step_name, "context": {"ticker": self.ticker, "peers": self.peers, "filed": self.filed_override}, "expected_output": f"Step {step_number} data and status"}
            if step_number > 1:
                self.runtime.save_node(f"Data Step {step_number}", "input", envelope)
            tool = DeskStepTool(
                name=f"Data Step {step_number}",
                description=step_name,
                step_number=step_number,
                desk=desk,
            )
            tool_result = tool.run()
            if step_number == 1:
                assert desk.output_dir
                self.runtime.set_output_dir(desk.output_dir)
                self.runtime.save_node("Data Step 1", "input", envelope)
            self.runtime.save_node(f"Data Step {step_number}", "output", {"result": tool_result})
        return {"output_dir": str(desk.output_dir), "report_period": desk.report_period}

    @listen(data_steps)
    def research_analyst(self, data_result: dict[str, Any]) -> str:
        assert self.runtime and self.runtime.desk and self.runtime.output_dir
        print("Node starting: Research Analyst", flush=True)
        context = self.runtime.research_context()
        self.contexts["Research Analyst"] = context
        envelope = self.runtime.envelope(
            "Analyze the business model, competitive position, catalysts, and recent developments from the 10-K Business and MD&A sections and earnings release.",
            context,
            "JSON object with draft string. Every factual claim includes an exact quote and source line citation.",
        )
        result = self.runtime.role_call("Research Analyst", "research_analyst.md", envelope)
        self.role_outputs["Research Analyst"] = str(result.get("draft", ""))
        return self.role_outputs["Research Analyst"]

    @listen(research_analyst)
    def financial_analyst(self, research_output: str) -> str:
        assert self.runtime and self.runtime.desk
        print("Node starting: Financial Analyst", flush=True)
        context = self.runtime.financial_context()
        self.contexts["Financial Analyst"] = context
        envelope = self.runtime.envelope(
            "Analyze annual facts, supplied calculations, the latest quarter, and peers. Do not calculate in the model.",
            context,
            "JSON object with draft string and calculator_requests array.",
        )
        result = self.runtime.role_call("Financial Analyst", "financial_analyst.md", envelope)
        self.role_outputs["Financial Analyst"] = str(result.get("draft", ""))
        return self.role_outputs["Financial Analyst"]

    @listen(financial_analyst)
    def investment_advisor(self, financial_output: str) -> str:
        assert self.runtime
        print("Node starting: Investment Advisor", flush=True)
        context = {
            "research_analyst_output": self.role_outputs["Research Analyst"],
            "financial_analyst_output": self.role_outputs["Financial Analyst"],
        }
        self.contexts["Investment Advisor"] = context
        envelope = self.runtime.envelope(
            "Form a thesis and Buy, Hold, or Sell recommendation from the two analyst outputs only.",
            context,
            "JSON object with draft string containing one rating and one cited deciding number.",
        )
        result = self.runtime.role_call("Investment Advisor", "investment_advisor.md", envelope)
        self.role_outputs["Investment Advisor"] = str(result.get("draft", ""))
        return self.role_outputs["Investment Advisor"]

    @listen(investment_advisor)
    def strategy_manager(self, advisor_output: str) -> str:
        assert self.runtime and self.runtime.desk and self.runtime.output_dir
        print("Node starting: Strategy Manager", flush=True)
        first = self._manager_call("Review and compile")
        failures = first.get("failures", [])
        sections = first.get("sections", {})
        owner = {
            "Overview": "Research Analyst",
            "Market Positioning and Growth Outlook": "Research Analyst",
            "Valuation Insights": "Financial Analyst",
            "Future Developments and Strategic Recommendations": "Research Analyst",
            "Investment Recommendation": "Investment Advisor",
        }
        flagged = {item.get("part") for item in failures if isinstance(item, dict)}
        for section in SECTIONS:
            if section not in flagged and not str(sections.get(section, "")).strip():
                failures.append({"role": owner[section], "part": section, "feedback": "This required report part is missing. Provide sourced content."})
                flagged.add(section)
        for failure in insight_failures(sections):
            if failure["part"] in flagged:
                existing = next(item for item in failures if item.get("part") == failure["part"])
                existing["feedback"] += " " + failure["feedback"]
            else:
                failures.append(failure)
                flagged.add(failure["part"])
        feedback: dict[str, list[str]] = {}
        for failure in failures:
            role = failure.get("role")
            if role in {"Research Analyst", "Financial Analyst", "Investment Advisor"}:
                feedback.setdefault(role, []).append(f"{failure.get('part')}: {failure.get('feedback')}")
        for role, notes in feedback.items():
            context = {
                "original_context": self.contexts[role],
                "prior_draft": self.role_outputs[role],
                "manager_feedback": notes,
            }
            if role == "Investment Advisor":
                context["original_context"] = {
                    "research_analyst_output": self.role_outputs["Research Analyst"],
                    "financial_analyst_output": self.role_outputs["Financial Analyst"],
                }
            retry = self.runtime.envelope(
                "Correct only the failing report part once. Use the original assigned context and Strategy Manager feedback.",
                context,
                "JSON object with corrected draft string.",
            )
            filename = {
                "Research Analyst": "research_analyst.md",
                "Financial Analyst": "financial_analyst.md",
                "Investment Advisor": "investment_advisor.md",
            }[role]
            corrected = self.runtime.role_call(role, filename, retry)
            self.role_outputs[role] = str(corrected.get("draft", ""))
        if failures:
            final = self._manager_call("Compile after one permitted correction", failures)
        else:
            final = first
        sections = final.get("sections", {})
        remaining = insight_failures(sections)
        if remaining:
            self.runtime.save_node("Strategy Manager", "output", {"sections": sections, "failures": remaining})
            raise ValueError("Report still violates one Insight per role after the permitted correction: " + "; ".join(item["feedback"] for item in remaining))
        filings_line = "Filings read: " + ", ".join(
            f"{form} {self.runtime.desk.filings[form].accession}" for form in ("10-K", "10-Q", "8-K")
        )
        content = [filings_line, f"Run time: {self.runtime.desk.run_timestamp}", ""]
        for section in SECTIONS:
            content.extend([f"## {section}", str(sections.get(section, "Not provided by Strategy Manager.")), ""])
        self.report_path = self.runtime.output_dir / "report.md"
        self.report_path.write_text("\n".join(content), encoding="utf-8")
        self.runtime.save_node("Strategy Manager", "output", {"sections": sections, "report": str(self.report_path)})
        return str(self.report_path)

    def _manager_call(self, task: str, failures: Any = None) -> dict[str, Any]:
        assert self.runtime and self.runtime.output_dir
        envelope = self.runtime.envelope(
            f"{task}. Check all five requested report parts and consistency. Require exactly one Insight: line per analyst role, three total. Place the Research Analyst Insight only at the end of Future Developments and Strategic Recommendations, the Financial Analyst Insight at the end of Valuation Insights, and the Investment Advisor Insight at the end of Investment Recommendation. Overview and Market Positioning and Growth Outlook must have no Insight line. Fail the responsible role if its Insight count is not one, is misplaced, or only repeats a figure in the earnings release first narrative paragraph. Return role, part, and feedback for each failure. Do not calculate or add facts.",
            {"role_outputs": self.role_outputs, "required_sections": list(SECTIONS), "previous_failures": failures or [], "earnings_release": numbered_lines(self.runtime.output_dir / "earnings_release_Ex99-1.txt")},
            "JSON object with failures array and sections object keyed by the five exact section names.",
        )
        self.runtime.save_node("Strategy Manager", "input", envelope)
        result = self.runtime.role_call(
            "Strategy Manager",
            "strategy_manager.md",
            envelope,
        )
        return result

    @listen(strategy_manager)
    def verifier(self, report_path: str) -> str:
        assert self.runtime
        verified = self.runtime.verify(Path(report_path), Path(report_path).with_name("verified_report.md"))
        return str(verified)


class VerifyOnlyFlow(Flow):
    def __init__(self, source: Path):
        super().__init__()
        self.source = source.expanduser().resolve()

    @start()
    def verify_saved_run(self) -> str:
        source = self.source
        if not source.is_dir():
            raise ValueError(f"Saved run folder does not exist: {source}")
        source_facts = source / "facts.json"
        source_report = source / "report.md"
        if not source_report.exists():
            source_report = source / "equity_research_report.md"
        if not source_facts.exists() or not source_report.exists():
            raise ValueError("Saved run must contain report.md (or equity_research_report.md) and facts.json")
        company = json.loads(source_facts.read_text(encoding="utf-8")).get("company") or source.name
        number = report_number(source, OUTPUT_ROOT, company)
        target = create_run(OUTPUT_ROOT, company, datetime.now().astimezone(), "verify", number)
        shutil.copytree(source, target, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("verified_report.md", "run_identity.json"))
        copied_report = target / "report.md"
        if source_report.name != "report.md":
            shutil.copy2(target / source_report.name, copied_report)
        runtime = Runtime()
        runtime.set_output_dir(target)
        runtime.save_node("Verifier", "input", {"source_run": str(source)})
        verified = runtime.verify(target / "report.md", target / "verified_report.md")
        return str(verified)


def run_cli(args: Any) -> int:
    if args.verify_only:
        if args.ticker or args.peers or args.price is not None or args.filed is not None:
            raise ValueError("--verify-only cannot be combined with ticker, --peers, --price, or --filed")
        result = VerifyOnlyFlow(Path(args.verify_only)).kickoff()
        print(f"Verified report: {result}")
        return 0
    if not args.ticker:
        raise ValueError("ticker is required unless --verify-only is used")
    peers = [part.strip() for item in (args.peers or []) for part in item.split(",") if part.strip()]
    result = EquityResearchFlow(args.ticker, peers, filed=args.filed).kickoff()
    print(f"Verified report: {result}")
    return 0
