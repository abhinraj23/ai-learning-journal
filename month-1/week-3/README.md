# Week 3 - LangChain Rebuild

## What It Does
Same Job Description Generator from Week 2 -
rebuilt using LangChain instead of raw Python 
HTTP requests.

## Why I Rebuilt The Same Project
Understanding what a framework replaces matters 
more than just using it. This rebuild proves 
every LangChain abstraction maps directly to 
something I already built manually.

## Raw Python vs LangChain - What Changed

### Making an LLM call
Raw Python (Week 2): 15 lines - manual headers, 
JSON structure, response parsing, custom error handling

LangChain (Week 3): ChatGroq object, reusable across 
the entire program, configured once

### Parsing structured output
Raw Python (Week 2): manual json.loads(), manual 
try/except, separate Pydantic validation step

LangChain (Week 3): PydanticOutputParser combines 
JSON parsing and validation in one step

### What did NOT change
- SerpAPI search logic
- Pydantic model structure  
- File saving logic
- Overall pipeline architecture

LangChain only replaced the API calling and 
parsing mechanics - the actual engineering 
decisions stayed identical.

## Key Decisions Made

**JsonOutputParser vs PydanticOutputParser**
Used JsonOutputParser for intermediate data 
(extracted patterns) and PydanticOutputParser 
for final output (the job description itself). 
Final outputs that get saved or used downstream 
need strict validation. Intermediate data passed 
internally doesn't need that overhead.

## Bugs Fixed During Build

- Added retry logic with full exception logging 
  to distinguish transient API failures from 
  structural prompt issues

## What I Learned
- LCEL - chaining prompt | llm | parser
- When to use Pydantic vs simpler JSON parsing
- Field descriptions guide LLM output quality
- Retry logic only helps for transient failures, 
  not structural prompt problems
- .partial() for pre-filling template variables

## Tech Stack
Python | LangChain | LangChain-Groq | Pydantic | SerpAPI

## How To Run
1. Clone repository
2. Add to .env: GROQ_API_KEY and SERPAPI_KEY
3. pip install langchain langchain-groq pydantic 
   requests python-dotenv
4. python3 job_generator_langchain.py

## Status
Complete
Next: Week 4 - First complete agent with tool use
