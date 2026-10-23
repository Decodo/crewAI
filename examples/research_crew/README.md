# Research crew

A three-agent [CrewAI](https://www.crewai.com) crew that researches any topic on the live web with Decodo and writes a cited report.

| Agent | Tool | Job |
| --- | --- | --- |
| Web researcher | `DecodoSearchTool` | Searches Google and picks the 5 most relevant sources. |
| Research analyst | `DecodoWebScraperTool` | Reads each source and extracts the key facts. |
| Report writer | none | Turns the notes into a Markdown report with citations. |

The agents run in sequence, each one working from the previous one's output. The final report is printed and saved to `report.md`.

## Setup

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set your keys in a `.env` file, in this folder or the repository root, or export them in your shell:

```bash
DECODO_API_KEY=<decodo_api_key>
OPENAI_API_KEY=<openai_api_key>
```

Get the Decodo API key from your Web Scraping API subscription on the [Decodo dashboard](https://dashboard.decodo.com/web-data/playground).

The crew uses CrewAI's default model, `gpt-4.1-mini`. To use another model, set `MODEL`, e.g. `MODEL=gpt-4.1`. Other providers need their CrewAI extra and key, e.g. `pip install "crewai[anthropic]"`, `ANTHROPIC_API_KEY` and `MODEL=anthropic/<model>`.

## Run

```bash
cd examples/research_crew
python main.py "heat pumps in cold climates"
```

Without a topic, it researches "the state of solid-state batteries for electric cars".

## Sample output

`python main.py` with the default topic and `gpt-4.1-mini` made 1 search and 5 page scrapes and wrote this report (October 2026):

<details>
<summary>report.md</summary>

# The State of Solid-State Batteries for Electric Cars

Solid-state batteries (SSBs) represent a promising evolution in electric vehicle (EV) energy storage technology, offering higher energy density, improved safety, and longer lifespan compared to conventional lithium-ion batteries. While significant technical progress has been made and multiple automakers target commercialization around 2027-2030, challenges in manufacturing scale-up and cost reduction mean widespread adoption remains several years away.

## Energy Density and Performance Advantages

SSBs replace the liquid electrolyte in lithium-ion batteries with a solid electrolyte, enabling theoretical energy densities exceeding 500 Wh/kg, compared to 250-300 Wh/kg typical of current lithium-ion batteries. This can translate into EV ranges of 600 to 750 miles and notably faster charging times, such as 10-minute fast charging targets set by Toyota and Samsung SDI for their all-solid-state battery (ASSB) development programs [1][2][4]. Safety is also improved due to the non-flammable nature of solid electrolytes and enhanced chemical stability [4][5].

## Industry Development and Timelines

Automakers and battery companies including Toyota, Samsung SDI, Volkswagen, QuantumScape, Honda, and Factorial Energy are actively developing various solid-state and semi-solid-state battery technologies. Semi-solid-state batteries, offering an intermediate step with improved energy density and reduced risk, have already been produced in limited forms—such as the Nio WELION 150-kWh pack with 260 Wh/kg in 2024 [2]. 

Full mass production of all-solid-state batteries is broadly expected to begin around 2027-2030, initially targeting premium and luxury vehicle segments. Toyota and Samsung SDI have pilot production lines aimed at 2027, while Honda plans demonstration production lines in 2024. Factorial Energy has demonstrated semi-solid-state packs with exceptional range [2][4][5]. However, industry insiders caution that large-scale commercial production may extend beyond 2030 to achieve cost-competitiveness and manufacturing reliability [1][3].

## Manufacturing and Cost Challenges

Despite promising performance, manufacturing SSBs at scale remains a major barrier. The production process requires advanced techniques to ensure dense, defect-free solid electrolyte and electrode interfaces, such as stamping and roll-pressing, which are still being refined [5]. Additional challenges include dendrite formation, raw material costs, and establishing consistent quality control [1][4].

Cost projections vary: optimistic scenarios predict $140 per kWh by 2028 with mass production, whereas pessimistic views suggest delays and prices near $175 per kWh around 2032-2033 [1]. These higher costs currently limit initial applications to premium vehicles, with broader market penetration likely delayed until mid-2030s [3].

## Market Impact and Outlook

While SSBs have the potential to revolutionize EV range, charging speed, and safety, incremental improvements in existing lithium-ion battery technologies—such as LFP cells with already-fast charging and 300-mile ranges—moderate the urgency to transition immediately [3]. The market outlook thus anticipates a gradual integration, with lithium-ion batteries evolving in parallel as SSB technology matures.

In summary, solid-state batteries are poised to become a critical technology milestone for EVs within this decade. Their successful commercialization depends on overcoming significant manufacturing and cost hurdles. Expected first adoption is in high-end vehicles by 2027-2030, followed by wider penetration in the 2030s.

---

## Sources

[1] Solid-state batteries, their future in the energy storage and electric vehicles market  
https://www.sciencedirect.com/science/article/pii/S2772569324000902

[2] We Keep Hearing About Solid-State Batteries. Here's What'll Actually Reach the Road.  
https://www.motortrend.com/features/solid-state-batteries-future-cars

[3] Will Solid-state batteries be the EV game changer when they start appearing in 2027/2028? (Reddit r/electricvehicles discussion)  
https://www.reddit.com/r/electricvehicles/comments/1vz26my/will_solidstate_batteries_be_the_ev_game_changer/

[4] Solid-State Battery News: Samsung & Toyota  
https://www.monolithai.com/blog/solid-state-battery-news

[5] All-solid-state battery technology (Honda official page)  
https://global.honda/en/tech/All-solid-state_battery_technology/

</details>
