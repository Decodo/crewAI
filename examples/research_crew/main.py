"""Multi-agent research crew powered by Decodo.

A researcher finds sources with Google search, an analyst reads them, and a writer turns the notes
into a cited Markdown report, saved to report.md.

    python main.py "your research topic"
"""

from __future__ import annotations

import sys

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

from decodo_crewai import DecodoSearchTool, DecodoWebScraperTool

load_dotenv()

DEFAULT_TOPIC = "the state of solid-state batteries for electric cars"


def build_crew() -> Crew:
    researcher = Agent(
        role="Web researcher",
        goal="Find the most relevant, credible and recent sources about {topic}",
        backstory=(
            "You are an experienced researcher. You search the web, skip ads and low-quality pages, "
            "and pick sources that a careful reader would trust."
        ),
        tools=[DecodoSearchTool()],
    )
    analyst = Agent(
        role="Research analyst",
        goal="Read the selected sources and extract the key facts about {topic}",
        backstory=(
            "You read primary sources closely and write down only what they actually say, "
            "with figures and dates where they exist."
        ),
        # Five full pages at once would crowd the context; 15k characters keeps the substance of most articles.
        tools=[DecodoWebScraperTool(max_chars=15_000)],
    )
    writer = Agent(
        role="Report writer",
        goal="Write a clear, well-sourced report about {topic}",
        backstory="You turn research notes into short reports that busy readers can trust and act on.",
    )

    find_sources = Task(
        description=(
            "Search Google for {topic}. From the results, pick the 5 most relevant and credible pages. "
            "Prefer original sources and recent articles over listicles and ads."
        ),
        expected_output="A numbered list of 5 sources, each with its title, URL and one line on why it is relevant.",
        agent=researcher,
    )
    analyze_sources = Task(
        description=(
            "Read each source from the researcher's list with the web scraper and extract the key facts, "
            "figures and claims about {topic}. If a page fails to load, note it and move on."
        ),
        expected_output=(
            "One entry per source, numbered [1], [2] and so on in the researcher's order: the title and URL, "
            "then 3 to 6 bullet points of key facts, or 'failed to load'."
        ),
        agent=analyst,
        context=[find_sources],
    )
    write_report = Task(
        description=(
            "Write a report on {topic} using only the analyst's notes. "
            "Cite facts inline with the analyst's source numbers, e.g. [2]. "
            "End with a Sources list that has every number you cited, with its title and URL, and nothing else."
        ),
        expected_output=(
            "A Markdown report with a title, a 2 to 3 sentence summary, 3 to 5 short sections "
            "and a numbered Sources list with URLs."
        ),
        agent=writer,
        context=[analyze_sources],
        output_file="report.md",
    )

    return Crew(
        agents=[researcher, analyst, writer],
        tasks=[find_sources, analyze_sources, write_report],
        process=Process.sequential,
        verbose=True,
    )


def main() -> None:
    topic = " ".join(sys.argv[1:]) or DEFAULT_TOPIC
    result = build_crew().kickoff(inputs={"topic": topic})
    print(result.raw)


if __name__ == "__main__":
    main()
