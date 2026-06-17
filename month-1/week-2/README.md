# Week 2 - AI Job Description Generator

## What It Does
Generates professional job descriptions by analyzing 
real job postings from Google Jobs... not hallucinating 
from general knowledge.

## Business Problem
Writing job descriptions manually takes recruiters 
1-2 hours per role. This tool generates a complete 
market-accurate job description in under 60 seconds.

## How It Works

User inputs role + location + experience
↓
SerpAPI searches Google Jobs - finds 5 real postings
↓
Stage 1: LLM extracts common patterns from real data
↓
Stage 2: LLM generates JD strictly from those patterns
↓
Pydantic validates the output structure
↓
Saves as .txt and .json

## What Makes This Different
Most AI job description tools prompt an LLM directly 
and get generic output. This tool grounds generation 
in real market data - making output reflect actual 
hiring requirements not LLM assumptions.

## Key Concepts Learned
- Pydantic data validation for reliable LLM outputs
- Two stage AI pipeline - extract then generate
- External API integration with SerpAPI
- Structured JSON outputs from LLMs
- DRY principle - helper functions for reusable logic
- Retry logic for LLM validation failures
- Primitive RAG pipeline - retrieve then generate

## Tech Stack
Python | Groq API | SerpAPI | Pydantic | python-dotenv

## How To Run
1. Clone this repository
2. Create .env file with:
   GROQ_API_KEY=your_groq_key
   SERPAPI_KEY=your_serpapi_key
3. Install dependencies:
   pip install requests python-dotenv pydantic
4. Run:
   python3 job_generator.py
5. Enter job details when prompted

## Sample Output
See samp output for a real generated example

## Status
Complete
Next: Week 3 - Rebuild in LangChain