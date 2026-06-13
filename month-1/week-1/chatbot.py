import os
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY=os.environ.get("GROQ_API_KEY")
messages=[{"role":"system","content":"You are an experienced and helpful recruitment assistant"}]

while True:
    user_input=input("You : ")
    if user_input=="exit":
        break
    
    messages.append({"role":"user","content":user_input})

    response = requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {API_KEY}"},json={"model": "llama-3.3-70b-versatile","messages": messages})
    reply=response.json()["choices"][0]["message"]["content"]

    messages.append({"role":"assistant","content":reply})

    print (f"\nAI : {reply}\n")
