
from __future__ import annotations

from urllib.parse import quote, urlparse
import re
import requests
from bs4 import BeautifulSoup

from core.config import REQUEST_TIMEOUT, SEARCH_RESULTS_PER_QUERY, approved_domains


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BusinessLaunchAdvisor/1.0; "
        "+https://streamlit.io)"
    )
}


def _host(url: str) -> str:
    return urlparse(url).netloc.lower().split(":")[0].removeprefix("www.")


def _is_approved(url: str, domains: list[str]) -> bool:
    host = _host(url)
    return any(host == d or host.endswith("." + d) for d in domains)


def _search_duckduckgo(query: str) -> list[dict]:
    url = "https://html.duckduckgo.com/html/?q=" + quote(query)
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for item in soup.select(".result"):
        link = item.select_one(".result__a")
        snippet = item.select_one(".result__snippet")
        if not link:
            continue

        href = link.get("href", "")
        title = link.get_text(" ", strip=True)
        text = snippet.get_text(" ", strip=True) if snippet else ""
        if href.startswith("http"):
            results.append({"title": title, "url": href, "snippet": text})

        if len(results) >= SEARCH_RESULTS_PER_QUERY:
            break

    return results


def search_verified_sources(country: str, city: str, business_idea: str) -> list[dict]:
    domains = approved_domains(country)
    domain_query = " OR ".join(f"site:{d}" for d in domains[:8])

    queries = [
        f"{domain_query} business registration license requirements {country} {business_idea}",
        f"{domain_query} taxes business startup requirements {country} {business_idea}",
        f"{domain_query} small business permits licenses {city} {business_idea}",
        f"{domain_query} entrepreneurship small business statistics {country} {business_idea}",
    ]

    collected = []
    seen = set()

    for query in queries:
        try:
            results = _search_duckduckgo(query)
        except requests.RequestException:
            continue

        for result in results:
            if not _is_approved(result["url"], domains):
                continue

            normalized = result["url"].split("#")[0].rstrip("/")
            if normalized in seen:
                continue

            seen.add(normalized)
            result["domain"] = _host(result["url"])
            collected.append(result)

    return collected[:20]
