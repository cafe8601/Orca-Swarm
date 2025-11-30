# Research Domain Agents

Specialized agents for academic research, literature review, and scholarly content creation.

## Agent Inventory

| Agent | Primary Focus | Key Capabilities |
|-------|---------------|------------------|
| academic-researcher | Academic research methodology | Literature review, citation management, research design |
| citation-manager | Reference management | Citation formatting, bibliography, source verification |
| literature-synthesizer | Research synthesis | Gap analysis, thematic analysis, meta-synthesis |
| paper-writer | Academic writing | Paper structure, scientific writing, peer review prep |

## Use Cases

### Literature Review
1. `academic-researcher` - Define search strategy and methodology
2. `literature-synthesizer` - Analyze and synthesize findings
3. `paper-writer` - Write the review document

### Paper Writing
1. `academic-researcher` - Background research and methodology
2. `citation-manager` - Manage references and citations
3. `paper-writer` - Draft and refine the paper

### Research Planning
1. `academic-researcher` - Define research questions and methodology
2. `literature-synthesizer` - Identify gaps and opportunities

## Integration with Profiles

These agents are automatically activated when using the `researcher` profile:

```python
from profiles import ProfileManager

manager = ProfileManager()
manager.set_active_profile("researcher")
# Research agents are now available
```

## Workflow Templates

Research agents integrate with these workflow templates:
- `literature_review` - Systematic literature review
- `paper_writing` - Academic paper creation
- `technical_report` - Technical documentation
