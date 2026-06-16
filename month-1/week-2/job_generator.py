#imports
from dotenv import load_dotenv
import os
import requests
import json
from typing import List,Optional
from pydantic import BaseModel
from datetime import datetime

load_dotenv()

#api keys loading
SERPAPI_KEY=os.environ.get("SERPAPI_KEY")
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")


#pydantic model for validation
class JobDescription(BaseModel):
    job_title: str
    location: str
    experience_required: str
    employment_type: str
    salary_range: Optional[str] = "Competitive"
    
    responsibilities: List[str]
    required_skills: List[str]
    nice_to_have: Optional[List[str]]=[]
    qualifications: List[str]
    
    about_role: str
    benefits: Optional[List[str]] = []


#Helper function
def call_llm(prompt,temperature=0.3,max_tokens=1000):
    response=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {GROQ_API_KEY}"},json={"model": "llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"temperature":temperature,"max_tokens":max_tokens})

    if response.status_code != 200:
        print(f"API error :{response.status_code}")
        print(response.json())
        return None

    return response.json()["choices"][0]["message"]["content"]


#parses json response
def parse_json_response(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        print(f"json parsing failed: {e}")
        print(f"Raw LLM output was: {data}")
        return None


#searches jobs on web and return list of structured job postings
def search_job_postings(job_title,location):

    print(f"searching for {job_title} in {location}")

    response=requests.get("https://serpapi.com/search",params={"engine":"google_jobs","q":f"{job_title} {location}","api_key":SERPAPI_KEY,"num":5})

    if response.status_code != 200:
        print(f"response failed: {response.status_code}")
        return []
    
    data=response.json()

    if "jobs_results" not in data:
        print("No job results found!")
        print(data.keys())
        return []
    
    jobs=[]

    for job in data["jobs_results"][:5]:
        jobs.append({"title":job.get("title",""),"company":job.get("company_name",""),"description":job.get("description","")[-2000:],"location":job.get("location",""),"highlights":job.get("job_highlights",[])})

    return jobs


#Extractes patterns using LLM
def extract_job_pattern(jobs):
    combined=""
    for i,j in enumerate(jobs):
        combined+=f"\n\n Job posting {i+1}\n"
        combined+=f"\n Title: {j["title"]}\nCompany: {j["company"]}\nDescription: {j["description"][:1000]}\n"
    
    prompt=f"""Analyse the real world job postings delimited by angle brackets and extract common patterns:
    <{combined}>
    return only a JSON object with the exact structure:
    {{
        "common_responsibilities":["list of 5-7 common responsibilities"],
        "mcommon_skills":["list of 5-8 required skills"],
        "nice_to_have":["list of 3-5 optional skills"],
        "qualifications":["list of 2-4 common qualifications"].
        "experience_level":"typical experience level as string"
    }}
    return ONLY the JSON object,no explanation,no markdown,only json object
    STRICT rule:
    - do not return json code fences like triple and double quotes
    - the response should start with a opening curly brace and should end with closing curly brace like a valid json object
    - only return valid JSON object 
    """

    raw_text=call_llm(prompt,temperature=0.3,max_tokens=1000)

    if not raw_text:
        return None
    
    return parse_json_response(raw_text)


#create a job description with patterns and user input
def job_description_generate(user_input,patterns):
    
    prompt=f"""Create a professional job description using this information:

    STRICT RULES:

	- Every skill in required_skills MUST come from the patterns below
	- Every responsibility MUST be derived from the patterns below  
	- Do NOT add anything from general knowledge
	- Only use what is explicitly in the provided patterns

    User requirements:
    
	- Job title:{user_input["title"]}
    - Location:{user_input["location"]}
    - Experience:{user_input["experience"]}
	- Employment type:{user_input["employment_type"]}
    - Salary: {user_input["salary_range"]}

	common patterns from real job postings...ONLY use these:

    - Responsibilities:{patterns["common_responsibilities"]}
    - Required skills:{patterns["common_skills"]}
    - Nice to have:{patterns["nice_to_have"]}
    - Qualifications:{patterns["qualifications"]}

    return ONLY a JSON object with the exact given structure:

    {{
        "job_title":"{user_input["title"]}",
        "location":"{user_input["location"]}",
        "experience_required":"{user_input["experience"]}",
        "employment_type":"{user_input["employment_type"]}",
        "salary_range":"{user_input["salary_range"]}", 
        "responsibilities":["list of 6-8 Responsibilities"],
        "required_skills":["list of 6-8 Required skills"],
        "nice_to_have":["list of 3-5 optional skills"],
        "qualifications":["list of 3-5 qualifications"],
        "about_role":"2-3 sentences about the job role",
        "benefits":["list of 3-4 job benefits"]
    }}
    Return only the JSON using patterns and user requirements,no explanation,no markdown.
    STRICT rules:
    - do not return json fences with triple or double quotes
    - the response should start with open curly brace and end with closing curly brace
    - only return valid json object
    """
    raw_text=call_llm(prompt,temperature=0.2,max_tokens=1500)

    if not raw_text:
        return None

    jd_data=parse_json_response(raw_text)

    if not jd_data:
        return None

    try:
        validated_data=JobDescription(**jd_data)
        return validated_data

    except Exception as e:
        print(f"pydantic validation failed: {e}")
        print("Retrying with correction prompt...")

        correction_prompt=f"""Your previous json response failed validation:
        Error: {e}

        Original JSON thaf failed:
        {jd_data }

        Fix the JSON so it matches this exact structure:
        {{
            "job_title": "{user_input['title']}",
            "location": "{user_input['location']}",
            "experience_required": "{user_input['experience']}",
            "employment_type": "{user_input['employment_type']}",
            "salary_range": "{user_input["salary_range"]}"
            "responsibilities": ["derived strictly from patterns above"],
            "required_skills": ["derived strictly from patterns above"],
            "nice_to_have": ["derived strictly from patterns above"],
            "qualifications": ["derived strictly from patterns above"],
            "about_role": "2-3 sentences about the role",
            "benefits": ["list of 4-5 reasonable benefits"]
            }}
        return ONLY the JSON,no explanation,no markdown.

        """
    retry_text=call_llm(correction_prompt,temperature=0.1,max_tokens=1500)

    if not retry_text:
        return None
    
    retry_data=parse_json_response(retry_data)

    if not retry_data:
        return None
    
    try:
        return JobDescription(**retry_data)
    except Exception as e2:
        print(f"retry also failed as : {e2}")
        return None

#save formatted job description to a text file
def save_jd(jd,filename=None):

    if filename is None:
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        filename=f"{jd.job_title.replace(" ","_")}_{timestamp}_JD.txt"

    content=f"""
    JOB DESCRIPTION
    {"="*50}

    ROLE : {jd.job_title}
    LOCATION : {jd.location}
    EXPERIENCE : {jd.experience_required}
    EMPLOYMENT TYPE : {jd.employment_type}
    SALARY : {jd.salary_range}

    ABOUT THE ROLE
    {"-"*30}
    {jd.about_role}

    RESPONSIBILITIES
    {"-"*30}
    {chr(10).join(f"• {r}" for r in jd.responsibilities)}

    REQUIRED SKILLS
    {"-"*30}
    {chr(10).join(f'• {s}' for s in jd.required_skills)}

    NICE TO HAVE
    {"-"*30}
    {chr(10).join(f'• {n}' for n in jd.nice_to_have)}

    QUALIFICATIONS
    {"-"*30}
    {chr(10).join(f'• {q}' for q in jd.qualifications)}

    BENEFITS
    {"-"*30}
    {chr(10).join(f'• {b}' for b in jd.benefits)}

    {"-"*50}
    Generated by AI Job Description Generator

    """
    with open(filename,'w',encoding="utf-8") as f:
        f.write(content)
    
    #also saving json for automation
    json_filename=filename.replace(".txt",".json")
    with open(json_filename,"w",encoding="utf-8") as f:
        json.dump(jd.model_dump(),f,indent=2)
    
    
    print(f"Text saved to filename : {filename}")
    print(f"Json saved to : {json_filename}")
    return filename



#main function
def main():
    
    print("AI Job Description Generator")
    print("="*40)

	#input section
    title=input("Job title: ")
    location=input("\nLocation: ")
    experience=input("\nExperience Required: ")
    employment_type=input("\nSpecify type of employement(full-time/part-time/contract): ")
    salary_range=input("\nSalary range: ")

    user_input={
        "title":title,
        "location":location,
        "experience":experience,
        "employment_type":employment_type,
        "salary_range":salary_range
    }

    #search on web
    print("searching real job postings...")
    jobs=search_job_postings(title,location)

    if not jobs:
        print("No jobs found.try again with different search terms")
        return 
    
    print(f"\nFound {len(jobs)} real world jobs")

    #pattern extraction
    print("\nAnalysing patterns....")
    patterns=extract_job_pattern(jobs)

    if not patterns:
        print("\nAnalysis failed")
        return
    
    print("\nAnalysis successful")

    #JD generation
    print("\nGenerating job description....")
    jd=job_description_generate(user_input,patterns)

    if not jd:
        print("\nGeneration failed")
        return
    
    #saving
    filename=save_jd(jd)

    print("\nPREVIEW : ")
    print(f"\nTitle :{jd.job_title}\nLocation :{jd.location}\nExperience :{jd.experience_required}\nSkills :{jd.required_skills}\nFull JD saved to: {filename}")


if __name__=="__main__":
    main()