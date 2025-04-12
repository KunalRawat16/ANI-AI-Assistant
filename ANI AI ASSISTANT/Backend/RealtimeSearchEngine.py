from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import json  # Import json module for JSONDecodeError


# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve specific environment variables.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqqAPIKey = env_vars.get("GroqqAPIKey")

# Initialize the Groq client.
client = Groq(api_key=GroqqAPIKey)

# Define the system instruction for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


# Load or initialize the chat log from a JSON file, or create an empty one if it doesn't exist.
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []  # Initialize an empty list if the file doesn't exist or is corrupted
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to perform a Google Search and format the results.
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
        
    Answer += "[end]"  # Fixed typo: Answerr -> Answer
    return Answer

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Predefine chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
def Information():
    Current_date_time = datetime.datetime.now()
    day = Current_date_time.strftime("%A")
    date = Current_date_time.strftime("%d")
    month = Current_date_time.strftime("%B")
    year = Current_date_time.strftime("%Y")
    hour = Current_date_time.strftime("%H")
    minute = Current_date_time.strftime("%M")
    second = Current_date_time.strftime("%S")
    data = f"Please use this real-time Information if needed, \n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"  # Fixed typo: date -> data
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages
    
    # Load the chat log from JSON file.
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        messages = []  # Initialize an empty list if the file doesn't exist or is corrupted
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f)
    
    # Append the user's query to the messages list.
    messages.append({"role": "user", "content": f"{prompt}"})
    
    # Add Google search results to the system chatbot messages.
    search_results = GoogleSearch(prompt)
    SystemChatBot.append({"role": "user", "content": search_results})
    
    # Generate a response using the Groq Client.
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )
    
    Answer = ""
    
    # Concatenate response chunks from the streaming output.
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
            
    # Clean up the response.
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})
    
    # Save the updated chat log back to the JSON file.
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)
        
    # Remove the most recent system message from the chatbot conversation.
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

# Main program entry point.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        if prompt.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        r = (RealtimeSearchEngine(prompt))
        print(r)
        