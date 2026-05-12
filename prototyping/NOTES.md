
# README
If you have no experience with Claude Code
* [5 Fun Projects Using Claude Code](https://www.kdnuggets.com/5-fun-projects-using-claude-code)

----

## `proto1` - CRUD for SQLite

SQLite-backed volunteer task manager for Makersmiths Shop Sergeant.
CLI tools in `scripts/` that an AI agent calls to read, update, delete, list, and purge task records.

### What Was Built

* **Schema-driven table loading** (`create_db_schema.py` + `db_table_create.py`): any hierarchical YAML → schema YAML → SQLite table. `create_db_schema.py` does DFS to discover the array-key chain from `--root` to `--leaf`, infers SQLite types, and unions fields across ALL records at every level (both leaf and intermediate). `db_table_create.py` traverses the hierarchy using `root_promote` + `levels[].promote` to seed a context dict, then merges context + leaf record for each row.
* **Schema-agnostic field validation** (`db_list`, `db_purge`, `db_update`): field names are validated against the live SQLite schema via `PRAGMA table_info` instead of a hardcoded `TASK_FIELDS` list. Works with any schema-generated table.
* **`db_utils.py` helpers**: `get_table_columns(conn, table) -> dict[str, str]` (PRAGMA introspection) and `coerce_for_type(field, raw, sql_type) -> Any` (schema-agnostic CLI coercion: INTEGER accepts bool-like or numeric strings, REAL→float, TEXT passthrough).

### Key Conventions

* All scripts use named CLI args (`--db_path`, `--yaml_data`, `--yaml_schema`, `--table`, etc.) — no positional args.
* `msl-schema.yaml` (proto1 root) is the hand-edited schema for `MSL-volunteer-opportunities.yaml`; raw `create_db_schema.py` output has conflicting `name` columns that must be renamed.
* `NA` string → SQL `NULL`. `supervision` stored as `0`/`1`. `uuid` is the canonical primary key; `task_id` is not enforced unique.
* 57 tests across 8 test files; run with `uv run pytest ./tests/ -v` from `proto1/`.

----

# protoX - Learn Claude Code & AI Agents
* [5 Fun Projects Using Claude Code](https://www.kdnuggets.com/5-fun-projects-using-claude-code)

1. [Claude Code for Beginners — Build Your First App with AI (No Coding Required!)](https://www.youtube.com/watch?v=s-Mc26Ytz10)
1. [Claude Code: Build Your First AI Agent](https://www.youtube.com/watch?v=gHB4JFG9i3k)
1. [Generate Images and Videos Inside Claude (Higgsfield MCP Setup)](https://www.youtube.com/watch?v=Wgs8MS86Dc0)
1. [Claude Skills: Build Your First AI Assistant (Never Repeat Prompts Again)](https://www.youtube.com/watch?v=mS5ojqQ7zzw)
1. [Claude Cowork for Beginners - Complete Step-by-Step Tutorial](https://www.youtube.com/watch?v=vv09DHej6gg)

----

## `proto2` - Build a Chatbot With Python
The Python ChatterBot library lets you build a self-learning command-line chatbot with just a few lines of code.
The objective is to learn the basic of interactive chatbot using Python’s ChatterBot.
Starting with an untrained chatbot and them move onto learn how you can train such a chatbot.

* [ChatterBot: Build a Chatbot With Python](https://realpython.com/build-a-chatbot-python-chatterbot/)
* [Building a Chatbot using Chatterbot in Python](https://www.datacamp.com/tutorial/building-a-chatbot-using-chatterbot)
* [AI Coding Agents Guide: A Map of the Four Workflow Types](https://realpython.com/ai-coding-agents-guide/)

----

## `proto3` - Slack Integration
What does the command `/install-slack-app` in Claude Code do?
It's a simple convenience command.
`/install-slack-app` opens the Slack Marketplace page for the Claude app in your browser,
making it easy to install Claude in your Slack workspace.
It takes no arguments, and internally it increments a `slackAppInstallCount` counter in your global config to track usage.

That's it — it's essentially a browser shortcut, not a configuration command.
If you want the actual Slack integration for routing coding tasks,
the relevant command is `/plugin` install slack (or `claude plugin install slack` from the shell),
which sets up the Slack MCP server.

* [How to Set Up Claude Code Channels Locally](https://www.kdnuggets.com/how-to-set-up-claude-code-channels-locally)

### Slack Integration
The Claude Code command `/install-slack-app` does substantially more.
It installs and configures the Slack MCP server for Claude Code.
Once the plugin loads, the Slack MCP server is automatically configured
and you're prompted to authenticate into your Slack workspace via OAuth.

Under the hood, it writes an MCP configuration to `.mcp.json` pointing at `https://mcp.slack.com/mcp` with OAuth credentials.
The practical result, per Slack's own docs:
it lets you connect to Slack for search, messaging, and document access.
It gives Claude Code context from your Slack workspace or the ability to post updates.
Think of it like mounting a network drive:
after running it, Claude Code gains Slack as a readable/writable data source within your session,
rather than just opening a browser page.

----

# protoX - Claude and n8n

* [Claude Code vs n8n? Wrong Question](https://www.youtube.com/watch?v=R8kSHT-JWSc)

----

# protoX - Build LLM From Scratch
A hands-on workshop where you write every piece of a GPT training pipeline yourself, understanding what each component does and why.

* [An LLM From “Scratch”](https://hackaday.com/2026/05/07/an-llm-from-scratch/)
* [Train Your Own LLM From Scratch](https://github.com/angelos-p/llm-from-scratch/tree/main)
* [An Animated Walkthrough Of How Large Language Models Work](https://hackaday.com/2024/11/20/an-animated-walkthrough-of-how-large-language-models-work/)
* [Learn AI Via Spreadsheet](https://hackaday.com/2024/03/18/learn-ai-via-spreadsheet/)

----

# protoX - Build Vector Search From Scratch
* [How to Build Vector Search From Scratch in Python](https://www.kdnuggets.com/how-to-build-vector-search-from-scratch-in-python)

----

# protoX - Build and Tryout HolyClaude
Full AI development workstation. Claude Code, web UI, headless browser, 7 AI CLIs, 50+ dev tools — containerized and ready.

* [HolyClaude](https://holyclaude.coderluii.dev/)
* [HolyCode](https://holycode.coderluii.dev/)

----

# protoX - Using Claude API
I asked Claude the following:
I have several videos that discuss the relationship between physics & machine learning.
I would like to extract all the information from these videos and summarize it as text.
How can Claude help me do this?

After some questioning, Claude recommend to write a script to automate the processing of the videos
using the Claude API.

There are 27 YouTube videos and they range in length of 8 to 18 minutes (average about 10 minutes)

## Automated Python Pipeline
Claude recommended this assembly line
— each video goes in one end, structured notes come out the other.
The stages are:

1. **Transcript extraction —** `youtube-transcript-api` pulls the auto-generated (or manual) captions from each YouTube URL.
   No audio processing needed, it's fast and free.
1. **Summarization via Claude API —** feed each transcript to Claude (`claude-sonnet-4-20250514`)
   with a prompt tailored for physics/ML content (key concepts, equations mentioned, relationships drawn).
   You'd get per-video structured notes + a final combined summary.
1. **Output —** write everything to markdown or a single PDF/DOCX.

What you'd need:

* `pip install youtube-transcript-api` anthropic
* An Anthropic API key (if you don't already have one via claude.ai, you'd need console.anthropic.com)
* A text file with your 27 YouTube URLs

>**NOTE:** API usage through the Claude Console (`console.anthropic.com`) requires separate setup and payment.
>You'll be billed per token at console.anthropic.com, independent of your Pro subscription.

```python
#!/usr/bin/env python3
"""
Physics & ML YouTube Video Summarization Pipeline
--------------------------------------------------
Extracts transcripts from YouTube videos and uses Claude to generate
per-video structured notes plus a combined synthesis.

Usage:
    python summarize_videos.py --urls urls.txt --output summaries/
    python summarize_videos.py --urls urls.txt --output summaries/ --combined combined.md
"""

import argparse
import os
import sys
import time
from pathlib import Path

import anthropic
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


# ── Config ────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048

PER_VIDEO_SYSTEM = """You are an expert in both physics and machine learning.
Your job is to extract and organize all substantive information from a video transcript.
Be thorough — don't skip equations, named concepts, or specific claims."""

PER_VIDEO_PROMPT = """Below is a transcript from a video about physics and machine learning.
Extract and organize all information into the following structured format:

## Summary
2–4 sentence overview of the video's main argument or topic.

## Key Concepts
Bullet list of every distinct concept introduced (physics or ML). One line each.

## Physics ↔ ML Connections
Explicit analogies or mappings drawn between physics and ML in this video.

## Equations & Formalisms
Any equations, loss functions, Hamiltonians, or mathematical structures mentioned (use LaTeX notation).

## Key Claims & Insights
Notable claims, surprising results, or actionable insights. Be specific.

## References & Names
People, papers, or tools mentioned.

---
TRANSCRIPT:
{transcript}
"""

COMBINED_SYSTEM = """You are an expert synthesizer of technical content in physics and machine learning.
Given summaries from multiple videos in a series, identify overarching themes and build a unified knowledge base."""

COMBINED_PROMPT = """Below are structured summaries from {n} videos about the relationship between physics and machine learning.

Synthesize them into:

## Overview
What is the central thesis or research agenda across all videos?

## Master Concept Map
All key concepts across all videos, grouped thematically (e.g., statistical mechanics, symmetry, optimization, etc.).

## Core Physics ↔ ML Connections
The most important and recurring mappings/analogies drawn across the series.

## Unified Equations & Formalisms
Collect all equations and mathematical structures, deduplicated and organized by topic.

## Key Takeaways
The 10 most important insights from the series as a whole.

## Open Questions & Research Frontiers
Any open problems or future directions mentioned across videos.

---
VIDEO SUMMARIES:
{summaries}
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    import re
    patterns = [
        r"(?:v=|youtu\.be/|/embed/|/v/|/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def get_transcript(video_id: str) -> tuple[str, str]:
    """
    Fetch transcript for a video. Returns (transcript_text, language).
    Prefers manual captions, falls back to auto-generated.
    """
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try manual English first, then auto-generated
    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
    except NoTranscriptFound:
        transcript = transcript_list.find_generated_transcript(["en"])

    entries = transcript.fetch()
    text = " ".join(e["text"] for e in entries)
    return text, transcript.language


def summarize_video(client: anthropic.Anthropic, transcript: str, video_url: str, title: str = "") -> str:
    """Send transcript to Claude and get structured notes."""
    prompt = PER_VIDEO_PROMPT.format(transcript=transcript)
    header = f"# {title or video_url}\n\n" if title else f"# {video_url}\n\n"

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=PER_VIDEO_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return header + response.content[0].text


def synthesize(client: anthropic.Anthropic, summaries: list[str]) -> str:
    """Combine all per-video summaries into a master synthesis."""
    combined_text = "\n\n---\n\n".join(
        f"### Video {i+1}\n{s}" for i, s in enumerate(summaries)
    )
    prompt = COMBINED_PROMPT.format(n=len(summaries), summaries=combined_text)

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=COMBINED_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return "# Combined Synthesis: Physics & Machine Learning\n\n" + response.content[0].text


def load_urls(path: str) -> list[str]:
    """Load URLs from a text file (one per line, # comments ignored)."""
    lines = Path(path).read_text().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Summarize physics/ML YouTube videos with Claude.")
    parser.add_argument("--urls", required=True, help="Path to text file with YouTube URLs (one per line)")
    parser.add_argument("--output", required=True, help="Output directory for per-video summaries")
    parser.add_argument("--combined", default="combined_synthesis.md", help="Output path for combined summary (default: combined_synthesis.md)")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between API calls (default: 1.0)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip videos that already have a summary file")
    args = parser.parse_args()

    # Validate API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.Anthropic(api_key=api_key)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    urls = load_urls(args.urls)
    print(f"Loaded {len(urls)} URLs from {args.urls}\n")

    summaries = []
    failed = []

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")

        try:
            video_id = extract_video_id(url)
        except ValueError as e:
            print(f"  ✗ {e}")
            failed.append((url, str(e)))
            continue

        out_file = output_dir / f"video_{i:02d}_{video_id}.md"

        if args.skip_existing and out_file.exists():
            print(f"  ↷ Skipping (already exists): {out_file.name}")
            summaries.append(out_file.read_text())
            continue

        # 1. Fetch transcript
        try:
            transcript, lang = get_transcript(video_id)
            print(f"  ✓ Transcript fetched ({lang}, {len(transcript.split())} words)")
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"  ✗ No transcript available: {e}")
            failed.append((url, str(e)))
            continue
        except Exception as e:
            print(f"  ✗ Transcript error: {e}")
            failed.append((url, str(e)))
            continue

        # 2. Summarize with Claude
        try:
            summary = summarize_video(client, transcript, url)
            out_file.write_text(summary, encoding="utf-8")
            summaries.append(summary)
            print(f"  ✓ Summary saved → {out_file.name}")
        except Exception as e:
            print(f"  ✗ Claude API error: {e}")
            failed.append((url, str(e)))
            continue

        time.sleep(args.delay)

    # 3. Combined synthesis
    if summaries:
        print(f"\nGenerating combined synthesis from {len(summaries)} summaries...")
        try:
            synthesis = synthesize(client, summaries)
            combined_path = Path(args.combined)
            combined_path.write_text(synthesis, encoding="utf-8")
            print(f"✓ Combined synthesis saved → {combined_path}")
        except Exception as e:
            print(f"✗ Synthesis failed: {e}")
    else:
        print("\nNo summaries to synthesize.")

    # 4. Report
    print(f"\n{'='*50}")
    print(f"Done. {len(summaries)} succeeded, {len(failed)} failed.")
    if failed:
        print("\nFailed videos:")
        for url, reason in failed:
            print(f"  {url}\n    → {reason}")


if __name__ == "__main__":
    main()
```

----


