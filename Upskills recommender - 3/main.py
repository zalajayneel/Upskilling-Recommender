# main.py
import os
from dotenv import load_dotenv
load_dotenv()  # ✅ load the .env file early

from agents.planner_agent import generate_learning_plan
from recommender.course_matcher import match_courses
from utils.fetch_courses import load_course_data_from_all_sources
from utils.skills_extractor import extract_skills
import json


# Step 1: Get user goal
def get_user_goal():
    print("Welcome to the Upskilling Recommendation Agent!")
    goal = input("\nEnter your career goal (e.g., 'I want to become a data scientist'): ")
    return goal

# Step 2: Generate skill roadmap from goal
def get_skills_from_goal(goal):
    skills = extract_skills(goal)
    print(f"\nIdentified key skills: {skills}")
    return skills

# Step 3: Match courses to skills
def get_course_recommendations(skills):
    course_data = load_course_data_from_all_sources(skills)
    recommendations = match_courses(skills, course_data)
    return recommendations

# Step 4: Display final learning plan
def show_learning_plan(goal, skills, recommendations):
    plan = generate_learning_plan(goal, skills, recommendations)
    print("\n=== Personalized Learning Plan ===")
    for week, content in plan.items():
        print(f"\nWeek {week}:")
        for skill, course in content.items():
            print(f"- Learn {skill} via: {course['title']} ({course['url']})")

if __name__ == "__main__":
    user_goal = get_user_goal()
    skills = get_skills_from_goal(user_goal)
    # Flatten and sanitize skill list
    flattened_skills = []
    for s in skills:
        if isinstance(s, list):
            flattened_skills.extend(s)
        elif isinstance(s, str):
            flattened_skills.append(s.strip().title())

    # Remove empty or duplicate values
    skills = list(dict.fromkeys([s for s in flattened_skills if s]))
    print("✅ Cleaned Skills:", skills)

    recommendations = get_course_recommendations(skills)
    show_learning_plan(user_goal, skills, recommendations)
