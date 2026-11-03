# Analyst

Weak human + machine + better process

## Equity research agent team

CrewAI currently supports Python 3.10 through 3.13. This computer has Python 3.14 as `python3`, so use `python3.13` for install and run.

Install the packages:

```bash
python3.13 -m pip install -r requirements.txt
```

Run the fixed-order team with a ticker, peers, and a price:

```bash
python3.13 equity_research_desk.py COST --peers WMT,TGT,BJ --price 992.13
```

Verify a saved run without rerunning its data steps or analyst roles:

```bash
python3.13 equity_research_desk.py --verify-only "equity_research_output/<run-folder>"
```

Put `API_KEY` and `SEC_USER_AGENT` in `.env`. The default model is `gemini/gemini-3.5-flash-lite`. Set `MODEL` to another CrewAI model name if needed, such as `openai/gpt-5.6-terra`. The value in `API_KEY` is passed to that provider. For an OpenAI-compatible gateway, set `LLM_BASE_URL` and `MODEL` in `.env`.
