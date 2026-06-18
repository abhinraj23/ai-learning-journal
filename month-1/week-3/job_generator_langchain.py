import os
import requests
import json
from pydantic import BaseModel,Field
from typing import List,Optional
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser,PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

#api keys
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
SERPAPI_KEY=os.environ.get("SERPAPI_KEY")

#LLM object creation
llm=ChatGroq(model="llama-3.3-70b-versatile",temperature=0.2,max_tokens=1500)

#pydantic model
class JobDescription(BaseModel):
    job_title: str
    location: str
    experience_required: str
    employment_type: str
    salary_range: Optional[str] = "Competitive"
    responsibilities: List[str] =Field(description="6-8 specific job responsibilities")
    required_skills: List[str] =Field(description="6-8 required skills")
    nice_to_have: List[str] =Field(description="5-7 preffered optional skills")
    qualifications: List[str] =Field(description="3-4 educational or experience qualifications")
    about_role: str =Field(description="2-3 sentence engaging summary of the role")
    benefits: Optional[List[str]] =Field(default=[],description="5-6 employee benefits for this particular job role in career and personal life")


#search on web
def search_job_postings(job_title,location):
    print(f"searching for real world {job_title} job postings in {location}")
    response=requests.get("https://serpapi.com/search",params={"engine":"google_jobs","q":f"{job_title} {location}","api_key":SERPAPI_KEY,"num":5})

    if response.status_code != 200:
        print(f"searching failed : {response.status_code}")
        return []
    
    result=response.json()

    if "jobs_results" not in result:
        print("no jobs found")
    
    jobs=[]
    for job in result["jobs_results"][:5]:
        jobs.append({"title":job.get("title",""),"company":job.get("company_name",""),"location":job.get("location",""),"description":job.get("description","")[-2000:],"highlights":job.get("job_highlights",[])})

    return jobs


#extract patterns
def extract_job_patterns(jobs,retries=3):
    combined=""
    for i,j in enumerate(jobs):
        combined=f"\n\n Job posting: {i+1}\nTitle :{j["title"]}\nCompany :{j["company"]}\nDescription :{j["description"]}\n"

    parser=JsonOutputParser()

    prompt=ChatPromptTemplate.from_messages(["user","""Analyze these real job postings and extract common patterns:

        {job_data}

        Return ONLY a JSON object with this exact structure:
        {{
            "common_responsibilities": ["list of 5-7 common responsibilities"],
            "common_skills": ["list of 5-8 required skills"],
            "nice_to_have": ["list of 3-5 optional skills"],
            "qualifications": ["list of 2-4 common qualifications"],
            "experience_level": "typical experience range as string",
            "benefits":"Benefits of this particular job role...be diverse according to job title"
        }}

        Return ONLY the JSON. No explanation. No markdown...make sure the response is a valid json STRICTLY
        {format_instruction}"""]).partial(format_instruction=parser.get_format_instructions())
        
    
    chain= prompt | llm | parser
    
    for i in range(retries):
        try:
            result=chain.invoke({"job_data":combined})
            return result
        except Exception as e:
            print(f"extraction attempt {i+1} failed : {e}")
            if i==retries-1:
                return None

#Create job postings
def job_description_create(user_input,patterns,retries=3):

    parser=PydanticOutputParser(pydantic_object=JobDescription)
    
    prompt=ChatPromptTemplate.from_messages([("user","""Create a professional Job Description:
    STRICT RULES:
    - every skills in required_skills MUST come from patterns given 
    - every responsibilities should be derviced from patterns below

    User Requirements:
    - Job Title: {title}
    - Locatio: {location}
    - Experience: {experience}
    - Employment Type: {employment_type}
    - Salary Range: {salary_range}

    patterns from real job postings...only use these:
    - Responsibilites: {responsibilities}
    - Requires skills: {skills}
    - Nice To Have: {nice_to_have}
    - Qualifications: {qualifications}
    - benefits: {benefits}

    {format_instructions}
    """
    )]).partial(format_instructions=parser.get_format_instructions())

    chain= prompt | llm | parser
    
    for i in range(retries):
        try:
            result=chain.invoke({"title":user_input["title"],"location":user_input["location"],"experience":user_input["experience"],"employment_type":user_input["employment_type"],"responsibilities":patterns["common_responsibilities"],"skills":patterns["common_skills"],"nice_to_have":patterns["nice_to_have"],"salary_range":user_input["salary_range"],"qualifications":patterns["qualifications"],"benefits":patterns["benefits"]})
            return result
        except Exception as e:
            print(f"Generation attempt {i+1} failed : {e}\nType of error : {type(e).__name__}")
            if i==retries-1:
                return None


#Saving thd generated JD
def save_job_description(jd,filename=None):

    if filename is None:
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        filename=f"{jd.job_title.replace(" ",'_')}_{timestamp}_JD.txt"

    content=f"""
    JOB DESCRIPTION
    {'='*70}

    ROLE            : {jd.job_title}
    Location        : {jd.location}
    Experience      : {jd.experience_required}
    Salary Range    : {jd.salary_range}
    Employment Type : {jd.employment_type}

    ABOUT ROLE
    {"-"*30}

    {jd.about_role}

    RESPONSIBILITIES
    {"-"*30}

    {chr(10).join(f"→ {r}" for r in jd.responsibilities)}

    REQUIRED SKILLS
    {"-"*30}

    {chr(10).join(f'→ {s}' for s in jd.required_skills)}

    NICE TO HAVE
    {"-"*30}

    {chr(10).join(f'• {n}' for n in jd.nice_to_have)}

    QUALIFICATIONS
    {"-"*30}

    {chr(10).join(f'• {q}' for q in jd.qualifications)}

    BENEFITS
    {"-"*30}

    {chr(10).join(f'• {q}' for q in jd.benefits)}

    {"="*70}
        
    Generated by AI Job Description Generator - Langchain Version

    """
    with open(filename,"w",encoding="utf-8") as f:
        f.write(content)
        
    json_filename=filename.replace(".txt",".json")
    with open(json_filename,"w",encoding="utf-8") as f:
        json.dump(jd.model_dump(),f,indent=2)

    print(f"\nJD saved to :{filename}\nJSON saved to :{json_filename}")
    return filename


#main function
def main():
    print(f"\nJOB DESCRIPTION GENERATOR - Langchain Version\n{"-"*50}\n")

    title=input("Job Title : ")
    location=input("\nLocation : ")
    experience=input("\nExperience Required : ")
    employment_type=input("\nEmployment Type (Full time\Part timr\Remote) : ")
    salary_range=input("\nSalary Range : ")

    user_input={
        "title":title,
        "location":location,
        "experience":experience,
        "employment_type":employment_type,
        "salary_range":salary_range
    }

    print("\nSeaching real job postings.....")
    jobs=search_job_postings(title,location)

    if not jobs:
        print("\nNo jobs found,try again with different search terms")
        return
    
    print(f"\nFound {len(jobs)} real world job postings")

    print("\nAnalysing and extracting patterns.....")
    patterns=extract_job_patterns(jobs)

    if not patterns:
        print('\nPattern Extraction failed')
        return
    
    print("\nPattern Extraction Successful")

    print("\nGenerating job description.....")
    jd=job_description_create(user_input,patterns)

    if not jd:
        print("\nGeneration Failed")
        return
    
    filename=save_job_description(jd)

    print(f"\nPREVIEW : \nJob Title : {jd.job_title}\nLocation : {jd.location}\nRequired Skills : {jd.required_skills}\nFull JD saved to : {filename }")

if __name__=="__main__":
    main()

