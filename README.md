# Morning Briefing Agent

A personal AI agent that generates a prioritized daily briefing by combining my live Google Calendar with a task list, using the Claude API to reason about what to do and in what order.

## What it does

- Pulls today's fixed commitments live from Google Calendar (OAuth 2.0, read-only).
- Reads a task list with deadlines and context from a local file.
- Sends both to the Claude API with an engineered prompt that:
  - Prioritizes tasks using the Eisenhower matrix (urgency + importance).
  - Respects fixed calendar blocks (never schedules work during class, work, or sleep).
  - Avoids overloading the day and flags what to defer.
  - Gives a one-line reason for each placement.
- Runs automatically every morning via a scheduled job (cron) and saves the briefing to a dated file.

## Tech

- Python
- Claude API (Anthropic) — prompt engineering, agentic task reasoning
- Google Calendar API (OAuth 2.0)
- cron (scheduled daily execution)

## How it works

1. `agent.py` authenticates with Google, fetches today's events, reads `tasks.txt`, and calls Claude to produce the briefing.
2. `run_briefing.sh` sets up the environment and runs the agent, saving output to `briefing_<date>.txt`.
3. A cron job triggers the wrapper each morning.

## Setup

Requires a Google Cloud OAuth client (`credentials.json`) and an Anthropic API key. Secrets are excluded from version control via `.gitignore`.

## Status

Built and in personal daily use. Roadmap: replace the local task file with a Notion integration (Phase 3), and add Gmail as a task source (Phase 4).

## Author

Matin Meraj — BSc Data Science, Simon Fraser University
