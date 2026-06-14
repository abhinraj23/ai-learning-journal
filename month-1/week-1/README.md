# Week 1 - Recruitment Assistant Chatbot

## What It Does
CLI-based recruitment assistant chatbot 
with persistent conversation memory.

## Business Problem
Recruitment agencies receive repetitive 
candidate inquiries. This chatbot handles 
basic Q&A automatically and remembers 
context across sessions.

## Features
- Persistent conversation history via JSON
- Error handling for API failures
- Clear command to reset conversation
- Graceful exit saving conversation
- Temperature and token controls

## What I Learned
- Raw Groq API calls in Python
- JSON file reading and writing
- Error handling with try/except
- Environment variables with dotenv
- Git workflow — real debugging experience

## How To Run
1. Clone repository
2. Create .env with GROQ_API_KEY=your_key
3. pip install requests python-dotenv
4. python3 chatbot.py

## Tech Stack
Python | Groq API | JSON | python-dotenv

## Status
Complete — Week 1 foundation done
Next: Week 2 Job Description Generator
