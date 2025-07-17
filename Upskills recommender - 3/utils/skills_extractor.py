# utils/skills_extractor.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("🔑 GEMINI_API_KEY Loaded:", bool(os.getenv("GEMINI_API_KEY")))

def extract_skills(goal):
    print("🧠 Using Gemini to extract skills for:", goal)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")  # or "gemini-pro" if that's what you used before

        prompt = f"""
You are an expert career assistant.
The user says: "{goal}"
Generate a list of 5 to 7 clean, search-friendly skills or topics they should learn.

✅ Each skill should match common course titles on platforms like Coursera and Udemy
✅ Use short, direct names (e.g., "Python", "Data Science", "Machine Learning")
❌ Do not return grouped skills (like "Programming (Python, Java)")

Return only a **comma-separated list** with no explanation or formatting.
"""

        response = model.generate_content(prompt)
        raw_output = response.text.strip()
        print("✅ Gemini Output:", raw_output)

        skills = [skill.strip().title() for skill in raw_output.split(",") if skill.strip()]
        return skills

    except Exception as e:
        print("❌ Gemini Error:", e)
        return ["Python", "SQL", "Git", "Problem Solving"]  # Fallback list
