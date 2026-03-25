# Capability Map

Use this document when migrating workflow assets from `.claude/` to other tool formats.

## Purpose

- Treat `.claude/` as the migration source of truth.
- Preserve Claude wording and structure by default.
- Translate capabilities only when the target tool cannot represent the same concept directly.
- Add a `Tool Mapping` section in the generated target file when a direct copy would be ambiguous.

## Canonical Capability Names

Use these capability names in migration notes and adapter sections:

- `ask_user`
- `delegate_worker`
- `background_work`
- `read_file`
- `write_file`
- `edit_file`
- `find_files`
- `search_content`
- `run_command`
- `fetch_web_docs`
- `base_instructions`
- `output_style`

## Mapping Table

| Capability | Claude Code Source | Generic Meaning | Migration Guidance |
|------------|--------------------|-----------------|--------------------|
| `ask_user` | `AskUserQuestion(...)` | Ask the user for missing input or confirmation | Keep direct question flow when supported. Otherwise rewrite as a plain instruction to ask the user before continuing. |
| `delegate_worker` | `Task(subagent_type=...)` | Hand work to a specialist worker or sub-agent | If the target has native agents, map to them. Otherwise convert to "perform this analysis as a separate worker step". |
| `background_work` | `Task(..., run_in_background=true)` / `TaskOutput(...)` | Run independent work concurrently and collect the result later | If the target lacks background tasks, convert to explicit sequential steps and note that concurrency was collapsed. |
| `read_file` | `Read(file_path=...)` | Inspect an existing file | Usually safe to keep as a read instruction. |
| `write_file` | `Write(file_path=...)` | Create or replace a file | Keep as a write instruction unless the target requires a different file-edit primitive. |
| `edit_file` | `Edit(file_path=...)` | Modify part of an existing file | Convert to the target edit primitive or describe the edit behavior generically. |
| `find_files` | `Glob(pattern=...)` | Find files by path pattern | Convert to the target file-discovery syntax or say "search for files matching pattern". |
| `search_content` | `Grep(pattern=...)` | Search file contents | Convert to the target search syntax or say "search content for pattern". |
| `run_command` | `Bash(command=...)` | Run a terminal command | Keep the command when the target supports shell execution. Otherwise rewrite as an explicit manual command step. |
| `fetch_web_docs` | `WebFetch(...)` / web search | Retrieve external documentation | Keep only when the target supports browsing. Otherwise instruct the agent to consult current docs manually. |
| `base_instructions` | `.claude/CLAUDE.md` | Global workflow and behavior rules | Copy the universal guidance first, then remove or rewrite Claude-only tool syntax. |
| `output_style` | `.claude/output-styles/*.md` | Prompt-level response mode | Keep the full intent and behavior. If the target has no native style mode, describe it as an instruction block rather than a mode feature. |

## Tool Mapping Section Template

Use this section only when direct copy from `.claude/` is not enough:

```md
## Tool Mapping

- `ask_user`: [how the target should collect user input]
- `delegate_worker`: [how the target should simulate or invoke specialist work]
- `run_command`: [how shell commands should be executed]
```

Keep the section short. Only include capabilities that actually need clarification for the target platform.

## Migration Rules

1. Read the selected `.claude` asset first.
2. Check whether the target tool supports the same capability natively.
3. Copy content directly when the concepts align.
4. When concepts do not align, preserve the intent and add a `Tool Mapping` section.
5. Prefer partial migration by selected asset or file name over full-repo sync.
