from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Disable TensorFlow oneDNN warnings (optional)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Load environment variable from the .env file
env_vars = dotenv_values(".env")
# print("Loaded environment variables:", env_vars)  # Debug statement

# Retrieve specific environment variables with default values.
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqqAPIKey = env_vars.get("GroqqAPIKey", "")
InputLanguage = env_vars.get("InputLanguage", "auto")  # Default to "auto" for automatic detection

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            recognition.lang = 'en-US';  // Set the language
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + ' ';
            };

            recognition.onend = function() {
                console.log("Speech recognition ended.");
            };

            recognition.start();
            console.log("Speech recognition started.");
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
                console.log("Speech recognition stopped.");
            }
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input Language from the environment variables.
HtmlCode = str(HtmlCode).replace("recognition.lang = 'en-US';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file.
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

# Get the current working directory.
current_dir = os.getcwd()
# Generate the file path for the HTML file.
Link = f"{current_dir}/Data/Voice.html"
# print(f"HTML file path: {Link}")  # Debug statement

# Set Chrome options for the WebDriver.
Chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
Chrome_options.add_argument(f'user-agent={user_agent}')
Chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Bypass permission prompts
Chrome_options.add_argument("--use-fake-device-for-media-stream")  # Use a fake microphone
# Chrome_options.add_argument("--headless=new")  # Comment out or remove this line to disable headless mode
Chrome_options.add_argument("--ignore-certificate-errors")  # Disable SSL verification
Chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless mode
Chrome_options.add_argument("--no-sandbox")  # Disable sandbox for better compatibility

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=Chrome_options)
# print("Browser initialized successfully.")  # Debug statement

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', 'w', encoding='utf-8') as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "what's", "where's", "how's", "can you"]
    
    # Check if the query is a question and add a question mark if necessary.
    if any(word + "" in new_query for word in query_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
            
    return new_query.capitalize()

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(Text):
    print(f"Translating text: {Text}")  # Debug statement
    english_translation = mt.translate(Text, "en", "auto")
    print(f"Translated text: {english_translation}")  # Debug statement
    return english_translation.capitalize()

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    while True:
        try:
            # Open the HTML file in the browser.
            driver.get("file:///" + Link)
            # print("HTML file loaded in the browser.")  # Debug statement
            # Start speech recognition by clicking the start button.
            driver.find_element(by=By.ID, value="start").click()
            
            while True:
                try:
                    # Get the recognized text from the HTML output element.
                    Text = driver.find_element(by=By.ID, value="output").text
                    
                    if Text:
                        # Stop recognition by clicking the stop button.
                        driver.find_element(by=By.ID, value="end").click()
                        
                        # If the input language is English, return the modified query.
                        if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                            return QueryModifier(Text)
                        else:
                            # If the input is not English, translate the text and return it.
                            SetAssistantStatus("Translating..")
                            translated_text = UniversalTranslator(Text)
                            return QueryModifier(translated_text)
                
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(1)  # Wait before retrying
        
        except ConnectionResetError:
            print("Connection reset. Retrying...")
            time.sleep(5)  # Wait before retrying

# Main execution block.
if __name__ == "__main__":
    try:
        while True:
            # Continuously perform speech recognition and print the recognized text.
            Text = SpeechRecognition()
            print(Text)
    except KeyboardInterrupt:
        print("Program stopped by user.")
        driver.quit()  # Close the browser gracefully