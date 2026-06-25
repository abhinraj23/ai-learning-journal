from langgraph.graph import StateGraph, END 
from typing import TypedDict,Annotated
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import re
import requests
import operator

load_dotenv()

llm=ChatGroq(model="llama-3.3-70b-versatile",temperature=0.2)

github_api="https://api.github.com/users/"


#State Definition
class AgentState(TypedDict):
    candidate_name:str
    resume_text:str
    job_requirements:str
    extracted_info:Annotated[str,operator.add]
    final_assessment:str


#Nodes
def extract_node(state: AgentState)-> dict:
    resume=state["resume_text"]

    if not resume or resume.strip()=="" or resume.strip().upper()=="N/A":
        return {"extracted_info":"Insufficient info provided"}
    prompt=f"""Extract the following from the provided resume text delimited by angle brackets:
    -Skills
    -Years of experience
    -Education
    -Notable projects ot achievements

    resume:
    <{resume}>

    return a brief structured plain text summary
    if something isn't mentioned,say "not specified".
    """
    response=llm.invoke(prompt)
    return {"extracted_info":response.content}
    

def github_node(state: AgentState)-> dict:
    resume=state["resume_text"]

    matched_info=re.search(r'github\.com/([^\s/]+)',resume,re.IGNORECASE)

    if not matched_info:
        return {"extracted_info":f"No Github link found in the resume"}
        
    
    username=matched_info.group(1).rstrip('/')

    try:
        response=requests.get(f"{github_api}{username}",timeout=5)

        if response.status_code == 200:
            profile=response.json()
            repos_response=requests.get(f"{github_api}{username}/repos",timeout=5)
            repos=repos_response.json()

            repos_names=[r.get("name","") for r in repos[:5]]

            summary=f"""
            Github verified : {username}
            Bio : {profile.get("bio","not specified")}
            Public Repos : {profile.get("public_repos",0)}
            Recent Repos : {",".join(repos_names)}
            """
            return {"extracted_info": f"\n\n{summary}"}

        else:
            return {"extracted_info": f"\n\nGithub profile for {username} not found or unavailable"}

    except Exception as e:
        return {"extracted_info" : f"Github verification failed : {str(e)}"}
     


def linkedin_node(state: AgentState)-> dict:
    resume=state["resume_text"]

    check=re.search(r'linkedin\.com/in/([^\s/]+)',resume,re.IGNORECASE)

    if not check:
        return {"extracted_info" :"\n\nNo Linkedin account link found"}
    
    slug=check.group(1).rstrip("/")
    return {"extracted_info":f"\n\nLinkedin profile link found : linkedin.com/in/{slug}"}
    

def assess_node(state: AgentState)-> AgentState:
    extracted=state["extracted_info"]
    job_requirements=state["job_requirements"]
    
    prompt=f"""You are a recruitment research agent.
    Based on this candidate information give a fit assessment out of 10 against the job requirements given below:
    candidate info:
    {extracted}

    job requirements:
    {job_requirements}

    CRITICAL RULES:
    - Do not invent details not present above
    - If experience level isn't clear, say so explicitly
    - Do not infer professional reputation or employability 
      from GitHub follower count or stars alone
    - Treat personal projects as valid evidence of skill, 
      especially for early-career candidates
    
    Give a rating out of 10 and 2-3 sentence justifying the assessment
    """
    
    response=llm.invoke(prompt)
    state["final_assessment"]=response.content
    return state

def skip_node(state: AgentState)-> AgentState:
    state["final_assessment"]="Insufficient information to assess the candidate"
    return state

#Routing Logic
def should_assess(state: AgentState)-> str:
    extracted=state["extracted_info"]
    if "Insufficient" in extracted or extracted.strip()=="":
        return "skip"
    return "assess"

#Graph Construction
graph=StateGraph(AgentState)

graph.add_node("extract",extract_node)
graph.add_node("github",github_node)
graph.add_node("linkedin",linkedin_node)
graph.add_node("assess",assess_node)
graph.add_node("skip",skip_node)


graph.set_entry_point("extract")

graph.add_conditional_edges("extract",should_assess,{"assess":"github","skip":"skip"})

graph.add_edge("extract","linkedin")

graph.add_edge("linkedin","assess")

graph.add_edge("github","assess")

graph.add_edge("assess",END)

graph.add_edge("skip",END)

app=graph.compile()

#Main block
if __name__ == "__main__":
    resume_text = """
    Abhinraj
    Final year ECE student.
    Building AI systems independently.
    Skills: Python, LangChain, LangGraph, AI agent development.
    GitHub: github.com/abhinraj23
    LinkedIn: linkedin.com/in/abhinraj-n-a-298952252
    """

    job_requirements = """
    Junior AI Developer needed.
    Requirements: Python, exposure to AI frameworks,
    fresh graduates welcome.
    """

    result = app.invoke({
        "candidate_name": "Abhinraj",
        "resume_text": resume_text,
        "job_requirements": job_requirements,
        "extracted_info": "",
        "final_assessment": ""
    })

    print("EXTRACTED INFO:")
    print(result["extracted_info"])
    print("FINAL ASSESSMENT:")
    print(result["final_assessment"])
