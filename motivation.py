import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
import os
import requests
import re

# Loading API Key and Project ID from .env
load_dotenv()

API_KEY = os.getenv('IBM_API_KEY')
PROJECT_ID = os.getenv('PROJECT_ID')
REGION = 'us-south'
MODEL_ID ='ibm/granite-3-2-8b-instruct'

def get_iam_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Token Error {response.status_code}: {response.text}")
        return None

def clean_generated_text(generated_text):
    match = re.search(r'["“](.*?)["”]', generated_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return generated_text.strip()

def generate_motivation():
    user_text = user_input.get("1.0", tk.END).strip()
    result_label.config(text="✨ Generating motivation... Please wait ✨", fg="#FF8C00")
    root.update()

    if not user_text:
        result_label.config(text=" Please describe how you're feeling.")
        return

    token = get_iam_token(API_KEY)
    if not token:
        result_label.config(text="Failed to get IBM Token. Check API key or Internet.")
        return

    url = f"https://{REGION}.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-06-01"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "model_id": MODEL_ID,
        "input": f"The user said: '{user_text}'. Give ONLY one motivational quote in double quotes. No explanation. No extra text.",
        "parameters": {
            "decoding_method": "sample",
            "max_new_tokens": 100,
            "temperature": 0.7
        },
        "project_id": PROJECT_ID
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            output = response.json()
            generated_text = output.get('results', [{}])[0].get('generated_text', "No motivation found.")

            cleaned_output = clean_generated_text(generated_text)
            result_label.config(text=cleaned_output, fg="#006400")

        else:
            result_label.config(text=f"API Error {response.status_code}: {response.text}", fg="red")

    except Exception as e:
        result_label.config(text=f"Error: {str(e)}", fg="red")

def copy_to_clipboard():
    motivation = result_label.cget("text")
    root.clipboard_clear()
    root.clipboard_append(motivation)
    messagebox.showinfo("Copied!", "Motivation copied to clipboard!")


root = tk.Tk()
root.title("✨ AI Daily Motivator ✨")
root.geometry("700x600")
root.configure(bg="#F0F8FF") 


tk.Label(root, text=" Tell me how you're feeling :)", 
         font=("Helvetica", 16, "bold"), 
         bg="#F0F8FF").pack(pady=15)

user_input = tk.Text(root, height=6, width=70, font=("Arial", 12), bg="#FAFAFA", bd=2, relief="groove")
user_input.pack(pady=10)

tk.Button(root, text="💬 Get Motivation", command=generate_motivation, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=15, pady=8).pack(pady=10)

result_label = tk.Label(root, text="", wraplength=650, justify="left", font=("Arial", 12), bg="#F0F8FF", fg="#006400")
result_label.pack(pady=10)

tk.Button(root, text="📋 Copy to Clipboard", command=copy_to_clipboard, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5).pack(pady=5)

root.mainloop()
