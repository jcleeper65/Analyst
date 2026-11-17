"""Exercise the actual CrewAI tool loop with a seeded stub, in a child process."""
import os
from pathlib import Path
import socket
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def denied(*args,**kwargs):raise RuntimeError('Seeded tool test cannot fetch')
socket.socket.connect=denied

with tempfile.TemporaryDirectory() as tmp:
    run=Path(tmp)
    os.environ['CREWAI_STORAGE_DIR']=str(run/'framework')
    from desk_stub_llm import StubLLM,tool_call
    from equity_research_agent_team import Runtime
    from desk_hook import Hook
    from desk_sources import Sources
    from desk_files import AssignedFiles,file_tool

    source=run/'skill.md';source.write_text('Computed amount: $100\n')
    runtime=Runtime.__new__(Runtime)
    runtime.output_dir=run;runtime.set_output_dir(run)
    runtime.role_call_counts={};runtime.skill_files=[source]
    gate=Hook(run,Sources(run,''))
    runtime.output_hook=lambda name,paths:gate.check(name,paths)
    runtime.llm=StubLLM(emit_events=False,responses=[
        tool_call('read_assigned_file',{'file':'skill.md'}),
        'Final Answer: {"draft":"Amount is $100 [skill.md:L1]."}'])
    packet={'task':'Quote the assigned file.','context':{},'expected_output':'JSON with draft.'}
    result=runtime.role_call('Research Analyst','research_analyst.md',packet)
    assert '$100' in result['draft']
    assert (run/'nodes/Research_Analyst_1/files_read.json').is_file()

    # A role that skips the read cannot publish an output.
    runtime.llm=StubLLM(emit_events=False,responses=['Final Answer: {"draft":"No read."}'])
    try:runtime.role_call('Research Analyst','research_analyst.md',packet)
    except ValueError as error:assert 'did not read' in str(error)
    else:raise AssertionError('Unread assigned file was accepted')
    assert not (run/'nodes/Research_Analyst_2/output.json').exists()

    # Test the real ToolFailure path with strict CrewAI failure policy.
    runtime.llm=StubLLM(emit_events=False,responses=[tool_call('read_assigned_file',{'file':'secret.env'})])
    try:runtime.role_call('Investment Advisor','investment_advisor.md',packet)
    except Exception as error:assert 'not assigned' in str(error) or 'failed' in str(error).lower(),str(error)
    else:raise AssertionError('Unassigned file was accepted')
    assert not (run/'nodes/Investment_Advisor_1/output.json').exists()

    # Reading a valid file does not permit changing a quoted amount.
    runtime.llm=StubLLM(emit_events=False,responses=[
        tool_call('read_assigned_file',{'file':'skill.md'}),
        'Final Answer: {"draft":"Amount is $101 [skill.md:L1]."}'])
    try:runtime.role_call('Financial Analyst','financial_analyst.md',packet)
    except ValueError as error:assert '$101' in str(error)
    else:raise AssertionError('Changed financial amount was accepted')

print('SEEDED real file-tool smoke check passed')
