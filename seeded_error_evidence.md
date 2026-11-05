# Seeded EPS audit evidence

The original seeded test result is [verify 4](<equity_research_output/COSTCO WHOLESALE CORP _NEW, 2026-11-03, 09-46-52, verify 4/verified_report.md>). Its model detected the seeded error. Its code checks did not establish claim support. The saved P/E mark is inconsistent, and the EPS correction cites the release rather than the required 10-K row.

The [tampered report copy](<equity_research_output/COSTCO WHOLESALE CORP _NEW, 2026-11-03, 09-46-48, report 4 (EPS TAMPER COPY (Seeded))/report.md>) retains a stale copied verified_report.md; do not use that copied verification as evidence of detection.

New verification runs preserve the original artifacts. See the newer verify 3 and verify 4 folders for results from the revised verifier; completion must be checked before using those results.

## Revised deterministic results

- [Clean report code checks](<equity_research_output/COSTCO WHOLESALE CORP _NEW, 2026-11-05, 08-31-50, verify 3/nodes/Verifier_Code/output.json>)
- [Seeded report code checks](<equity_research_output/COSTCO WHOLESALE CORP _NEW, 2026-11-05, 08-31-51, verify 4/nodes/Verifier_Code/output.json>)

The revised code detects the altered EPS quotation and cites the 10-K per-share value at line 1221, with the Diluted label, period, and accession. Matching quotations remain unsupported until claim meaning and period receive model review. Correct formula arithmetic is checked separately from source validity.

The clean live rerun failed with provider 503 UNAVAILABLE. These deterministic results do not establish successful completion of model verification.
