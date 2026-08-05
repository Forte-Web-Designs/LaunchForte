# Fortress operating notes

## Job classes
The runner knows exactly five: client_ui, doc_update, export, generator, site_pass.
Timeouts: doc_update 300s, export 300s, client_ui 900s, site_pass 1200s, generator 1800s.
Playwright is available to client_ui, generator and site_pass only.
Any other class is refused before a token is spent.

## task-note webhook
Valid type values: task, note, amend. Anything else is rejected outright.
To move a task status, post type amend with task_id and to_status.

## n8n publish state
A workflow is only live when versionId equals activeVersionId, read from a response that returned HTTP 200.
Comparing two undefined values returns true and looks like a pass.

## Data table filters
Every filter condition needs both a keyName and a condition operator.
Missing either one makes the query match nothing, silently, with no error.

## Expressions
n8n only evaluates a parameter whose stored value begins with an equals sign.
Without it the braces are sent literally and lookups return nothing.

## Logs
The live runner log is logs/runner.log. The file logs/launchagent.out.log is stale and should be ignored.
