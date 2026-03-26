# Allowed Commands

This document lists the supported `know` CLI commands in a compact reference format.

The CLI also loads a local `.env` file at startup. When a command below mentions an OS variable, that value can come from the current environment or from `.env`.

## Placeholders

- `$KEY`: knowledge key name
- `$URL`: HTTP or HTTPS URL
- `$URL_OR_PATH`: HTTP or HTTPS URL, or a local filesystem path
- `$PATH`: filesystem path
- `$NAME`: generic name
- `$VALUE`: generic value
- `$CQL`: Confluence Query Language expression
- `$REPO`: Git repository URL
- `$SOURCE_ID`: registered source id
- `$OWNER_REPO`: GitHub repository in `owner/repo` format
- `$FORMAT`: `json`, `television`, or `television-preview`
- `$ENTRY`: selected row used with `television-preview`

## Notes

- `[ ... ]` marks optional arguments.
- Commands that show one flag multiple times use the flag as repeatable input.
- `know add confluence` requires at least one of `--space` or `--cql`.
- `know search confluence` and `know search jira` accept an optional free-text query.
- `know add tv` also accepts the alias `know add television`.
- `know add tv` without a channel name installs the bundled Television cable files.

## Add Commands

# Register an Aha workspace source; if flags are omitted, default connection values can come from `AHA_BASE_URL` and `AHA_TOKEN`
`know add aha $NAME --key $KEY [--base-url $URL] [--token $NAME] [--limit N]`

# Register an arXiv paper source
`know add arxiv $URL --key $KEY`

# Register a Confluence source by space or by a saved CQL query; if flags are omitted, default connection values can come from `CONFLUENCE_BASE_URL`, `CONFLUENCE_USERNAME`, and `CONFLUENCE_TOKEN`
`know add confluence [--space $NAME] [--cql $CQL] --key $KEY [--base-url $URL] [--username $NAME] [--token $NAME] [--limit N]`

# Register a GitHub repository source
`know add github-repo $REPO --key $KEY [--branch $NAME ...]`

# Register a Google Cloud release notes feed
`know add google-releases $URL --key $KEY`

# Register a Jira project source; if flags are omitted, default connection values can come from `JIRA_BASE_URL`, `JIRA_USERNAME`, and `JIRA_TOKEN`
`know add jira-project $NAME --key $KEY [--base-url $URL] [--username $NAME] [--token $NAME] [--jql $VALUE] [--field $NAME ...] [--limit N]`

# Create a knowledge key
`know add key $KEY`

# Register a website source
`know add site $URL --key $KEY [--max-depth N] [--max-pages N]`

# Install the repository's bundled Television cable files
`know add tv`

# Register a Television channel source
`know add tv [$NAME] [--key $KEY] [--source-command $VALUE] [--description $VALUE] [--source-display $VALUE] [--preview-command $VALUE] [--action-command $VALUE]`

# Equivalent alias for the same Television channel source command
`know add television [$NAME] [--key $KEY] [--source-command $VALUE] [--description $VALUE] [--source-display $VALUE] [--preview-command $VALUE] [--action-command $VALUE]`

# Install the repository's pre-built Television cable files on Unix-like systems
`mkdir -p ~/.config/television/cable && cp cables/*.toml ~/.config/television/cable/`

# Install the repository's pre-built Television cable files on Windows PowerShell
`New-Item -ItemType Directory -Force -Path $HOME/.config/television/cable | Out-Null; Copy-Item cables/*.toml $HOME/.config/television/cable/`

# Register a video source from a URL or local path
`know add video $URL_OR_PATH --key $KEY [--language $NAME ...]`

## Browse Commands

# Browse Aha items with sync status
`know browse aha [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse arXiv items with sync status
`know browse arxiv [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse keys across the whole store
`know browse by-key [--format $FORMAT] [--entry $ENTRY]`

# Browse source types across the whole store
`know browse by-type [--format $FORMAT] [--entry $ENTRY]`

# Browse saved operational commands
`know browse commands [--format $FORMAT] [--entry $ENTRY]`

# Browse Confluence items with sync status
`know browse confluence [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse sources shared across multiple keys
`know browse crossref [--format $FORMAT] [--entry $ENTRY]`

# Browse local files with optional full-text filtering
`know browse files [--query $VALUE] [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse GitHub repositories you have interacted with; remote access uses `GITHUB_TOKEN` when present and otherwise falls back to stored credentials such as `github_token`
`know browse github [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse issues, pull requests, and discussions for one GitHub repository; remote access uses `GITHUB_TOKEN` when present and otherwise falls back to stored credentials such as `github_token`
`know browse github-activity $OWNER_REPO [--format $FORMAT] [--entry $ENTRY]`

# Browse Jira items with sync status
`know browse jira [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse the sources attached to one key
`know browse key-sources --key $KEY [--format $FORMAT] [--entry $ENTRY]`

# Browse all local knowledge files
`know browse local [--key $KEY] [--type $NAME] [--format $FORMAT] [--entry $ENTRY]`

# Browse all arXiv papers across keys
`know browse papers [--format $FORMAT] [--entry $ENTRY]`

# Browse recently synced sources
`know browse recent [--limit N] [--format $FORMAT] [--entry $ENTRY]`

# Browse Google release notes with sync status
`know browse releases [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse files inside a synced repository
`know browse repo-files [--repo $NAME] [--format $FORMAT] [--entry $ENTRY]`

# Browse all synced GitHub repositories across keys
`know browse repos [--format $FORMAT] [--entry $ENTRY]`

# Browse website sources with sync status
`know browse sites [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

# Browse the files attached to one source
`know browse source-files --key $KEY --source-id $SOURCE_ID [--format $FORMAT] [--entry $ENTRY]`

# Browse stale sources
`know browse stale [--days N] [--format $FORMAT] [--entry $ENTRY]`

# Browse store statistics
`know browse stats [--format $FORMAT] [--entry $ENTRY]`

# Browse the chronological source timeline
`know browse timeline [--format $FORMAT] [--entry $ENTRY]`

# Browse never-synced sources
`know browse unsynced [--format $FORMAT] [--entry $ENTRY]`

# Browse video sources with sync status
`know browse videos [--key $KEY] [--format $FORMAT] [--entry $ENTRY]`

## Delete Commands

# Delete a registered source from a key
`know del --key $KEY $SOURCE_ID`

## Export And Import Commands

# Export one key or the full store to a zip archive
`know export [--key $KEY]`

# Import a previously exported zip archive
`know import $PATH`

## Global Command

# Show the top-level CLI help
`know --help`

# Initialize the knowledge store
`know init`

## Global Flags

# Emit JSON output
`know --json list keys`

# Suppress non-error output
`know --quiet export --key $KEY`

# Override the default `~/.knowledge` store path
`know --store $PATH list keys`

# Print progress messages
`know --verbose sync --key $KEY`

## List Commands

# List stored credentials
`know list credentials`

# List knowledge keys
`know list keys [--format $FORMAT] [--entry $ENTRY]`

# List registered sources
`know list sources [--key $KEY] [--type $NAME] [--format $FORMAT] [--entry $ENTRY]`

## Search Commands

# Search the arXiv public API
`know search arxiv "$VALUE" [--start N] [--max-results N] [--sort-by relevance|lastUpdatedDate|submittedDate] [--sort-order ascending|descending] [--format $FORMAT] [--entry $ENTRY]`

# Search Confluence content through configured sources
`know search confluence ["$VALUE"] [--knowledge-key $KEY] [--space $NAME] [--cql $VALUE] [--type $NAME] [--label $NAME ...] [--title-contains $VALUE] [--text-contains $VALUE] [--created-after $VALUE] [--created-before $VALUE] [--updated-after $VALUE] [--updated-before $VALUE] [--limit N] [--cursor $VALUE] [--format $FORMAT] [--entry $ENTRY]`

# Search Jira issues through configured sources
`know search jira ["$VALUE"] [--knowledge-key $KEY] [--project $NAME] [--jql $VALUE] [--status $NAME ...] [--issue-type $NAME ...] [--assignee $NAME] [--reporter $NAME] [--created-after $VALUE] [--created-before $VALUE] [--updated-after $VALUE] [--updated-before $VALUE] [--order-by $VALUE ...] [--field $NAME ...] [--property $NAME ...] [--expand $NAME ...] [--fields-by-keys] [--limit N] [--next-page-token $VALUE] [--format $FORMAT] [--entry $ENTRY]`

## Set Commands

# Store a credential value; source configs can also reference OS variables with `$env:ENV_VAR_NAME` instead of a stored credential
`know set credential $NAME $VALUE`

## Sync Commands

# Synchronize an Aha workspace source
`know sync aha $NAME --key $KEY`

# Synchronize an arXiv source
`know sync arxiv $URL --key $KEY`

# Synchronize a Confluence source
`know sync confluence --space $NAME --key $KEY`

# Synchronize a GitHub repository source
`know sync github-repo $REPO --key $KEY [--branch $NAME ...]`

# Synchronize a Google Cloud release notes source
`know sync google-releases $URL --key $KEY`

# Synchronize a Jira project source
`know sync jira-project $NAME --key $KEY`

# Synchronize a website source
`know sync site $URL --key $KEY`

# Synchronize a Television source
`know sync television $NAME --key $KEY`

# Synchronize a video source
`know sync video $URL_OR_PATH --key $KEY`

# Synchronize every source attached to a key
`know sync --key $KEY`
