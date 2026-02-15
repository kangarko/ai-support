# AI Issue Support

Centralized AI-powered issue responder for kangarko's Minecraft plugins. When a GitHub issue is opened or commented on, the system analyzes the codebase and responds with actionable solutions — or proposes a draft PR fix.

## Supported Projects

ChatControl, Boss, CoreArena, Protect, Winter

## How It Works

Each public repo has a small calling workflow (`.github/workflows/ai-support.yml`) that delegates to the reusable workflow in this private repo. The flow:

1. **Gate** — Filters out bot comments. For follow-up comments, only responds if the bot already participated in the thread.
2. **Pre-analysis** — Extracts keywords, stacktrace classes, and mentioned files from the issue. Searches both the project and Foundation repos for relevant source files.
3. **Phase 1: Respond** — An AI agent reads skill files, config references, and relevant source code, then writes a response. If a code fix is possible, it proposes file changes.
4. **Phase 2: Self-review** — If code changes were proposed, a second AI pass reviews the diff for bugs, DRY violations, and correctness. Fixes problems before they reach the PR.
5. **Phase 3: Insights** — Extracts reusable knowledge from the resolution (e.g., non-obvious config behaviors, common mistakes) and stores it for future issues.
6. **Output** — Posts a comment on the issue. If code changes were made, creates a draft PR on the public repo. Commits any new insights back to this repo.

## Structure

```
config/          Project configs (layout, key files, purchase links, extra rules)
projects/        Per-project skill files with architecture, config keys, common issues
insights/        Learned insights (global + per-project), auto-updated by the responder
responder.py     Config-driven responder script (3-phase pipeline)
```

## Adding a New Project

1. Create `config/{project}.yml` following an existing config as template
2. Create `projects/{project}/skills/` with at least one `SKILL.md` (YAML frontmatter + Markdown)
3. Add the calling workflow to the public repo
4. Add `COPILOT_MCP_GITHUB_TOKEN` secret to the public repo
