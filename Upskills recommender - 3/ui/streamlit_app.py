# ui/streamlit_app.py
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv()
from utils.env_loader import load_env_variables
from utils.skills_extractor import extract_skills
from utils.fetch_courses import load_course_data_from_all_sources
from recommender.course_ranker import rank_all_skills
from agents.planner_agent import generate_learning_plan
import json

# Load environment variables for APIs
load_env_variables()

st.set_page_config(page_title="Upskilling Agent", layout="wide")
st.title("📘 Upskilling Recommendation Agent")
st.write("Get a personalized learning roadmap based on your career goal.")

# Add some helpful information
with st.expander("ℹ️ How it works"):
    st.write("""
    1. **Enter your career goal** - Describe what you want to become or achieve
    2. **AI extracts skills** - Our system identifies key skills you need to learn
    3. **Course matching** - We find the best courses from Coursera, Udemy, and YouTube
    4. **Learning plan** - Get a structured weekly plan with resources from all platforms
    """)

# Input career goal
goal = st.text_input(
    "🎯 Enter your career goal:", 
    placeholder="e.g., I want to become a data scientist, I want to learn web development, I want to become a machine learning engineer",
    help="Be specific about your goal for better skill extraction"
)

if goal:
    # Step 1: Extract skills
    with st.spinner("🧠 Extracting skills from your goal..."):
        skills = extract_skills(goal)
    
    st.subheader("🛠 Extracted Skills")
    if skills:
        # Display skills as tags
        cols = st.columns(len(skills))
        for i, skill in enumerate(skills):
            with cols[i]:
                st.info(f"**{skill}**")
    else:
        st.error("❌ Could not extract skills. Please try rephrasing your goal.")
        st.stop()

    # Step 2: Fetch and rank courses
    with st.spinner("🔍 Finding the best courses from all platforms..."):
        try:
            all_courses = load_course_data_from_all_sources(skills)
            
            if not all_courses:
                st.error("❌ No courses found. Please check your API keys and try again.")
                st.stop()
            
            recommendations = rank_all_skills(skills, all_courses)
            plan = generate_learning_plan(goal, skills, recommendations)
            
        except Exception as e:
            st.error(f"❌ Error fetching courses: {str(e)}")
            st.stop()

    # Step 3: Display learning plan
    st.subheader("📅 Your Personalized Learning Plan")
    st.info("💡 **Tip:** Click on course titles to open them in a new tab")
    
    for week, data in plan.items():
        st.markdown(f"### 📚 Week {week}: {data['skill']}")
        
        if not data.get('resources'):
            st.warning("⚠️ No resources found for this skill")
            continue
        
        # Create three columns for platforms
        col1, col2, col3 = st.columns(3)
        
        # Define column mapping
        columns = [col1, col2, col3]
        platforms = ["coursera", "udemy", "youtube"]
        platform_colors = {
            "coursera": "#0056D2",
            "udemy": "#EC5252", 
            "youtube": "#FF0000"
        }
        platform_icons = {
            "coursera": "🎓",
            "udemy": "💻",
            "youtube": "🎥"
        }
        
        for idx, platform in enumerate(platforms):
            with columns[idx]:
                # Find course for this platform
                course = next(
                    (c for c in data['resources'] if c.get("source", "").lower() == platform), 
                    None
                )
                
                if course and course.get('url') != "#":
                    # Real course found
                    st.markdown(f"""
                    <div style="border: 2px solid {platform_colors[platform]}; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                        <h4 style="color: {platform_colors[platform]}; margin-bottom: 10px;">
                            {platform_icons[platform]} {platform.title()}
                        </h4>
                        <p style="font-weight: bold; margin-bottom: 5px;">{course['title']}</p>
                        <p style="font-size: 0.9em; color: #666; margin-bottom: 10px;">{course.get('duration', 'Duration not specified')}</p>
                        <a href="{course['url']}" target="_blank" style="
                            background-color: {platform_colors[platform]}; 
                            color: white; 
                            padding: 8px 16px; 
                            text-decoration: none; 
                            border-radius: 5px; 
                            font-size: 0.9em;
                            display: inline-block;
                        ">Start Course →</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show relevance score if available
                    if course.get('relevance_score'):
                        score = course['relevance_score']
                        st.caption(f"Relevance: {score:.2f}/1.0")
                else:
                    # Placeholder
                    st.markdown(f"""
                    <div style="border: 2px dashed #ccc; border-radius: 10px; padding: 15px; margin-bottom: 10px; text-align: center;">
                        <h4 style="color: #999; margin-bottom: 10px;">
                            {platform_icons[platform]} {platform.title()}
                        </h4>
                        <p style="color: #666;">Course coming soon...</p>
                        <p style="font-size: 0.8em; color: #999;">Check back later for updates</p>
                    </div>
                    """, unsafe_allow_html=True)

# Step 4: Export functionality
st.subheader("💾 Export Your Plan")

# Only show Export to JSON
if st.button("📄 Export as JSON", type="secondary"):
    user_data = {
        "goal": goal,
        "skills": skills,
        "learning_plan": plan,
        "generated_at": str(st.session_state.get('timestamp', 'Unknown'))
    }

    json_str = json.dumps(user_data, indent=2)
    st.download_button(
        label="⬇️ Download JSON",
        data=json_str,
        file_name="learning_plan.json",
        mime="application/json"
    )

# Sidebar with project summary
with st.sidebar:
    st.header("📌 Summary")
    st.markdown("""
    ### 🔍 Upskilling Recommendation Agent

    This tool helps users get a **personalized weekly learning roadmap** based on their career goals. It works by:

    - 🧠 Extracting relevant skills using AI (Gemini)
    - 🎯 Matching those skills with courses from **Coursera**, **Udemy**, and **YouTube**
    - 📅 Generating a clear weekly learning plan across platforms
    - 💡 Letting users export the roadmap as a downloadable file

    ---
    Built using **Streamlit**, **Python**, and **AI APIs**.
    """)
