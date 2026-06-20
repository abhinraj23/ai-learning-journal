import os
import requests
from dotenv import load_dotenv
import time

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
    searches the web for additional public information about a job candidate on Github profile and verify linkedin profile if provided.
    Only use this if there is a Linkedlin URL or Github URL or both in the resume content after extraction to find supplimentary context.
    Results may be limited or empty for some candidates without a proper online presence,
    it is normal and expected.
    Do not treat empty results as failure.
    input should be the entire extracted resume content
    """
    import re

    results=[]

    #extract linkedin
    linkedin=re.search(r'linkedin\.com/in/[^\s]+',resume_text,re.IGNORECASE)

    #extract github
    github=re.search(r'github\.com/[^\s]+',resume_text,re.IGNORECASE)
    
    #linkedin verification
    if linkedin:
        results.append(f"LinkedIn profile found : {linkedin.group()}")
    
    #github analysis
    if github:
        url=github.group()
        username=url.rstrip("/").split("/")[-1]

        try:

            #Github profile
            profile=requests.get(f"https://api.github.com/users/{username}").json()

            if profile.get("message")=="Not Found":
                return "Github profile not found"

            #Repositories
            repos=requests.get(f"https://api.github.com/users/{username}/repos").json()

            repo_names=[]

            if isinstance(repos,list):
                for repo in repos[:5]:
                    repo_names.append(repo.get("name",""))
            
            results.append(f"""
            Github profile found
            
            Username: {profile.get("login",'N/A')}
            Name: {profile.get("name","N/A")}
            Bio: {profile.get("bio","N/A")}
            Public Repos: {profile.get("public_repos",0)}
            Followers: {profile.get("followers",0)}

            Top repositories:
            {",".join(repo_names) if repo_names else "None"}

            """)
        
        except Exception as e:
            print("Error ",e)
            results.append(f"Github analysis is failed: {str(e)}")

    if not results:
        return "No github or linkedin profile found"

    print(results)
    return "\n\n".join(results)

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

MUST: If years of experience are not explicitly stated,
respond with "Experience not specified".
Do not assume 0 years.
Do not assume 1 year.

If a Linkedin URL or Github URL is present inside the resume content:
-call the search_additional_info tool by passing ENTIRE resume text
-use any returned info to strengthen the assessment

Do not infer professional reputation, network strength,
or employability from GitHub follower count, stars,
or other social metrics.

Treat personal projects and public repositories as
evidence of practical technical skills, especially for
students and early-career candidates.

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


