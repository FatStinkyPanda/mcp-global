# MCP Global Rules - AI Agent Quick Reference

## Available Commands (60+ total)

Run with: `python mcp-global-rules/mcp.py <command>`

### Before Coding - Context Loading
```bash
mcp autocontext              # Load 3-tier context (warm + skeleton + semantic)
mcp predict-context "task"   # Pre-bundle files for your task
mcp recall "topic"           # Search memory
mcp search "query"           # Semantic code search
mcp hybrid-search "query"    # Multi-dimensional search (semantic+structural+temporal)
```

### Understanding the Codebase
```bash
mcp skeleton src/            # Get signature-only code views (28% smaller)
mcp graph "function"         # Query call graph relationships
mcp correlate                # See which files change together
mcp state                    # View project goals/tasks/lessons
```

### While Coding
```bash
mcp predict-bugs file.py     # Check for bugs
mcp impact file.py           # What breaks?
mcp context "query"          # Get context
mcp heal "error message"     # Get fix suggestions
```

### After Coding
```bash
mcp review file.py           # Code review
mcp security file.py         # Security check
mcp test-gen file.py --impl  # Generate tests
```

### Learning & Memory
```bash
mcp remember "key" "value"   # Store knowledge
mcp recall "query"           # Search knowledge
mcp heal --learn "lesson"    # Add lesson (auto-injected to context)
mcp auto-learn               # View learning stats
mcp learn-patterns           # Analyze git for file correlations
```

## Hooks (Automatic - Strictly Enforced)

All hooks run automatically with bypass detection:
- **pre-commit**: Records flag + fix + bugs + security + review + patterns
- **post-commit**: Records commit + auto-learn + correlations + index updates
- **pre-push**: Verifies no bypasses + security + architecture validation

**Bypass Detection**: Using `--no-verify` is detected and logged. Warnings shown on push.

## Advanced Features

| Feature | Command |
|---------|---------|
| **Skeleton Context** | `mcp skeleton` - Compressed code views |
| **Hybrid Graph** | `mcp hybrid-search` - 4-dimensional search |
| **Auto-Learning** | `mcp auto-learn --from-commit` - Learn from commits |
| **Hook Guardian** | `mcp hook-guardian` - Track bypass attempts |
| **Predictive Context** | `mcp predict-context "task"` - Pre-bundle files |
| **Error Healing** | `mcp heal` - Analyze errors, suggest fixes |

## Key Directories

- `mcp-global-rules/` - MCP package (scripts, hooks, config)
- `.mcp/` - Index data, learning data, graphs (auto-generated)

## New in This Version

- **3-Tier Context**: Warm (state+lessons) + Structure (skeleton+graph) + Active (files)
- **Hybrid Knowledge Graph**: Combines semantic, structural, temporal, co-modification signals
- **Auto-Learning**: Extracts lessons from commits, tracks test outcomes, learns patterns
- **Hook Guardian**: Detects and logs bypass attempts, enforces compliance
