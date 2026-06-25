# Week 6 - Advanced LangGraph

## What's New
Added checkpointing, human-in-the-loop pausing, and 
streaming on top of Week 5's graph structure.

## Why This Matters
A fully autonomous agent that auto-generates and sends assessments without human review isn't actually what most recruitment teams want.
This adds a real pause point before the final assessment, letting a human approve or reject based on what was gathered first.

Checkpointing means a failed run can resume from where it stopped instead of restarting and re-spending tokens on steps that already succeeded.

## Key Concepts Learned
- MemorySaver for checkpointing graph state
- interrupt_before for pausing execution at a specific node
- Resuming a paused graph using invoke(None, config)
- Streaming execution to observe node-by-node progress

## Tech Stack
Python | LangGraph | LangChain-Groq | GitHub REST API

## Status
Complete

## Next
Week 7 - CrewAI, multi-agent systems with distinct roles