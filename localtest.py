from flask import Flask, request, jsonify
from openai import OpenAI
import os
import threading
import os
from dotenv import load_dotenv
from openai import OpenAI
app = Flask(__name__)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#test
def delete_text_from_file(file_path, target_text):
    try:
        # Open the file in read mode and read all lines
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Filter out lines containing the target text
        updated_lines = [line for line in lines if target_text not in line]

        # Open the file in write mode and write the updated lines
        with open(file_path, 'w') as file:
            file.writelines(updated_lines)

        print(f"Lines containing '{target_text}' have been removed.")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

@app.route("/ask", methods=["POST"])
def main():
    print("🤖 AI Console Chat (type 'quit' to exit)")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "end"]:
            print("👋 Goodbye!")
            break

        # --- Handle commands ---
        if "duck mode" in user_input:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Answer everything by replacing all words with 'quack'."},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content.strip()

        elif "remember" in user_input:
            # Extract content after the keyword 'remember' and store only that
            lower_input = user_input.lower()
            idx = lower_input.find("remember")
            memory_text = user_input[idx + len("remember"):].strip(" :,-\t")
            if memory_text:
                with open("brain.txt", 'a', encoding="utf-8") as af:
                    af.write("\n" + memory_text)
                reply = "Memory Updated"
            else:
                reply = "Nothing to remember. Please provide content after 'remember'."

        elif "clear memory cache" in user_input:
            # Fully clear the memory file so future prompts reference an empty brain
            try:
                with open("brain.txt", 'w', encoding="utf-8") as wf:
                    wf.write("")
                reply = "Memory Cache Cleared."
            except Exception as e:
                reply = f"Failed to clear memory: {e}"

        elif "from memory" in user_input:
            try:
                with open("brain.txt", 'r', encoding="utf-8") as rf:
                    system_prompt = rf.read()
            except FileNotFoundError:
                system_prompt = ""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content.strip()

        else:
            try:
                with open("generalparam.txt", 'r', encoding="utf-8") as rf:
                    system_prompt = rf.read()
            except FileNotFoundError:
                system_prompt = "You are a helpful assistant."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content.strip()

        print(f"AI: {reply}")
#10.1.67.185
if __name__ == "__main__":
    main()

#ngrok http 5050

