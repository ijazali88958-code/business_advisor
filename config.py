
import os

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_RETRIES = 3
BACKOFF_SECONDS = 2
SEARCH_RESULTS_PER_QUERY = 5
REQUEST_TIMEOUT = 15

# Only these domains are accepted as evidence.
# Add countries gradually rather than accepting arbitrary websites.
COUNTRY_SOURCES = {
    "pakistan": [
        "gov.pk",
        "fbr.gov.pk",
        "secp.gov.pk",
        "smeda.org.pk",
        "pbs.gov.pk",
        "sbp.org.pk",
        "punjab.gov.pk",
        "sindh.gov.pk",
        "kp.gov.pk",
        "balochistan.gov.pk",
    ],
    "india": [
        "gov.in",
        "mca.gov.in",
        "gst.gov.in",
        "msme.gov.in",
        "startupindia.gov.in",
        "dpiit.gov.in",
        "mospi.gov.in",
    ],
    "united states": [
        "sba.gov",
        "irs.gov",
        "usa.gov",
        "sec.gov",
        "census.gov",
    ],
    "united kingdom": [
        "gov.uk",
        "companieshouse.gov.uk",
        "ons.gov.uk",
    ],
    "canada": [
        "canada.ca",
        "statcan.gc.ca",
        "ised-isde.canada.ca",
    ],
    "australia": [
        "business.gov.au",
        "ato.gov.au",
        "asic.gov.au",
        "abs.gov.au",
    ],
    "united arab emirates": [
        "u.ae",
        "moec.gov.ae",
        "economy.gov.ae",
        "tax.gov.ae",
        "fta.gov.ae",
    ],
    "saudi arabia": [
        "gov.sa",
        "mc.gov.sa",
        "zatca.gov.sa",
        "monshaat.gov.sa",
        "stats.gov.sa",
    ],
    "new zealand": [
        "business.govt.nz",
        "companiesoffice.govt.nz",
        "ird.govt.nz",
        "stats.govt.nz",
    ],
}

GLOBAL_PUBLIC_SOURCES = [
    "worldbank.org",
    "ilo.org",
    "unctad.org",
]

def approved_domains(country: str) -> list[str]:
    key = country.strip().lower()
    return list(dict.fromkeys(COUNTRY_SOURCES.get(key, []) + GLOBAL_PUBLIC_SOURCES))
