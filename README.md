# DeepSeek Grader Assistant

A pet project using DeepSeek AI to help professors automate grading.

## 📦 Setup Instructions

1. **Install dependencies**  
   Make sure you have Python installed, then run:

pip install -r requirements.txt


2. **Configure environment variables**  
Create a `.env` file in the project root based on the provided `.env.example`.

## 📧 Email Instructions

The email sent to the professor must include:

- **Subject format**:

assignment_[Assignment_Number]_[Student_Name]


- **Attachments**:
- `question.txt` – the assignment prompt
- `solution.py` – the student’s Python solution

---

## 💡 Example

**Subject**:

assignment_assignment3_JohnDoe


**Attachments**:

- `question.txt`
- `solution.py`

---

## 🧠 About

This project leverages DeepSeek's AI capabilities to evaluate programming assignments automatically, aiming to save time for professors and ensure consistent feedback.
