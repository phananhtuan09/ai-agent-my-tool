"""Live source adapters for the Crypto Airdrop agent."""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os
import re

from backend.agents.crypto_airdrop.fixtures import get_fixture_airdrops
from backend.agents.crypto_airdrop.models import AirdropRecord
from backend.exceptions import CrawlError


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)


def fetch_source_airdrops(source_name: str) -> tuple[list[AirdropRecord], str | None]:
    """Fetch one source with deterministic fixtures by default."""

    fallback = get_fixture_airdrops(source_name)
    if os.environ.get("AI_AGENT_TOOL_ENABLE_LIVE_AIRDROP_FETCH") != "1":
        if fallback:
            return fallback, None
        raise CrawlError(f"No airdrop fixture is configured for source '{source_name}'.")

    loaders = {
        "airdrops_io": _load_airdrops_io,
        "cryptorank": _load_cryptorank,
        "defillama": _load_defillama,
    }
    try:
        return loaders[source_name](), None
    except CrawlError as exc:
        if fallback:
            return fallback, f"{source_name} live crawl degraded; fallback snapshot used: {exc}"
        raise


def _load_airdrops_io() -> list[AirdropRecord]:
    html = _fetch_html("https://airdrops.io/")
    pattern = re.compile(
        r'<article[^>]+?project type-project[^>]+?data-published="(?P<published>\d+)"[^>]*>'
        r'.*?location.href=\'(?P<url>https://airdrops\.io/[^/\']+/?)\''
        r'.*?<h3>(?P<title>[^<]+)</h3>'
        r'.*?Actions:\s*<span>(?P<actions>[^<]+)</span>',
        re.DOTALL,
    )
    records: list[AirdropRecord] = []
    for match in pattern.finditer(html):
        title = _clean_text(match.group("title"))
        actions = _clean_text(match.group("actions"))
        url = match.group("url")
        published = match.group("published")
        record = AirdropRecord(
            name=title,
            chain=_infer_chain(" ".join([title, actions, url])),
            requirements_summary=actions,
            source="airdrops_io",
            source_url=url,
            deadline=_format_compact_date(published),
            team_signal=_signal_from_keywords(title, actions, strong={"ai", "bridge", "defi"}),
            tokenomics_signal=_signal_from_keywords(title, actions, strong={"points", "season", "campaign"}),
            community_signal=_signal_from_keywords(title, actions, strong={"quest", "social", "community"}),
            task_reward_signal=_task_reward_signal(actions),
        )
        records.append(_enrich_airdrops_io_record(record))
        if len(records) == 8:
            break
    if not records:
        raise CrawlError("airdrops_io live crawl returned no parseable rows.")
    return records


def _load_cryptorank() -> list[AirdropRecord]:
    html = _fetch_html("https://cryptorank.io/drophunting")
    marker = '__NEXT_DATA__" type="application/json">'
    start = html.find(marker)
    if start == -1:
        raise CrawlError("cryptorank page did not expose __NEXT_DATA__.")
    start = html.find(">", start) + 1
    end = html.find("</script>", start)
    payload = json.loads(html[start:end])
    items = payload["props"]["pageProps"]["fallbackTableData"]["data"]

    records: list[AirdropRecord] = []
    for item in items[:12]:
        coin = item["coin"]
        activity_types = item.get("activityTypes") or []
        reward_type = item.get("rewardType") or "unknown reward"
        activity_points = item.get("activityPoints") or "No activity points listed"
        time_cost = item.get("time") or "Unknown time cost"
        cost = item.get("cost") or "Unknown cost"
        summary = (
            f"Reward type: {reward_type}. Activity: {activity_points}. "
            f"Tasks: {', '.join(activity_types) if activity_types else 'general activity'}. "
            f"Time cost: {time_cost}. Cost: {cost}."
        )
        project_key = item.get("key") or coin["key"]
        records.append(
            _enrich_cryptorank_record(
                AirdropRecord(
                name=_clean_text(coin["name"]),
                chain=_infer_chain(" ".join([coin["name"], project_key])),
                requirements_summary=summary,
                source="cryptorank",
                source_url=f"https://cryptorank.io/drophunting/{project_key}",
                deadline=item.get("statusUpdatedAt"),
                team_signal=_fund_signal(coin.get("funds") or []),
                tokenomics_signal="high" if item.get("rewardType") else "medium",
                community_signal=_twitter_signal(coin.get("twitterScore")),
                task_reward_signal=_task_reward_signal(summary),
                )
            )
        )
    if not records:
        raise CrawlError("cryptorank live crawl returned no parseable rows.")
    return records


def _load_defillama() -> list[AirdropRecord]:
    try:
        html = _fetch_html(
            "https://defillama.com/airdrops",
            headers={
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
            },
        )
    except CrawlError as exc:
        raise CrawlError(f"defillama blocked live fetch ({exc})") from exc

    parser = _TitleListParser()
    parser.feed(html)
    titles = [title for title in parser.items if title and "protocol" not in title.lower()]
    if not titles:
        raise CrawlError("defillama live crawl returned no parseable rows.")

    records: list[AirdropRecord] = []
    for title in titles[:8]:
        records.append(
            AirdropRecord(
                name=title,
                chain=_infer_chain(title),
                requirements_summary="Tokenless protocol detected from DeFiLlama airdrop watchlist.",
                source="defillama",
                source_url="https://defillama.com/airdrops",
                deadline=None,
                team_signal="medium",
                tokenomics_signal="medium",
                community_signal="medium",
                task_reward_signal="medium",
            )
        )
    return records


def _fetch_html(url: str, headers: dict[str, str] | None = None) -> str:
    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", errors="ignore")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise CrawlError(str(exc)) from exc


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _format_compact_date(value: str) -> str | None:
    if len(value) < 8:
        return None
    return f"{value[:4]}-{value[4:6]}-{value[6:8]}"


def _infer_chain(text: str) -> str:
    normalized = text.lower()
    mapping = {
        "ethereum": "Ethereum",
        "solana": "Solana",
        "arbitrum": "Arbitrum",
        "base": "Base",
        "optimism": "Optimism",
        "cosmos": "Cosmos",
        "bitcoin": "Bitcoin",
        "bnb": "BNB Chain",
    }
    for token, chain in mapping.items():
        if token in normalized:
            return chain
    return "Multi-chain"


def _signal_from_keywords(title: str, summary: str, strong: set[str]) -> str:
    normalized = f"{title} {summary}".lower()
    if any(keyword in normalized for keyword in strong):
        return "high"
    if any(keyword in normalized for keyword in {"task", "point", "social", "activity"}):
        return "medium"
    return "low"


def _fund_signal(funds: list[dict[str, object]]) -> str:
    if any(int(fund.get("tier") or 0) == 1 for fund in funds):
        return "high"
    if funds:
        return "medium"
    return "low"


def _twitter_signal(score: object) -> str:
    try:
        value = float(score)
    except (TypeError, ValueError):
        return "medium"
    if value >= 70:
        return "high"
    if value >= 35:
        return "medium"
    return "low"


def _task_reward_signal(summary: str) -> str:
    normalized = summary.lower()
    if any(token in normalized for token in {"weekly", "four epochs", "maintain", "stake"}):
        return "medium"
    if any(token in normalized for token in {"social", "quest", "points", "mission"}):
        return "high"
    return "low"


class _TitleListParser(HTMLParser):
    """Collect title text from the first level of heading tags."""

    def __init__(self) -> None:
        super().__init__()
        self.current_tag: str | None = None
        self.current_text: list[str] = []
        self.items: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"h1", "h2", "h3", "h4"}:
            self.current_tag = tag
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_tag is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self.current_tag:
            text = _clean_text("".join(self.current_text))
            if text:
                self.items.append(text)
            self.current_tag = None
            self.current_text = []


def _enrich_airdrops_io_record(record: AirdropRecord) -> AirdropRecord:
    html = _fetch_html(record.source_url)
    published_match = re.search(
        r'article:published_time" content="([^"]+)"',
        html,
    )
    details_match = re.search(
        r"<h2[^>]*>.*?Airdrop Details</h2>(.*?)<h2",
        html,
        re.DOTALL,
    )
    description_match = re.search(
        r'<meta name="description" content="([^"]+)"',
        html,
    )

    details = _extract_text(details_match.group(1)) if details_match else ""
    description = _clean_text(description_match.group(1)) if description_match else ""
    enriched_text = " ".join([record.name, description, details])

    if details:
        first_sentence = details.split(". ", maxsplit=1)[0].strip()
        record.requirements_summary = (
            first_sentence if len(first_sentence) > 30 else record.requirements_summary
        )
        record.task_reward_signal = _task_reward_signal(details)
        record.team_signal = _signal_from_keywords(
            record.name,
            details,
            strong={"leaderboard", "portal", "mainnet", "testnet"},
        )
        record.community_signal = _signal_from_keywords(
            record.name,
            details,
            strong={"community", "social", "quest", "leaderboard"},
        )

    record.chain = _infer_chain(enriched_text)
    if published_match:
        record.deadline = published_match.group(1)[:10]
    return record


def _enrich_cryptorank_record(record: AirdropRecord) -> AirdropRecord:
    html = _fetch_html(record.source_url)
    marker = '__NEXT_DATA__" type="application/json">'
    start = html.find(marker)
    if start == -1:
        return record
    start = html.find(">", start) + 1
    end = html.find("</script>", start)
    page = json.loads(html[start:end])["props"]["pageProps"]
    coin = page.get("coin") or {}
    activity = page.get("drophuntingActivity") or {}
    tasks = activity.get("tasks") or []

    task_titles = [_clean_text(task.get("title") or "") for task in tasks if task.get("title")]
    blockchains = []
    for task in tasks:
        for chain in task.get("blockchains") or []:
            name = chain.get("name")
            if name:
                blockchains.append(_clean_text(str(name)))

    ecosystems = [
        _clean_text(ecosystem.get("name") or "")
        for ecosystem in coin.get("ecosystems") or []
        if ecosystem.get("name")
    ]
    descriptions = [
        _extract_text(task.get("description") or "")
        for task in tasks[:3]
        if task.get("description")
    ]

    summary_parts = []
    if task_titles:
        summary_parts.append(f"Tasks: {', '.join(task_titles[:4])}.")
    if descriptions:
        summary_parts.append(descriptions[0].split(". ", maxsplit=1)[0].strip() + ".")
    record.requirements_summary = " ".join(part for part in summary_parts if part) or record.requirements_summary

    enriched_text = " ".join(
        [
            record.name,
            coin.get("category") or "",
            coin.get("description") or "",
            " ".join(blockchains),
            " ".join(ecosystems),
        ]
    )
    record.chain = _infer_chain(enriched_text)
    if blockchains:
        record.chain = blockchains[0]
    elif ecosystems:
        record.chain = ecosystems[0].replace(" Ecosystem", "")

    if activity.get("distributeDate") and str(activity.get("distributeDate"))[:10] != "None":
        record.deadline = str(activity["distributeDate"])[:10]
    else:
        for task in tasks:
            end_date = task.get("endDate") or task.get("startDate")
            if end_date:
                record.deadline = str(end_date)[:10]
                break

    record.tokenomics_signal = _signal_from_keywords(
        record.name,
        f"{coin.get('category') or ''} {record.requirements_summary}",
        strong={"defi", "dex", "bridge", "lending", "restaking"},
    )
    record.task_reward_signal = _task_reward_signal(record.requirements_summary)
    return record


def _extract_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return _clean_text(without_tags)
