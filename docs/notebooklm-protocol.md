# NotebookLM Protocol

This protocol records the operating boundaries for NotebookLM in Research OS.

NotebookLM is a source-centered literature memory layer. It can organize imported sources, answer source-grounded questions, and produce study artifacts. It cannot be the final source of truth for a paper claim.

## Source Limits And Behavior

Based on Google NotebookLM Help, a source is a static copy of an imported or uploaded document. NotebookLM uses uploaded sources to answer questions and complete requests.

NotebookLM supports source types including pasted text, Google Docs, Google Slides, Google Sheets, images, Word, text, Markdown, PDF, CSV, PowerPoint, web URLs, ePub, public YouTube URLs, and audio files.

Current documented limits include:

- each source can contain up to 500,000 words or up to 200 MB for uploaded files
- a notebook can include up to 50 sources
- Google Slides imports are limited to 100 slides
- Google Sheets imports are currently limited to 100k tokens

Project impact:

- Register every underlying source in `10_literature/source_manifest.yaml`.
- Register every NotebookLM import in `10_literature/notebooklm_manifest.yaml`.
- Do not assume a NotebookLM source tracks the original source over time.

## Sync Rules

Google Drive imports are copied into NotebookLM. NotebookLM does not automatically track source document changes. Drive sources need manual re-sync when the original changes. Other source types generally need deletion and re-upload to refresh.

Project impact:

- Record `last_synced` in `notebooklm_manifest.yaml`.
- Mark stale imports with `import_status: stale`.
- Do not rely on a stale NotebookLM source for current claims.

## Web And YouTube Limits

For web URLs, NotebookLM imports HTML text. It does not import images, embedded videos, nested webpages, or paywalled webpages. PDF URLs are treated as PDF sources.

For YouTube URLs, only public videos with captions are supported, and NotebookLM imports the transcript text. Recently uploaded videos and videos without speech may fail.

Project impact:

- Record source type and rights status in `source_manifest.yaml`.
- Prefer official papers, benchmark docs, dataset docs, and official repositories when possible.
- Treat web and YouTube imports as convenience copies, not archival sources.

## Privacy And Feedback

Google states that NotebookLM content is not used to directly train foundational models unless the user chooses to provide feedback. Feedback can include prompts, sources, uploads, and outputs, and may be reviewed by humans. Google advises users not to include confidential or sensitive information in feedback.

Project impact:

- Do not store secrets, credentials, cookies, private keys, customer data, or sensitive business information in NotebookLM.
- Do not include confidential or sensitive material in NotebookLM feedback.
- Do not commit NotebookLM auth artifacts.

## Citation Rules

NotebookLM output can be used as a lead only.

Allowed path:

```text
NotebookLM answer
  -> export_index.yaml
  -> verify against source_manifest.yaml source
  -> evidence_map.md
  -> claims.yaml only when supported by primary evidence
```

Forbidden path:

```text
NotebookLM answer
  -> claims.yaml
```

Validator rule:

- supported claims must not cite `10_literature/notebooklm_exports/*` directly
- `notebooklm_exports/export_index.yaml` must keep `allowed_for_claims: false`

## Sources

- Google NotebookLM Help: Add or discover new sources for your notebook, accessed 2026-04-28.
- Google NotebookLM Help: Privacy and Terms of Use in NotebookLM, accessed 2026-04-28.

