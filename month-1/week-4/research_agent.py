import os
import requests
from dotenv import load_dotenv
import time

from langchain_classic import hub
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent

#load dotenv fils
load_dotenv()

#api keys
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
SERPAPI_KEY=os.environ.get("SERPAPI_KEY")

#LLM object
llm=ChatGroq(model="llama-3.3-70b-versatile",temperature=0.1)


#Tools for the agent

#Tool for extracting resume data
@tool
def extract_resume_data(resume:str)->str:
    '''
    Extracts structured information from raw resume text.
    Use this first,always,when given resume text.
    returns key skills,years of experience,educational qualifications,and notable achivement and project found in resume.
    input text should be raw resume text given by the user.
    '''
    prompt=f'''Extract the following from the resume text:
    -Skills mentioned
    - Years of experience
    - Education
    - Notable achievements or projects

    resume text:
    {resume}

    return a brief and clear structured summary,plain text,NO JSON.
    '''

    result=llm.invoke(prompt)
    return result.content

#Tool for scraping additional information about candidate from web
@tool
def search_additional_info(resume_text: str)-> str:
    """
    searches the web for additional public information about a job candidate,such as linkedIn and Github profiles.
    Only use this if there is a Linkedlin URL or Github URL or both in the resume content after extraction to find supplimentary context.
    Results may be limited or empty for some candidates without a proper online presence,
    it is normal and expected.
    Do not treat empty results as failure.
    input should be the entire extracted resume content
    """
    import re
    #extract linkedin
    linkedin=re.search(r'linkedin\.com/in/[^\s]+',resume_text,re.IGNORECASE)

    #extract github
    github=re.search(r'github\.com/in/[^\s]+',resume_text,re.IGNORECASE)

    if linkedin and github:
        query=f'"{linkedin.group()}" OR "{github.group()}"'

    elif linkedin:
        query=f'"{linkedin.group()}"'

    elif github:
        query=f'"{github.group()}"'

    else:
        return "no linkedin or github account found in the resume"
    

    time.sleep(2)

    response=requests.get("https://serpapi.com/search",params={"q":query,"api_key":SERPAPI_KEY,"num":3})

    if response.status_code != 200:
        return "Search unavailable right now,proceed only with resume content"
    
    data=response.json()

    if "organic_results" not in data:
        return "No additional information found online,its normal and proceed only with resume content"

    if "organic_results" in data:
        for i, result in enumerate(data["organic_results"]):
            print(f"\n--- Result {i+1} ---")
            print("Title:", result.get("title", "No title"))
            print("Link:", result.get("link", "No link"))
    else:
        print("No results found")

    snippets=[]
    for result in data["organic_results"][:3]:
        title=result.get("title","")
        link=result.get("link","")
        snippet=result.get("snippet","")[:200]
        if snippet:
            snippets.append(f"{title} ({link}): {snippet}")
    
    if not snippets:
        return "No useful information found,this is normal,proceed only with resume content"
    
    return "\n".join(snippets)

tools=[extract_resume_data,search_additional_info]

#Agent creation
agent=create_agent(model=llm,tools=tools,system_prompt="""You are a recruitment research agent
You have two tools available:
1)extract_resume_data,always use this first when given resume data
2)search_additional_info,use this after extracting resume data to get additional context if needed,its optional

Many candidates will havd no online presence at all,it is normal and dont treat it as a failure and dont apoligise for it.

CRITICAL RULE:
If the resume text provided is empty, says N/A, or contains
no real candidate information, you MUST respond exactly with:
"Insufficient information provided to assess this candidate."

For any specific detail not explicitly stated in the resume,
such as exact years of experience, specific company names,
or skills not mentioned, you MUST say "not specified in resume"
rather than estimating, assuming, or inventing a number or detail.

Do NOT invent, assume, or fabricate any skills, experience,
years, companies, or background information that was not
explicitly written in the provided resume text.

If a Linkedin URL or Github URL is present inside the resume content:
-call the search_additional_info tool by passing ENTIRE resume text
-use any returned info to strengthen the assessment

Your job is to assess how well a candidate fits given job requirements,based primarily on given resume content and additional web information is supplimentary enrichment.No assumptions or invention.

Give a clear,brief fit assessment with a rating out of 10 and 2-3 sentence explaining the assessment and rating using only real information.
Also provide information about the use of search_additional_info tool even if it haven't used or used
""")

#function for loading text files
def load_text_file(filepath):
    with open(filepath,"r",encoding="utf-8") as f:
        return f.read()

resume_text=load_text_file("sample_resume.txt")
job_requirements=load_text_file("sample_job_requirements.txt")

#Calling the Agent
result=agent.invoke({
    "messages": [
        {"role": "user", "content":f"""Here is a candidate resume:
        {resume_text}

        Job requirements:
        {job_requirements}

        assess this candidate fit for this role.
        """}
    ]
})
print(result["messages"][-1].content)


