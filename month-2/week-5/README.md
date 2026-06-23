# Week 5 - LangGraph Foundations

## What It Does
Rebuilds the Week 4 candidate research agent using 
explicit graph structure instead of a single agent 
loop following prompt instructions.

## Why Rebuild Something That Already Worked
Week 4's agent relied on one long system prompt to 
handle hallucination prevention, tool ordering, and 
reporting rules simultaneously. This worked but 
depended entirely on the model correctly following 
every instruction every time.

LangGraph moves that logic into actual code structure. 
Decisions like "skip assessment if extraction found 
nothing" are now enforced by which function literally 
gets called, not by hoping a prompt rule was followed.

## Architecture

extract → conditional branch
  if insufficient info → skip → end
  if sufficient info → github_check + linkedin_check (parallel) → assess → end

## Key Concepts Learned
- State as a shared dictionary passed through every node
- Nodes as plain functions, no special class required
- Conditional edges for real branching logic in code
- Parallel edges for running independent steps simultaneously
- Append pattern for safe shared state writes during parallel execution

## What Changed From Week 4
- GitHub verification and LinkedIn verification now 
  run simultaneously instead of sequentially
- Skip logic is explicit code, not a prompt instruction
- Network error handling added with proper timeouts

## Tech Stack
Python | LangGraph | LangChain-Groq | GitHub REST API | Regex

## Status
Complete

## Next
Week 6 - Advanced LangGraph, human-in-the-loop and 
checkpointing