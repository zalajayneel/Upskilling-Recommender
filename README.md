# 🎯 Upskilling Recommendation Agent

An intelligent AI-powered system that creates a personalized weekly **learning roadmap** based on a user's **career goal**. It extracts relevant skills and recommends high-quality courses from **YouTube**, **Coursera**, and **Udemy** — helping users upskill with focus and structure.

---

## 📌 Key Features

- 🧠 **Natural Language Understanding**: Accepts free-text career goals like "I want to become a machine learning engineer"
- 🛠 **Skill Extraction**: Automatically identifies relevant technical or non-technical skills
- 🔗 **Course Collection**: Fetches matching courses using the YouTube API and Google Search links for other platforms
- 📊 **Semantic Ranking**: Uses embeddings to rank courses based on relevance
- 📅 **Learning Plan Generation**: Produces a clean, week-by-week roadmap
- 📥 **Plan Export**: Allows users to download their personalized learning plan in JSON format

---

## 📌 Demo

Try the app here:  
👉 [Streamlit App Link]([https://your-deployment-url.streamlit.app/](https://upskilling-recommender-5yjjgsuf32gfydhjlvnfsh.streamlit.app/))

---

## 🗃️ Folder Structure

upskilling-recommendation-agent/
│
├── ui/
│ └── streamlit_app.py # Main Streamlit app UI
│
├── utils/
│ ├── fetch_courses.py # Course collection logic (YouTube API + search links)
│ ├── skills_extractor.py # Extracts skills from user goals
│ └── env_loader.py # Loads API keys from .env
│
├── recommender/
│ ├── course_ranker.py # Ranks and selects best courses per skill/platform
│ └── embedder.py # Uses Sentence Transformers for similarity
│ └── course_matcher.py #Matches skills to course
├── agents/
│ └── planner_agent.py # Generates the week-wise learning plan
│
├── .env # [DO NOT COMMIT] API keys and environment variables
|
└── README.md # Project documentation


---

## 🔑 Environment Setup

Create a `.env` file in your root directory with the following format:

```env
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
