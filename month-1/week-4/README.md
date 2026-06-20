# Week 4 — Candidate Research Agent

## What It Does
An AI agent that researches job candidates by extracting 
information from their resume, then verifying technical 
credibility through direct GitHub API integration, and 
assesses their fit against given job requirements.

## Why This Matters
Most candidates a recruiter actually needs to research 
are early career or currently unemployed, not public 
figures with strong search visibility online. General 
web search proved unreliable for this exact reason, 
detailed below.

## The Architecture That Changed Mid-Build

### Attempt 1: General web search
Used SerpAPI to search the open web for candidate 
information by name. Consistently returned irrelevant 
results, generic job postings, unrelated people sharing 
similar names. Google search deprioritizes specific rare 
terms in favor of common popular ones, making name based 
search unreliable for early career candidates.

### Attempt 2: Site-restricted search
Restricted search specifically to site:linkedin.com and 
site:github.com. Removed irrelevant noise completely, 
but still failed to surface specific individuals due to 
search engine indexing delays for recently created or 
updated profiles.

### Final approach: Direct extraction and API verification
Extract LinkedIn and GitHub URLs directly from resume 
text using pattern matching. For GitHub, call the GitHub 
REST API directly to pull verified, structured data, real 
repositories, real bio, real activity. For LinkedIn, 
verify the URL exists as a credibility signal only, since 
LinkedIn's API is not realistically accessible for this 
use case.

This trades search-based guessing for precision, the 
agent only acts on information the candidate explicitly 
provided, never guesses who someone might be online.

## Key Engineering Decisions

- GitHub API over search scraping, for structured, 
  verifiable data instead of noisy snippets
- LinkedIn scoped to verification only, an honest 
  limitation rather than a broken workaround
- Explicit rule preventing GitHub follower count or 
  stars from influencing employability judgment, to 
  avoid unfair bias against early-career candidates
- Strict hallucination prevention, agent must say 
  "not specified" rather than estimate missing details

## Verified Test Result
Tested with real personal data, agent correctly extracted 
GitHub username from resume, pulled actual repository 
data through the GitHub API, and incorporated that real 
information into the final fit assessment without 
fabricating anything not present in the source data.

## What I Learned
- ReAct agent pattern, reasoning, acting, observing
- Tool design matters more than prompt wording for 
  preventing hallucination
- General search is unreliable for specific individual 
  lookup, direct data sources are far more trustworthy
- Real APIs over scraping wherever genuinely available
- Designing fairness constraints directly into a system 
  prompt, not just functional correctness

## Tech Stack
Python | LangChain | LangChain-Groq | GitHub REST API | 
SerpAPI | Regex

## Status
Complete and verified with real data

## Next
Week 5 — LangGraph, rebuilding this agent with explicit 
state management and decision nodes