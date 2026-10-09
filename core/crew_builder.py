
from crewai import Agent, Crew, Process, Task
from core.config import MODEL_NAME
from core.groq_client import chat, GroqServiceError
from research.verified_search import search_verified_sources


def _run_agent(role: str, goal: str, task_text: str, evidence: str) -> str:
    system = f"""
You are the {role} in a business-launch consulting team.

Goal:
{goal}

STRICT EVIDENCE POLICY:
1. You may use only the supplied VERIFIED SOURCES for factual claims about laws,
   registration, licenses, taxes, government programs, statistics, or official requirements.
2. Never invent a law, fee, deadline, license, office, statistic, market fact, or website.
3. If the evidence does not establish a fact, write exactly: "Not verified from the approved sources."
4. Recommendations and assumptions must be clearly labelled as recommendations or assumptions.
5. Preserve source URLs when referring to evidence.
6. Keep advice practical for a beginner.
"""

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                f"BUSINESS REQUEST:\n{task_text}\n\n"
                f"VERIFIED SOURCE MATERIAL:\n{evidence}"
            ),
        },
    ]
    return chat(messages, MODEL_NAME)


def run_consulting_crew(inputs: dict) -> dict:
    sources = search_verified_sources(
        inputs["country"], inputs["city"], inputs["business_idea"]
    )

    source_text = "\n\n".join(
        f"[SOURCE {i+1}] {s['title']}\nURL: {s['url']}\nDOMAIN: {s['domain']}\n"
        f"SEARCH SNIPPET: {s['snippet']}"
        for i, s in enumerate(sources)
    )

    if not source_text:
        source_text = (
            "NO VERIFIED SOURCE WAS RETRIEVED. Do not make factual legal/tax/licensing claims. "
            "State that the requirement is not verified."
        )

    business_request = (
        f"Country: {inputs['country']}\n"
        f"City/region: {inputs['city']}\n"
        f"Business idea: {inputs['business_idea']}\n"
        f"Business size: {inputs['business_size']}\n"
        f"Budget: {inputs['budget'] or 'Not provided'}\n"
        f"Environment: {inputs['online_or_physical']}\n"
        f"Experience: {inputs['experience']}"
    )

    # CrewAI provides the orchestration layer. We use explicit sequential tasks,
    # while the Groq wrapper gives us retry/error handling and the verified
    # research is performed before LLM reasoning.
    analyst = Agent(
        role="Business Discovery Analyst",
        goal="Turn the user's idea into a clear business model and list what must be researched.",
        backstory="You are a careful business analyst who separates known facts from assumptions.",
        allow_delegation=False,
        verbose=False,
    )

    compliance = Agent(
        role="Regulatory and Requirements Analyst",
        goal="Identify only requirements supported by the supplied approved sources.",
        backstory="You never guess legal, tax, licensing, or registration requirements.",
        allow_delegation=False,
        verbose=False,
    )

    strategist = Agent(
        role="Startup Strategy Advisor",
        goal="Convert verified facts into a practical first-step launch sequence.",
        backstory="You give beginner-friendly recommendations and label assumptions clearly.",
        allow_delegation=False,
        verbose=False,
    )

    auditor = Agent(
        role="Evidence and Hallucination Auditor",
        goal="Audit the draft and remove unsupported factual claims.",
        backstory="You reject unsupported claims and require a source for factual requirements.",
        allow_delegation=False,
        verbose=False,
    )

    # The CrewAI Task objects are used for the workflow definition.
    # We execute the LLM calls through our Groq wrapper so retry behavior is explicit.
    analysis_task = Task(
        description="Analyze the user's business idea and identify business-model questions.",
        expected_output="A concise business analysis with assumptions clearly labelled.",
        agent=analyst,
    )
    compliance_task = Task(
        description="Extract verified registration, tax, licensing and official-program information.",
        expected_output="A source-grounded requirements checklist.",
        agent=compliance,
        context=[analysis_task],
    )
    strategy_task = Task(
        description="Create a practical launch sequence using the verified evidence.",
        expected_output="A prioritized startup sequence.",
        agent=strategist,
        context=[compliance_task],
    )
    audit_task = Task(
        description="Audit all claims and remove anything unsupported.",
        expected_output="A final source-grounded report.",
        agent=auditor,
        context=[strategy_task],
    )

    crew = Crew(
        agents=[analyst, compliance, strategist, auditor],
        tasks=[analysis_task, compliance_task, strategy_task, audit_task],
        process=Process.sequential,
        verbose=False,
    )

    # Run the same defined workflow in controlled calls. This avoids making
    # undocumented assumptions about provider-specific tool calling.
    analysis = _run_agent(
        analyst.role,
        analyst.goal,
        business_request,
        source_text,
    )

    compliance_text = _run_agent(
        compliance.role,
        compliance.goal,
        business_request + f"\n\nPREVIOUS ANALYSIS:\n{analysis}",
        source_text,
    )

    strategy_text = _run_agent(
        strategist.role,
        strategist.goal,
        business_request + f"\n\nANALYSIS:\n{analysis}\n\nREQUIREMENTS:\n{compliance_text}",
        source_text,
    )

    final_report = _run_agent(
        auditor.role,
        auditor.goal,
        (
            business_request
            + f"\n\nANALYSIS:\n{analysis}"
            + f"\n\nREQUIREMENTS:\n{compliance_text}"
            + f"\n\nSTARTUP STRATEGY:\n{strategy_text}"
            + "\n\nProduce the final answer with these headings:\n"
              "1. Best place/environment to start\n"
              "2. What you need before starting\n"
              "3. Step-by-step launch order\n"
              "4. Budget considerations\n"
              "5. Main risks\n"
              "6. What is verified vs not verified\n"
              "7. Official sources"
        ),
        source_text,
    )

    return {"report": final_report, "sources": sources}
