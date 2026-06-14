import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

API_KEY=os.environ.get("GROQ_API_KEY")
SAVE_FILE="conversations.json"

def load_conversation():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE,'r') as f:
            return json.load(f)
    return []

def save_conversation(messages):
    with open(SAVE_FILE,"w") as f:
        json.dump(messages,f,indent=2)
    print(f"conversation saved to {SAVE_FILE}")

def chat():
    print("Recruitment assistant \nType 'quit' to exit \nType 'clear' to start fresh \n")
    print("-" * 30)


    system_message={"role":"system","content":"""You are a recruitment assistant for a TechRecruit Agency kerala
    Current Open Roles:
    Role:Python Developer 
    Salary:8-12LPA
    Location:Kochi,Hyrid
    Experience:2-4 years
    Skills:Python,Django,RestAPI
    
    Role:Data Analyst
    Salary:6-10LPA
    Location:Remote
    Experience:1 year internship minimum 
    Skills:SQL,Python,Power BI,Excel
    
    answer candidate questions about this roles accurately.
    If asked about something not listed above,say you'll check with the recruitment team """}

    messages=load_conversation()

    if not messages:
        messages=[system_message]
    elif messages[0]["role"] != "system":
        messages.insert(0,system_message)
    

    while True:

        try:
            user_input=input("You : ").strip()

            if user_input.lower()=="quit":
                save_conversation(messages)
                print("Goodbye👋🏻")
                break
            
            if user_input.lower()=="clear":
                messages=[system_message]
                save_conversation(messages)
                print("conversation is cleared")
                continue
            
            if not user_input:
                continue 
            
            messages.append({"role":"user","content":user_input})

            response = requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {API_KEY}"},json={"model": "llama-3.3-70b-versatile","messages": messages,"temperature":0.7,"max_tokens":500})
            
            if response.status_code != 200:
                print(f"API error is {response.status_code}")
                print(response.json())
                continue
            
            reply=response.json()["choices"][0]["message"]["content"]

            messages.append({"role":"assistant","content":reply})

            print (f"\nAssistant: {reply}\n")
        
        except KeyboardInterrupt:
            save_conversation(messages)
            print("\nconversation saved, goodbye")
            break
        
        except Exception as e:
            print(f"error occurred : {e}")
            continue
    
if __name__=="__main__":
    chat()
