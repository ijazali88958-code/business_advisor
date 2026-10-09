

import streamlit as st

from core.crew_builder import run_consulting_crew
from core.validators import validate_inputs

st.set_page_config(
    page_title="Business Launch Advisor",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Business Launch Advisor")
st.write(
    "A source-grounded multi-agent business planning app for people "
    "who want to start a small or large business."
)

with st.sidebar:
    st.header("Business information")

    country = st.text_input("Country", placeholder="e.g. Pakistan")
    city = st.text_input("City / region", placeholder="e.g. Lahore")

    business_idea = st.text_area(
        "What business do you want to start?",
        placeholder="e.g. small bakery, online clothing store, software agency",
    )

    business_size = st.selectbox(
        "Business size",
        ["Micro / home-based", "Small", "Medium", "Large / growing"],
    )

    budget = st.text_input(
        "Approximate starting budget",
        placeholder="e.g. PKR 1,000,000 or USD 10,000",
    )

    online_or_physical = st.selectbox(
        "Business environment",
        ["Online", "Physical location", "Both"],
    )

    experience = st.selectbox(
        "Your experience",
        ["Beginner", "Some experience", "Experienced"],
    )

    run = st.button(
        "Create verified startup plan",
        type="primary",
        use_container_width=True,
    )

if run:
    inputs = {
        "country": country.strip(),
        "city": city.strip(),
        "business_idea": business_idea.strip(),
        "business_size": business_size,
        "budget": budget.strip(),
        "online_or_physical": online_or_physical,
        "experience": experience,
    }

    try:
        errors = validate_inputs(inputs)
    except Exception:
        st.error("Input validation failed. Check the application logs.")
        st.stop()

    if errors:
        for error in errors:
            st.error(error)
        st.stop()

    with st.status(
        "Researching sources and building your plan...",
        expanded=True,
    ) as status:
        try:
            result = run_consulting_crew(inputs)

            if not isinstance(result, dict):
                raise TypeError(
                    "run_consulting_crew must return a dictionary."
                )

            if not isinstance(result.get("report"), str):
                raise TypeError(
                    "The result must contain a string named 'report'."
                )

            sources = result.get("sources", [])

            if not isinstance(sources, list):
                raise TypeError(
                    "The result field 'sources' must be a list."
                )

            status.update(
                label="Plan completed",
                state="complete",
                expanded=False,
            )

        except Exception:
            status.update(
                label="The plan could not be completed",
                state="error",
                expanded=True,
            )
            st.error(
                "The consulting workflow failed. "
                "Open Manage app → Logs to inspect the full traceback. "
                "Do not share API keys or other secrets."
            )
            st.stop()

    st.success("Your startup plan is ready.")

    st.markdown("## Your business launch plan")
    st.markdown(result["report"])

    st.markdown("## Sources returned by the workflow")

    if sources:
        for source in sources:
            if not isinstance(source, dict):
                st.warning("A source entry has an unexpected format.")
                continue

            title = source.get("title", "Untitled source")
            domain = source.get("domain", "Unknown domain")
            url = source.get("url", "")

            st.markdown(f"- **{title}** — {domain}")

            if isinstance(url, str) and url.startswith(
                ("https://", "http://")
            ):
                st.markdown(f"  {url}")
            else:
                st.warning(
                    "A source URL is missing or invalid; "
                    "its authenticity has not been established."
                )
    else:
        st.warning(
            "No sources were returned. Treat factual requirements "
            "as unverified."
        )

    st.info(
        "This tool provides planning assistance, not legal, accounting, "
        "regulatory, or investment advice. Confirm important requirements "
        "with the responsible official authority before acting."
    )

st.markdown("---")
st.caption(
    "Verification note: the interface displays sources returned by the "
    "workflow. Their presence alone does not prove that claims were "
    "independently verified. Unverified facts must be clearly identified."
)
