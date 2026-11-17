"""Claims ledger: the model selects evidence, code checks it and writes every number.

The research role returns
    {"claims": [...], "draft": "prose with {c1} placeholders"}

Each claim is one of:
    {"id": "c1", "file": "earnings_release_Ex99-1.txt", "line": 10,
     "quote": "Net sales for the quarter increased 11.2 percent, to $93.9 billion",
     "value": "$93.9 billion", "metric": "Q4 net sales", "period": "Q4 FY2026"}
    {"id": "c2", "fact": "net_income", "which": "value"}           # from facts.json

Checking is literal, not interpretive:
  * the quote must appear on the cited line,
  * the value must appear inside the quote, copied character for character,
  * the prose may not contain a financial number outside a {cN} placeholder.

Because the value is a substring of the quote, a wrong amount, scale, or line fails
without any unit parsing. Scale ("amounts in millions") is decided here, from the
filing's own section header, never by the model.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from desk_quantities import SMALL,TENS,SCALES,enumeration_spans,heading_spans

PLACEHOLDER = re.compile(r"\{(c\d+)\}")
SCALE_WORD = re.compile(r"\b(thousand|million|billion|trillion)s?\b", re.I)
HEADER = re.compile(r"\(amounts in (thousands|millions|billions)([^)]*)\)", re.I)
SECTION = re.compile(r"^Item\s+\d+[A-C]?\s*[—\-–.]", re.I)
QUARTER = re.compile(r"\b(?:Q[1-4]|FY\d{2,4}|H[12])\b")
# Allowed bare digits: list labels "(1)" or "1." at line start, Item numbers, ordinals in dates.
LIST_LABEL = re.compile(r"(?:^|\n)\s*(?:\(\d{1,2}\)|\d{1,2}[.)])\s|\(\d{1,2}\)")
ITEM_REF = re.compile(r"\bItem\s+\d+[A-C]?\b", re.I)
LABEL_REF=re.compile(r'\b(?:section|criterion|table|figure|chapter)\s+\d+\b|\bclaim\s+c\d+\b',re.I)
ISO_DATE=re.compile(r'(?<![\w$])\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?\b')
TEXT_DATE=re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(?:19|20)\d{2}\b')
ACCESSION_REF=re.compile(r'\b\d{10}-\d{2}-\d{6}\b')
FORM_REF = re.compile(r'\b(?:10-K|10-Q|8-K|20-F|40-F|6-K)(?:/A)?\b|\bForm\s+(?:3|4|5|10|144)\b',re.I)
NUMBER_WORDS = '|'.join(SMALL|TENS|SCALES|{'hundred':100})
UNIT_WORDS = (r"percent|percentage points?|basis points?|bps|trillion|billion|million|thousand|"
              r"warehouses?|stores?|members?|shares?|units?|cents?|dollars?|USD|EUR|GBP|times|x")
YEAR = re.compile(r'\b(?:fiscal(?:\s+year)?|year|in|for|during|the|from|since|through|versus|vs\.?|with)\s+(?:19|20)\d{2}\b(?!\s*(?:'+UNIT_WORDS+r')\b)|(?<![\w$.,])(?:19|20)\d{2}(?=\s+(?:net\s+(?:sales|income)|gross\s+margin|fiscal\s+year|revenue|results)\b)',re.I)
WORD_AMOUNT = re.compile(
    rf"\b(?:{NUMBER_WORDS})(?:[\s-]+(?:{NUMBER_WORDS}))*\s+(?:{UNIT_WORDS})\b", re.I)


def _norm(text: str) -> str:
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text).strip()


def complete_value(value,quote,source):
    """Require a complete literal value, not part of a larger amount or unit."""
    if len(re.findall(r'\d[\d,]*(?:\.\d+)?',value))>1:return False
    for q in re.finditer(re.escape(quote),source):
        for v in re.finditer(re.escape(value),quote):
            start,end=q.start()+v.start(),q.start()+v.end()
            left,right=source[:start],source[end:]
            if left and (left[-1].isalnum() or left[-1] in '$€£.,−-'):continue
            if right and (right[0].isalnum() or right[0] in '%'):continue
            if re.match(r'[.,]\d',right):continue
            if re.match(r'\s*(?:thousand|million|billion|trillion)s?\b|\s*(?:percent(?:age)?|basis\s+points?|bps|USD|EUR|GBP|dollars?)\b',right,re.I):continue
            if not re.search(r'\d|\b(?:'+NUMBER_WORDS+r')\b',value,re.I):continue
            return True
    return False


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    rendered: str = ""
    values: dict[str,str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def repair_message(self) -> str:
        """Text to send back to the model for a targeted retry."""
        return ("Your output failed these checks. Fix only the listed items and return the "
                "full JSON again:\n- " + "\n- ".join(self.errors))


def section_scale(lines: list[str], index: int) -> tuple[str | None, str]:
    """Scale declared by the nearest '(amounts in ...)' header above, within the same Item."""
    for i in range(index, -1, -1):
        match = HEADER.search(lines[i])
        if match:
            return match.group(1).lower().rstrip("s"), match.group(2).lower()
        if i < index and SECTION.match(lines[i].strip()):
            return None, ""
    return None, ""


def display_value(claim: dict, lines: list[str]) -> str:
    """Literal source value, with the section's scale added only where the filing implies it."""
    value = claim["value"].strip()
    if not value.startswith("$") or SCALE_WORD.search(value):
        return value
    scale, exceptions = section_scale(lines, claim["line"] - 1)
    if not scale:
        return value
    # The short quote may end at the value; its per-share qualifier is still
    # present on the saved filing line and must not be lost.
    quote = _norm(lines[claim['line']-1])
    quote_start=quote.find(_norm(claim['quote']))
    start=quote_start+_norm(claim['quote']).find(value)
    after = quote[start + len(value):][:30].lower()
    if "per share" in exceptions and re.match(r"\s*(?:,\s*)?(?:or\s+)?per\s+(?:\w+\s+)?share", after):
        return value
    return f"{value} {scale}"


def format_fact(key: str, fact: dict, which: str) -> str:
    value = fact.get(which)
    if value is None:
        raise ValueError(f"facts.json {key}.{which} is empty")
    value=Decimal(str(value))
    def exact(value):
        text=format(value,',f')
        return text.rstrip('0').rstrip('.') if '.' in text else text
    if "eps" in key or "per_share" in key:
        return '$'+exact(value)
    for size, word in ((Decimal('1e12'), "trillion"), (Decimal('1e9'), "billion"), (Decimal('1e6'), "million")):
        if abs(value) >= size:
            return '$'+exact(value/size)+f' {word}'
    return '$'+exact(value)


def check(output: dict[str, Any], texts: dict[str, str], facts: dict[str, Any] | None = None,origins=None,reference_only=False) -> Result:
    result = Result()
    if not isinstance(output,dict):
        result.errors.append('Return JSON with "claims" (array) and "draft" (string).')
        return result
    claims = output.get("claims")
    draft = output.get("draft")
    if not isinstance(claims, list) or not isinstance(draft, str):
        result.errors.append('Return JSON with "claims" (array) and "draft" (string).')
        return result

    rendered: dict[str, str] = {}
    fact_table = (facts or {}).get("facts", {})
    ids=set()
    for claim in claims:
        if not isinstance(claim,dict):
            result.errors.append('Each claim must be a JSON object.')
            continue
        cid = claim.get("id", "?")
        if not isinstance(cid,str) or not PLACEHOLDER.fullmatch('{'+cid+'}'):
            result.errors.append('Each claim id must have the form c1, c2, and so on.')
            continue
        if cid in ids:
            result.errors.append(f"{cid}: duplicate claim id.")
            continue
        ids.add(cid)
        if 'from' in claim:
            origin=claim.get('from');reference=claim.get('claim')
            key=claim.get('from_file',origin)
            if not isinstance(origin,str) or not isinstance(reference,str) or not isinstance(key,str) or reference not in (origins or {}).get(key,{}):
                result.errors.append(f'{cid}: referenced analyst claim is not available.')
                continue
            if key!=origin and not re.fullmatch('nodes/'+re.escape(origin.replace(' ','_'))+r'_[12]/output\.json',key):
                result.errors.append(f'{cid}: referenced file does not belong to the named analyst.')
                continue
            rendered[cid]=origins[key][reference]
            continue
        if reference_only:
            result.errors.append(f'{cid}: use an existing analyst claim with from and claim; do not add a value.')
            continue
        if 'computed' in claim or 'quarter' in claim:
            group='metrics' if 'computed' in claim else 'quarter_results'
            key=claim.get('computed',claim.get('quarter'))
            try:
                saved=json.loads(texts['calculated_facts.json'])
                if not isinstance(key,str):raise ValueError('key must be a string')
                entry=saved[group][key]
                if not isinstance(entry,dict) or entry.get('value') is None:raise ValueError('saved value is unavailable; state that limitation without a numeric claim')
                import ast,operator,math
                ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
                def evaluate(node):
                    if isinstance(node,ast.Constant) and type(node.value) in (int,float):return Decimal(str(node.value))
                    if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):return (-1 if isinstance(node.op,ast.USub) else 1)*evaluate(node.operand)
                    if isinstance(node,ast.BinOp) and type(node.op) in ops:return ops[type(node.op)](evaluate(node.left),evaluate(node.right))
                    raise ValueError('unsupported saved formula')
                formula=entry.get('formula','')
                expected=evaluate(ast.parse(formula,mode='eval').body)
                if entry.get('unit')=='%' and not re.search(r'\*\s*100\b',formula):expected*=100
                if not math.isclose(float(expected),float(entry['value']),rel_tol=1e-12,abs_tol=1e-12):raise ValueError('saved calculation does not match its formula')
                unit=entry.get('unit')
                if unit=='USD':shown=format_fact(key,entry,'value')
                elif unit=='%':shown=str(entry['value'])+'%'
                elif unit=='ratio':shown=str(entry['value'])+' times'
                else:raise ValueError('saved calculation has no supported unit')
                sources=entry.get('sources',[])
                if not sources or any(s=='not available' for s in sources):raise ValueError('saved calculation has no source evidence')
                rendered[cid]=shown+f' [saved calculated_facts.json#/{group}/{key}; computed, rechecked given calculations; formula {formula}; inputs: '+'; '.join(sources)+']'
            except (KeyError,TypeError,ValueError,SyntaxError,ArithmeticError) as error:result.errors.append(f'{cid}: {error}')
            continue
        if "fact" in claim:
            key, which = claim["fact"], claim.get("which", "value")
            if not isinstance(key,str) or which not in ('value','prior_value'):
                result.errors.append(f'{cid}: fact must name a saved key and which must be value or prior_value.')
                continue
            peer=claim.get('peer')
            table=fact_table if peer is None else (facts or {}).get('peers',{}).get(peer,{}).get('facts',{}) if isinstance(peer,str) else {}
            fact = table.get(key)
            if not fact or fact.get(which) is None or not fact.get("tag"):
                result.errors.append(f"{cid}: facts.json has no value for {key}.{which}.")
                continue
            period = fact.get("period_end" if which == "value" else "prior_period_end")
            filing = fact.get("filing" if which == "value" else "prior_filing")
            if not period or not filing:
                result.errors.append(f'{cid}: saved fact has no period or filing.')
                continue
            rendered[cid] = (f"{format_fact(key, fact, which)} "
                             f"[XBRL tag {fact['tag']}, period end {period}, filing {filing}]")
            continue

        name, line_no = claim.get("file"), claim.get("line")
        quote, value = claim.get("quote", ""), claim.get("value", "")
        if not isinstance(name,str) or name not in texts:
            result.errors.append(f"{cid}: file {name!r} is not one of your supplied sources.")
            continue
        lines = texts[name].splitlines()
        if type(line_no) is not int or not 1 <= line_no <= len(lines):
            result.errors.append(f"{cid}: {name} has no line {line_no}.")
            continue
        source_line = _norm(lines[line_no - 1])
        if not isinstance(quote,str) or not isinstance(value,str):
            result.errors.append(f'{cid}: quote and value must be strings.')
            continue
        if not quote or _norm(quote) not in source_line:
            hits = [i + 1 for i, l in enumerate(lines) if quote and _norm(quote) in _norm(l)]
            hint = f" It appears on line {hits[0]}." if hits else " It does not appear in that file."
            result.errors.append(f"{cid}: quote is not on {name}:L{line_no}.{hint}")
            continue
        if not value or _norm(value) not in _norm(quote):
            result.errors.append(
                f"{cid}: value {value!r} must be copied exactly from the quote; it is not in it.")
            continue
        if not complete_value(_norm(value),_norm(quote),source_line):
            result.errors.append(f'{cid}: value must be a complete amount and unit copied from the cited line, not a substring of a larger value.')
            continue
        claim = {**claim, "value": _norm(value), "line": line_no}
        rendered[cid] = f'{display_value(claim, lines)} [{name}:L{line_no}]'

    used = set(PLACEHOLDER.findall(draft))
    for cid in sorted(used - rendered.keys() - ids):
        result.errors.append(f"{{{cid}}} is used in the draft but no claim has that id.")
    for cid in sorted(ids - used):
        result.errors.append(f"{cid} is never used in the draft; remove it or place it.")

    for n, line in enumerate(draft.splitlines(), 1):
        prose = PLACEHOLDER.sub("", line)
        prose = re.sub(r"\[[\w./-]+\.txt:L\d+\]", "", prose) # source identifiers only
        for start,end in reversed(enumeration_spans(prose)):
            prose=prose[:start]+' '*(end-start)+prose[end:]
        for allowed in (ISO_DATE,TEXT_DATE,ACCESSION_REF,YEAR, QUARTER, ITEM_REF, FORM_REF,LABEL_REF):
            prose = allowed.sub(" ", prose)
        for start,end in reversed(heading_spans(prose)):
            prose=prose[:start]+' '*(end-start)+prose[end:]
        for match in re.finditer(r"[$%]?\d[\d,.]*%?", prose):
            result.errors.append(
                f"draft line {n}: number {match.group(0)!r} is typed directly; use a {{cN}} claim.")
        for match in WORD_AMOUNT.finditer(prose):
            result.errors.append(
                f"draft line {n}: written amount {match.group(0)!r} must be a {{cN}} claim.")

    if result.ok:
        result.values=rendered
        result.rendered = PLACEHOLDER.sub(lambda m: rendered[m.group(1)], draft)
    return result


SOURCE_FILES = ("10-K.txt", "10-Q.txt", "earnings_release_Ex99-1.txt",'calculated_facts.json')


def load_sources(run) -> tuple[dict[str, str], dict[str, Any]]:
    """Filing texts and saved XBRL facts from a run folder, as the hook reads them."""
    run = Path(run)
    texts = {name: (run / name).read_text(encoding="utf-8", errors="replace")
             for name in SOURCE_FILES if (run / name).is_file()}
    facts = json.loads((run / "facts.json").read_text()) if (run / "facts.json").is_file() else {}
    return texts, facts


def verify_saved(run, data: dict[str, Any],role=None) -> list[str]:
    """Hook check for a saved claims output: recheck every claim and the rendering."""
    texts, facts = load_sources(run)
    role=role or data.get('role','Research Analyst')
    from desk_role_contracts import origins_for
    try:origins=origins_for(run,role)
    except ValueError as error:return [str(error)]
    result = check({"claims": data.get("claims"), "draft": data.get("template")}, texts, facts,origins,role=='Investment Advisor')
    if result.ok and result.rendered != data.get("draft"):
        return ["Saved draft differs from the rendering of its checked claims and template."]
    return result.errors


def with_repairs(ask, texts: dict[str, str], facts: dict[str, Any], repairs: int = 2,on_attempt=None,validator=None):
    """Call ask(feedback) until the claims pass, sending each failure back once.

    ask(None) is the first call; ask(message) is a repair call. Returns
    (final_output_dict, attempts) where attempts lists every raw output and its errors.
    Raises ValueError with the remaining errors when repairs run out.
    """
    attempts, feedback = [], None
    for _ in range(repairs + 1):
        raw = ask(feedback)
        result = validator(raw) if validator else check(raw, texts, facts)
        attempts.append({"output": raw, "errors": result.errors})
        if on_attempt:on_attempt(attempts)
        if result.ok:
            if hasattr(result,'output'):return {**result.output,'claim_attempts':len(attempts)},attempts
            return {"claims": raw["claims"], "template": raw["draft"], "draft": result.rendered,
                    "claim_attempts": len(attempts)}, attempts
        feedback = result.repair_message()
    raise ValueError("Role claims still fail after repairs:\n- " + "\n- ".join(result.errors))
