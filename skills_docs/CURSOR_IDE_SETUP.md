# Cursor IDE setup — skills access modes

This guide explains how to configure Cursor for **skills-kg MCP only** or **filesystem skills only** when working in this repository.

The repository **defaults to MCP-only** (see committed workspace artefacts below). Switch modes deliberately — mixing both without understanding the layers causes duplicate or conflicting skill guidance.

## Project rules vs user-level Cursor settings

| Kind | Location | Scope |
| --- | --- | --- |
| **Project rules** | `.cursor/rules/*.mdc` (committed in this repo) | This workspace only — travels with the clone |
| **User Rules** | **Cursor → Settings → Rules** (or `Cursor Settings` user rules) | All projects on your machine |
| **Cursor Skills** | **Settings → Plugins → Rules, Skills, Subagents → Skills** (`~/.cursor/skills/`) | User-level; invoked when relevant or via `/` in chat |
| **MCP servers** | `~/.cursor/mcp.json` + **Tools & MCPs** | User-level server wiring (paths are local) |
| **Workspace settings** | `.vscode/settings.json` (gitignored here — set locally) | This workspace only |

Committed project rules for this repository:

| File | Purpose |
| --- | --- |
| `project-context.mdc` | Dual-mode purpose — portable library **and** Skills KG; do not delete portable artefacts |
| `skills-kg-mcp-only.mdc` | MCP-first skill discovery for Cursor sessions in this workspace |

Do **not** treat `project-context.mdc` or `skills-kg-mcp-only.mdc` as general user rules. Other repositories keep their own `.cursor/rules/` or none at all.

## How Cursor loads skills (three consumption layers)

| Layer | Where configured | What it does |
| --- | --- | --- |
| **1. Agent Skills locations** | `.vscode/settings.json` → `chat.agentSkillsLocations` | Injects `SKILL.md` files from configured folders into agent context |
| **2. Rules, Skills, Subagents** | **Cursor → Settings → Plugins → Rules, Skills, Subagents** | **User-level** skills from `~/.cursor/skills/` — separate from committed `.cursor/rules/` project rules |
| **3. MCP servers** | **Cursor → Settings → Plugins → Tools & MCPs** and `~/.cursor/mcp.json` | Exposes tools (`route_skill_query`, `get_skill`, …) from the read-only **skills-kg** server |

Safety baselines (`AGENTIC_CODING_GLOBAL_SAFETY.md`, `SECURE_AGENTIC_DEVELOPMENT.md`) are **repository files**, not skills. Agents should read them from the repo root in either mode.

---

## Mode A — skills-kg MCP only (repository default)

Use this when you want bounded retrieval, routing traces, usage metrics and a single governed skill boundary.

### Committed workspace artefacts

| File | Purpose |
| --- | --- |
| `.vscode/settings.json` | Repo `skills/` path disabled in `chat.agentSkillsLocations` (local; gitignored) |
| `.cursor/rules/project-context.mdc` | Project-only dual-mode context; not a user rule |
| `.cursor/rules/skills-kg-mcp-only.mdc` | MCP-only agent workflow; overrides filesystem-first text in `AGENTS.md` / `CLAUDE.md` in this workspace |

### Step 1 — Enable skills-kg MCP

**Cursor → Settings → Plugins → Tools & MCPs** → ensure **`skills-kg`** is **On** and connected.

Add to `~/.cursor/mcp.json` (replace paths):

```json
{
  "mcpServers": {
    "skills-kg": {
      "command": "/path/to/uv",
      "args": [
        "run", "--no-project",
        "--directory", "/path/to/coding-agent-skill-library",
        "--with-editable", "/path/to/coding-agent-skill-library",
        "python", "scripts/skills_mcp_server.py", "--sdk-stdio"
      ]
    }
  }
}
```

Smoke test:

```bash
python3 scripts/skills_mcp_server.py --list-tools
```

### Step 2 — Disable filesystem agent skills

Confirm `.vscode/settings.json` keeps the repo skills folder **disabled**:

```json
"chat.agentSkillsLocations": {
  "/path/to/coding-agent-skill-library/skills": false
}
```

Use your actual clone path (the committed file uses an absolute path for this workspace).

In **Cursor → Settings**, search **Agent Skills** and disable any extra locations you do not want (for example global `~/.cursor/skills` injection).

### Step 3 — Clean up Rules, Skills, Subagents

Open **Cursor → Settings → Plugins → Rules, Skills, Subagents → Skills** and adjust:

| Skill | Action | Reason |
| --- | --- | --- |
| **`discover-local-skills`** | **Remove** | Conflicts with MCP-only; scans `skills/` on disk |
| **`apply-laws-of-ai`** | **Remove** (optional) | Available via MCP (`get_skill` / `get_skill_execution_guide`) |
| **`github-workflow-best-practices`** | **Keep** (optional) | Not in skills-kg; only needed for GitHub Actions work |

### Step 4 — Disable unrelated MCP servers (optional)

For a strict **skills-kg-only** tool surface, turn off **`MCP_DOCKER`** and other MCP servers you do not need in **Tools & MCPs**.

### Step 5 — Confirm project rule is active

Ensure `.cursor/rules/skills-kg-mcp-only.mdc` exists with `alwaysApply: true`. Start a **new chat** after changing rules or MCP settings.

### Expected agent workflow (MCP)

1. Read safety files from repo root.
2. Load `apply-laws-of-ai` via MCP.
3. Call `route_skill_query` for ambiguous tasks.
4. Follow with route-specific tools: `resolve_skill`, `get_skill`, `recommend_skills`, `get_skill_context`, `get_skill_execution_guide`, `search_skills`.
5. Read resource `skills://contract` when tool choice is unclear.

**Authoring exception:** agents may read `skills/**` and `skills_docs/**` when you explicitly ask to author, validate or maintain skills.

### Verify MCP-only mode

In a new chat, ask: *“Which skill should I use for MCP server design?”*

| Expected | Not expected |
| --- | --- |
| MCP calls to `route_skill_query`, `recommend_skills`, etc. | `Read` on `skills/**/SKILL.md` for routing |
| Bounded MCP payloads with evidence | Full library scan via `discover-local-skills` |

Optional: after MCP calls, check Grafana **Skills KG Usage** for tool hit metrics (`docker compose up -d`).

### Optional — Neo4j-backed MCP

Default stdio **skills-kg** builds an in-memory graph from the repository at startup.

For a live graph via Docker:

```bash
docker compose up -d
```

Point Cursor at `http://127.0.0.1:8000/mcp` if your Cursor build supports URL MCP servers. See `SKILLS_KG_MCP_RUNBOOK.md` for operator detail.

---

## Mode B — filesystem skills only

Use this for **portable drop-in** workflows, offline use without MCP, or when copying `skills/` into another repository. Matches `AGENTS.md`, `CLAUDE.md` and `DROP_IN_BOOTSTRAP.md`.

### Step 1 — Enable filesystem agent skills

Edit `.vscode/settings.json`:

```json
"chat.agentSkillsLocations": {
  "/path/to/coding-agent-skill-library/skills": true,
  ".agents/skills": false,
  ".github/skills": false,
  ".claude/skills": false,
  "~/.agents/skills": false,
  "~/.copilot/skills": false,
  "~/.claude/skills": false
}
```

Replace `/path/to/coding-agent-skill-library` with your clone path.

### Step 2 — Disable MCP-only project rule

Either:

- **Rename or remove** `.cursor/rules/skills-kg-mcp-only.mdc`, or
- Set `alwaysApply: false` in that file’s frontmatter and restart Cursor.

Without this step, the MCP-only rule will still override filesystem-first instructions.

### Step 3 — Disable skills-kg MCP (optional)

**Cursor → Settings → Plugins → Tools & MCPs** → turn **Off** **`skills-kg`**.

Filesystem mode does not require MCP. Keeping MCP enabled is harmless if agents follow `AGENTS.md`, but disabling it avoids accidental dual paths.

### Step 4 — Configure Rules, Skills, Subagents (recommended)

Open **Cursor → Settings → Plugins → Rules, Skills, Subagents → Skills** and adjust:

| Skill | Action | Reason |
| --- | --- | --- |
| **`apply-laws-of-ai`** | **Keep** | Mandatory baseline before other skills |
| **`discover-local-skills`** | **Keep** (optional) | Helps agents search `skills/` before planning |
| **`github-workflow-best-practices`** | **Keep** (optional) | GitHub Actions guidance outside the library |

You can rely on `AGENTS.md` alone without global Cursor skills if your user rules already mandate the startup order.

### Expected agent workflow (filesystem)

1. Read `AGENTIC_CODING_GLOBAL_SAFETY.md` and `SECURE_AGENTIC_DEVELOPMENT.md`.
2. Execute `skills/apply-laws-of-ai/SKILL.md` in full.
3. Route with `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`.
4. Load the smallest matching `skills/<name>/SKILL.md`.

See `AGENTS.md` for the full mandatory startup order.

### Verify filesystem mode

In a new chat, ask for guidance on a known skill (for example TDD).

| Expected | Not expected |
| --- | --- |
| Read of `skills/tdd-practice/SKILL.md` or routing via `HOW_TO_FIND_THE_RIGHT_SKILL.md` | MCP `route_skill_query` as the primary discovery path |

---

## Quick comparison

| Concern | MCP only (Mode A) | Filesystem only (Mode B) |
| --- | --- | --- |
| Skill discovery | `route_skill_query`, `recommend_skills`, … | `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` |
| Skill content | MCP tools (bounded payloads) | Direct `skills/**/SKILL.md` reads |
| Offline | Requires MCP server process | Works with repo checkout only |
| Usage metrics | Yes (Grafana / Prometheus) | No MCP telemetry |
| Repo default | **Yes** | Change settings + disable MCP rule |
| Best for | KG-backed agent workflows in this repo | Portable copy, other IDEs, no Docker/MCP |

---

## Switching modes (checklist)

### MCP only ← you are here (default)

- [ ] `chat.agentSkillsLocations` → repo `skills/` **false**
- [ ] `.cursor/rules/skills-kg-mcp-only.mdc` → **alwaysApply: true**
- [ ] **skills-kg** MCP **On**
- [ ] Remove **`discover-local-skills`** from Cursor Skills

### Filesystem only

- [ ] `chat.agentSkillsLocations` → repo `skills/` **true**
- [ ] Disable or remove **skills-kg-mcp-only** rule
- [ ] **skills-kg** MCP **Off** (recommended)
- [ ] Keep **`apply-laws-of-ai`** in Cursor Skills or enforce via `AGENTS.md`

After any switch, **start a new chat** — existing sessions retain prior context and behaviour.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Agent reads `skills/*.md` in MCP mode | Filesystem locations or `discover-local-skills` still active | Mode A steps 2–3 |
| Agent calls MCP in filesystem mode | MCP-only rule still `alwaysApply: true` | Mode B step 2 |
| **skills-kg** disconnected | Bad path in `mcp.json` or missing `uv` | Fix paths; run `--list-tools` smoke test |
| Duplicate guidance | Both MCP and filesystem enabled | Pick one mode using this guide |
| No skills at all | Both paths disabled | Re-enable MCP **or** filesystem per mode above |

Operator runbook: `SKILLS_KG_MCP_RUNBOOK.md`. Docker and API: `GETTING_STARTED.md`.

---

## Related documents

| Document | Purpose |
| --- | --- |
| `GETTING_STARTED.md` | Docker stack, MCP smoke tests, validation |
| `SKILLS_KG_MCP_RUNBOOK.md` | Rebuild graph, Neo4j, observability |
| `AGENTS.md` / `CLAUDE.md` | Filesystem mandatory startup order |
| `DROP_IN_BOOTSTRAP.md` | Portable library copy without KG service |
| `HOW_TO_FIND_THE_RIGHT_SKILL.md` | Task-shape routing (filesystem mode) |
