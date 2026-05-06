# Shop Sergeant Agentic OS

```yaml
orchestration:
  name: Shop Sergeant Agentic OS
  context: CLAUDE.md
  memory: MEMORY.md
  sub-agents:
    - name: Database
      context: CLAUDE.md
      memory: MEMORY.md
      skills:
        - skill: CRUD
        - skill: Backup
        - skill: Restore
    - name: Slack Response
      context: CLAUDE.md
      memory: MEMORY.md
      skills:
```

