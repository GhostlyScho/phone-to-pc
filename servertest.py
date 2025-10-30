from flask import Flask, request, jsonify
from openai import OpenAI
import os
import threading
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

servertest = Flask(__name__)

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

import threading
import os
import signal

def schedule_process_exit(delay_seconds: float = 0.5) -> None:
    """Shut down gracefully across different Flask runtimes."""
    def _delayed_exit():
        try:
            # Try to trigger Werkzeug shutdown if available
            from flask import request
            func = request.environ.get("werkzeug.server.shutdown")
            if func:
                func()
                print("✅ Werkzeug server shutting down gracefully...")
            else:
                print("⚠️ Not using Werkzeug, forcing process exit...")
                os.kill(os.getpid(), signal.SIGTERM)
        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")
            os._exit(0)

    threading.Timer(delay_seconds, _delayed_exit).start()

@servertest.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("text", "")
    print("DEBUG: Received text:", repr(user_input))
    # AI response
    lower_input = user_input.lower()
    # graceful shutdown (server-agnostic)
    if lower_input.strip() in ["end", "quit", "exit"]:
        reply1 = "Server shutting down."
        schedule_process_exit(0.5)
        return jsonify({"reply": reply1})

    if "duck mode" in user_input:
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": ("Answer the question but replace all words in your response with 'quack")
                 },
                {"role": "user", "content": user_input}
            ],
        )
        reply1 = response2.choices[0].message.content.strip()
    elif "remember" in lower_input:
        idx = lower_input.find("remember")
        memory_text = user_input[idx + len("remember"):].strip(" :,-\t")
        if memory_text:
            with open("brain.txt", 'a', encoding="utf-8") as af:
                af.write("\n" + memory_text)
            reply1 = "Memory Updated"
        else:
            reply1 = "Nothing to remember. Provide content after 'remember'."

    elif "clear memory cache" in lower_input:
        try:
            with open("brain.txt", 'w', encoding="utf-8") as wf:
                wf.write("")
            reply1 = "Memory Cache Cleared"
        except Exception as e:
            reply1 = f"Failed to clear memory: {e}"
    else:
        try:
            with open("generalparam.txt", 'r', encoding="utf-8") as rf:
                general_prompt = rf.read()
        except FileNotFoundError:
            general_prompt = ""

        try:
            with open("brain.txt", 'r', encoding="utf-8") as rf:
                brain_prompt = rf.read()
        except FileNotFoundError:
            brain_prompt = ""

        system_prompt = f"{general_prompt}\n\n{brain_prompt}".strip()
        response1 = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": (system_prompt)
                 },
                {"role": "user", "content": user_input}
            ],
        )
        reply1 = response1.choices[0].message.content.strip()

    print("DEBUG: Returned text:" + reply1)
    return jsonify({"reply": reply1})
#10.1.67.185
if __name__ == "__main__":
    servertest.run(host="0.0.0.0", port=5050)

#ngrok http 5050


