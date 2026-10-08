
import streamlit as st
from core.validators import validate_inputs

st.set_page_config(page_title="Business Launch Advisor", page_icon="🚀", layout="wide")

st.title("🚀 Business Launch Advisor")
st.write(
    "A source-grounded multi-agent business planning app for people who want to start "
    "a small or large business."
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

    run = st.button("Create verified startup plan", type="primary", use_container_width=True)

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

    errors = validate_inputs(inputs)
    if errors:
        for error in errors:
            st.error(error)
        st.stop()

    with st.status("Researching official sources and building your plan...", expanded=True) as status:
        try:
            result = run_consulting_crew(inputs)
            status.update(label="Plan completed", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="The plan could not be completed", state="error", expanded=True)
            st.error(str(exc))
            st.stop()

    st.success("Your startup plan is ready.")

    st.markdown("## Your business launch plan")
    st.markdown(result["report"])

    st.markdown("## Verified sources used")
    if result["sources"]:
        for source in result["sources"]:
            st.markdown(
                f"- **{source['title']}** — {source['domain']}  \n"
                f"  {source['url']}"
            )
    else:
        st.warning("No approved official source was retrieved. Treat factual requirements as unverified.")

    st.info(
        "Important: this is a planning assistant, not a lawyer, accountant, regulator, "
        "or investment adviser. Requirements can change. Before spending money or registering "
        "a business, confirm the cited requirement with the responsible authority."
    )

st.markdown("---")
st.caption(
    "Anti-hallucination design: factual requirements are restricted to approved official/public "
    "sources. If a fact cannot be verified, the report must say 'Not verified'."
)
