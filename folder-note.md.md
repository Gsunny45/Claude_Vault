---
type: folder-index
status: active
created: {{date}}
modified: {{date}}
---

# {{folder_name}}

## Purpose
[What belongs in this folder?]

## Contents
\`\`\`dataview
LIST
FROM "{{folder_path}}"
WHERE file.name != this.file.name
SORT file.name ASC
\`\`\`

## Notes
