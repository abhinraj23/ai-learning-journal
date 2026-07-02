# AI Content Generation Pipeline with CrewAI

A simple multi-agent content generation workflow built with CrewAI. The system uses specialized AI agents to collaboratively research, write, review, and format content for a client while passing context between each stage.

## Workflow

```
Client Input
      │
      ▼
Researcher
      │
      ▼
Writer
      │
      ▼
Editor
      │
      ▼
Formatter
```

## Agents

### Researcher
- Analyzes the client, industry, topic, and brand voice.
- Identifies relevant market context and trends.
- Provides research for downstream agents.

### Writer
- Generates a content draft using the research.
- Adapts the writing style to match the client's brand voice.

### Editor
- Reviews the draft for clarity, consistency, and brand voice.
- Refines the content before formatting.

### Formatter
- Converts the approved content into:
  - LinkedIn post
  - Twitter/X post
  - Email newsletter introduction

## Features

- Sequential multi-agent workflow using CrewAI.
- Context sharing between tasks.
- Dedicated agent responsibilities.
- Retry mechanism for failed executions.
- Environment variable support using `.env`.
- Modular and easy to extend.

## Technologies

- Python
- CrewAI
- Gemini API
- dotenv

## Sample Input

- Client Name
- Industry
- Brand Voice
- Content Topic

## Output

The pipeline generates:

- A polished content draft.
- A LinkedIn version.
- A Twitter/X version.
- An email newsletter introduction.

## Future Improvements

- Editor-driven revision loop.
- Structured JSON outputs.
- Short-term memory between revisions.
- External search integration for real-time research.
- Conditional workflow routing based on quality checks.