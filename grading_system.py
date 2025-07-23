import os
import re
import json
import imaplib
import email
import time
import pandas as pd
import requests
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
# mcp agentic ai
# load_dotenv(find_dotenv(), override=True) 
load_dotenv(find_dotenv()) 

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SERVER = os.getenv("EMAIL_SERVER")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "993"))

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
RESULTS_DIR = BASE_DIR / "results"

TEMP_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE
)

class AssignmentGrader:
    def __init__(self):
        self.results = []
        self.email_pattern = re.compile(r"assignment_([^_]+)_(.+)")
        
    def connect_to_email(self):
        try:
            mail = imaplib.IMAP4_SSL(EMAIL_SERVER, EMAIL_PORT)
            mail.login(EMAIL_USER, EMAIL_PASSWORD)
            return mail
        except Exception as e:
            print(f"Error connecting to email: {e}")
            return None
    
    def fetch_emails(self):
        mail = self.connect_to_email()
        if not mail:
            return
        
        try:
            mail.select('inbox')
            status, email_ids = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("No new emails found")
                return
            
            for e_id in email_ids[0].split():
                self.process_email(mail, e_id)
                
        except Exception as e:
            print(f"Error fetching emails: {e}")
        finally:
            mail.logout()
    
    def process_email(self, mail, email_id):
        try:
            status, email_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return
            
            msg = email.message_from_bytes(email_data[0][1])
            subject = decode_header(msg["Subject"])[0][0]
            
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            match = self.email_pattern.match(subject)
            if not match:
                print(f"Email with subject '{subject}' doesn't match the required format")
                return
            
            assignment_name, student_name = match.groups()
            print(f"Processing assignment '{assignment_name}' from student '{student_name}'")
            
            question_content = None
            solution_content = None
            
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                
                filename = part.get_filename()
                if not filename:
                    continue
                
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode()
                
                if filename == "question.txt":
                    question_content = part.get_payload(decode=True).decode()
                elif filename == "solution.py":
                    solution_content = part.get_payload(decode=True).decode()
            
            if question_content and solution_content:
                grade_result = self.grade_assignment(question_content, solution_content)
                self.results.append({
                    "student_name": student_name,
                    "assignment_name": assignment_name,
                    "grade": grade_result.get("grade", 0),
                    "comment": grade_result.get("comment", "")
                })
                self.save_results()
            else:
                print("Missing question.txt or solution.py in the email")
                
        except Exception as e:
            print(f"Error processing email: {e}")
    
    def grade_assignment(self, question, solution):
        try:
            # Prepare the prompt for the model
            prompt = f"""
            You are an expert programming instructor grading a student's assignment.
            
            Here is the assignment question:
            {question}
            
            Here is the student's solution:
            {solution}
            
            Evaluate this solution and provide:
            1. A grade on a scale from 0-100
            2. A comment explaining the grade, especially if the solution is not correct
            
            Return your evaluation as a JSON object with the following format:
            {{
                "grade": <numeric_grade>,
                "comment": "<your feedback>"
            }}
            
            Only return the JSON object, nothing else.
            """
        
            response = client.chat.completions.create(
                model="deepseek-chat",  # Use deepseek-chat (V3) or deepseek-reasoner (R1)
                messages=[
                    {"role": "system", "content": "You are an expert programming instructor who evaluates code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}  
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # If the response isn't valid JSON, try to extract JSON part
                json_match = re.search(r'{.*}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    print("Error: Could not parse JSON response from API")
                    return {"grade": 0, "comment": "Error processing solution - invalid response format"}
            
            return result
            
        except Exception as e:
            print(f"Error grading assignment: {e}")
            return {"grade": 0, "comment": f"Error during grading: {str(e)}"}
    
    
    def save_results(self):
        if not self.results:
            return
        
        try:
            for result in self.results:
                if 'graded_at' not in result:
                    result['graded_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Group results by assignment name
            assignment_groups = {}
            for result in self.results:
                assignment_name = result['assignment_name']
                if assignment_name not in assignment_groups:
                    assignment_groups[assignment_name] = []
                assignment_groups[assignment_name].append(result)
            
            # Save separate CSV files for each assignment
            for assignment_name, results in assignment_groups.items():
                df = pd.DataFrame(results)
                output_file = RESULTS_DIR / f"{assignment_name}.csv"
                
                # Check if file exists to append or create new
                if output_file.exists():
                    existing_df = pd.read_csv(output_file)
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    # Remove duplicates based on student_name (keeping the latest)
                    combined_df = combined_df.drop_duplicates(subset=['student_name'], keep='last')
                    combined_df.to_csv(output_file, index=False)
                else:
                    df.to_csv(output_file, index=False)
                
                print(f"Results for '{assignment_name}' saved to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def run(self, interval=30):
        print(f"Starting assignment grading system. Checking emails every {interval} seconds.")
        
        try:
            while True:
                self.fetch_emails()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Grading system stopped by user")
            self.save_results()

if __name__ == "__main__":
    grader = AssignmentGrader()
    grader.run()