{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Note Schema v1",
  "type": "object",
  "required": ["id", "type", "status", "created", "modified", "version", "owner"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    },
    "type": {
      "type": "string",
      "enum": ["project-note", "area-note", "concept-note", "entity-note", 
               "literature-note", "execution-script", "governance-rule", "archive-manifest"]
    },
    "status": {
      "type": "string",
      "enum": ["draft", "active", "review", "stale", "archived"]
    },
    "created": {
      "type": "string",
      "format": "date-time"
    },
    "modified": {
      "type": "string",
      "format": "date-time"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "owner": {
      "type": "string",
      "pattern": "^(system|user|agent-[a-f0-9]+)$"
    }
  }
}