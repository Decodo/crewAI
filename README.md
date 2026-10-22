# Decodo tools for CrewAI

![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-green)
![License](https://img.shields.io/badge/license-MIT-blue)

[CrewAI](https://www.crewai.com) tools for the [Decodo](https://decodo.com) Web Scraping API. Give your agents live web pages and search results.

| Tool | What it does |
| --- | --- |
| `DecodoWebScraperTool` | Scrapes any public URL and returns the page as Markdown. |
| `DecodoSearchTool` | Searches Google or Amazon and returns the parsed results as JSON. |

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
print(crew.kickoff(inputs={"topic": "web scraping APIs"}))
```

The tools can also be called directly:

```python
from decodo_crewai import DecodoSearchTool, DecodoWebScraperTool

print(DecodoWebScraperTool().run(url="https://ip.decodo.com"))
print(DecodoSearchTool().run(query="mechanical keyboard", source="amazon"))
```

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

## Errors

When a request fails, for example because of an invalid API key, a rate limit or a page that returns `404`, the tools return a CrewAI `ToolFailure` instead of raising. The agent sees what went wrong and can retry or change course, and CrewAI records the failure according to the agent's `tool_failure_policy`.

## License

MIT
