# Decodo tools for CrewAI

![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-green)
![License](https://img.shields.io/badge/license-MIT-blue)

[CrewAI](https://www.crewai.com) tools for the [Decodo](https://decodo.com) Web Scraping API. Give your agents live web pages and search results.

| Tool | What it does |
| --- | --- |
| `DecodoWebScraperTool` | Scrapes any public URL and returns the page as Markdown. |
| `DecodoSearchTool` | Searches Google or Amazon and returns the parsed results as JSON. |
| `DecodoEcommerceTool` | Gets product details or search results from Amazon, Walmart or Target as JSON. |
| `DecodoSERPTool` | Gets Google or Bing results pages, with paging, or a Google AI Mode answer as JSON. |

## Requirements

- Python 3.12 or 3.13
- A Decodo Web Scraping API key

## Installation

```bash
pip install decodo-crewai
```

## Credentials

Copy your API key from your Web Scraping API subscription on the [Decodo dashboard](https://dashboard.decodo.com/web-data/playground) and set it as an environment variable:

```bash
export DECODO_API_KEY="<api_key>"
```

Or pass it to each tool:

```python
DecodoWebScraperTool(api_key="<api_key>")
```

## Usage

```python
from crewai import Agent, Crew, Task

from decodo_crewai import DecodoSearchTool, DecodoWebScraperTool

researcher = Agent(
    role="Researcher",
    goal="Find and summarize up-to-date information from the web",
    backstory="You search the web, read the most relevant pages and report what they say.",
    tools=[DecodoSearchTool(), DecodoWebScraperTool()],
)

task = Task(
    description="Find the three most recent announcements about {topic} and summarize each one.",
    expected_output="Three bullet points, each with a one-sentence summary and the source URL.",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[task])
print(crew.kickoff(inputs={"topic": "solid-state batteries"}))
```

The tools can also be called directly:

```python
from decodo_crewai import DecodoSearchTool, DecodoWebScraperTool

print(DecodoWebScraperTool().run(url="https://ip.decodo.com"))
print(DecodoSearchTool().run(query="mechanical keyboard", source="amazon"))
```

For a complete multi-agent example, see the [research crew](examples/research_crew): a researcher, an analyst and a writer that turn any topic into a cited report.

## Tools

### DecodoWebScraperTool

Arguments the agent fills in:

| Argument | Type | Description |
| --- | --- | --- |
| `url` | `str` | Full URL of the page to scrape. |
| `geo` | `str`, optional | Country to send the request from, e.g. `United States`. |
| `js_render` | `bool`, optional | Open the page in a headless browser. Only needed for pages that load content with JavaScript. |

Constructor options:

| Option | Default | Description |
| --- | --- | --- |
| `api_key` | `DECODO_API_KEY` | Decodo Web Scraping API key. |
| `max_chars` | `45000` | Markdown longer than this is truncated to keep the page within the agent's context. |

### DecodoSearchTool

Arguments the agent fills in:

| Argument | Type | Description |
| --- | --- | --- |
| `query` | `str` | Search query. |
| `source` | `"google"` or `"amazon"`, optional | `google` (default) for web results, `amazon` for product listings. |
| `geo` | `str`, optional | Google: a country name, e.g. `United States`. Amazon: a US ZIP code, e.g. `10001`, or a two-letter country code for delivery outside the US, e.g. `DE`. |

### DecodoEcommerceTool

Arguments the agent fills in. Pass either `product_id` or `query`:

| Argument | Type | Description |
| --- | --- | --- |
| `store` | `"amazon"`, `"walmart"` or `"target"` | Store to look up. |
| `product_id` | `str`, optional | One product's details. Amazon: the ASIN, e.g. `B09H74FXNW`. Walmart or Target: the product ID from the product URL. |
| `query` | `str`, optional | Search the store's products instead. |
| `zip_code` | `str`, optional | US ZIP code for prices and availability at that delivery location, e.g. `10001`. |

### DecodoSERPTool

Arguments the agent fills in:

| Argument | Type | Description |
| --- | --- | --- |
| `query` | `str` | Search query. |
| `engine` | `"google"`, `"bing"` or `"google_ai_mode"`, optional | `google` (default) or `bing` for a results page; `google_ai_mode` for Google's AI-written answer and the sources it cites. |
| `page` | `int`, optional | Results page to fetch, starting at 1. Ignored by `google_ai_mode`. |
| `geo` | `str`, optional | Country to search from, e.g. `United States`. |

Bing results are rendered in a headless browser and can take over a minute.

## Errors

When a request fails, for example because of an invalid API key, a rate limit or a page that returns `404`, the tools return a CrewAI `ToolFailure` instead of raising. The agent sees what went wrong and can retry or change course, and CrewAI records the failure according to the agent's `tool_failure_policy`.

## License

MIT
