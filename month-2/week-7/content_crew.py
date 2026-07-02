
from dotenv import load_dotenv
import os
from crewai import Agent, Task, Crew ,LLM

load_dotenv()

llm = LLM( 
    model="gemini/gemini-2.5-flash",
    temperature=0.3
)

# AGENTS

researcher = Agent(
    role="Client and Market Researcher",
    goal="Research the client's brand voice, industry context, and current market trends relevant to the content topic",
    backstory="""You are a meticulous researcher who 
    understands how to read a client's industry and 
    brand voice, and connect it to current trends. You 
    report only what you can reasonably determine, you 
    do not invent client details that weren't provided.""",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Draft content that matches the client's brand voice and incorporates the researched context",
    backstory="""You are a skilled writer who adapts tone 
    and style to match a specific client's brand voice, 
    using research provided rather than writing generically.""",
    llm=llm,
    verbose=True
)

editor = Agent(
    role="Brand Voice Editor",
    goal="Review the draft specifically for brand voice consistency, accuracy against the research, and overall clarity",
    backstory="""You are a sharp editor who checks whether 
    a draft actually sounds like the client's brand, not 
    just whether it's grammatically correct. You flag 
    anything that contradicts the research or feels 
    generic.""",
    llm=llm,
    verbose=True
)

formatter = Agent(
    role="Platform Formatter",
    goal="Reformat the approved content into versions suited for specific platforms",
    backstory="""You understand the different conventions 
    of LinkedIn, Twitter, and email newsletters, you 
    reshape content length, tone, and structure 
    appropriately for each platform without changing the 
    core message.""",
    llm=llm,
    verbose=True
)


# QUALITY GATE CALLBACK

def check_editing_quality(output):
    
    result_text = str(output).lower()

    if "generic" in result_text or "does not match" in result_text or "doesn't match" in result_text:
        print("\n⚠️  QUALITY GATE: Editor flagged potential brand voice issues")
    else:
        print("\n✅ QUALITY GATE: Editor found no major issues")

    return output


# TASKS

research_task = Task(
    description="""Research context for this content request:
    
    Client: {client_name}
    Industry: {industry}
    Brand Voice: {brand_voice}
    Topic: {topic}
    
    Identify 3-4 relevant points connecting the topic to 
    current trends in this industry, and note how the 
    brand voice should shape the tone.""",
    expected_output="3-4 researched points plus brand voice notes",
    agent=researcher
)

writing_task = Task(
    description="""Using the research provided, write a 
    200 word draft about {topic} for {client_name}, 
    matching their brand voice and incorporating the 
    researched trends.""",
    expected_output="A 200 word draft matching the brand voice",
    agent=writer,
    context=[research_task]
)

editing_task = Task(
    description="""Review the draft against the original 
    research and brand voice notes. Flag and fix anything 
    that sounds generic or contradicts the brand voice. 
    Return the improved version.""",
    expected_output="A brand-voice-consistent, polished draft",
    agent=editor,
    context=[research_task, writing_task],
    callback=check_editing_quality
)

formatting_task = Task(
    description="""Take the approved content and create 
    three versions: a LinkedIn post, a short Twitter post, 
    and an email newsletter intro paragraph.""",
    expected_output="Three platform-specific versions of the content",
    agent=formatter,
    context=[editing_task]
)


# CREW ASSEMBLY

crew=Crew(
    agents=[researcher, writer, editor, formatter],
    tasks=[research_task, writing_task, editing_task, formatting_task],
    verbose=True,
    process="sequential"
)


# RETRY WRAPPER

def run_crew_with_retry(crew, inputs, max_attempts=2):

    for attempt in range(max_attempts):
        try:
            result = crew.kickoff(inputs=inputs)
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                print("All attempts failed.")
                return None
    return None

# MAIN

if __name__ == "__main__":
    result = run_crew_with_retry(crew, inputs={
        "client_name": "MindMagic",
        "industry": "mental health and life strategy",
        "brand_voice": "bold,motivational,poetic, slightly playful,Empaphasizes on life success,mind as a superpower",
        "topic": "the effect of mind and beliefs in mixed martial arts"
    })

    if result:
        print("\n\n=== FINAL OUTPUT ===")
        print(result)
    else:
        print("Pipeline failed after retries.")