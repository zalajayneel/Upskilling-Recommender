# recommender/course_matcher.py

from sentence_transformers import SentenceTransformer, util

# Load sentence embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    return model.encode(text, convert_to_tensor=True)

def match_courses(skills, courses):
    """
    Match each skill to the most semantically similar course title+description
    """
    recommendations = {}

    for skill in skills:
        skill_embedding = embed_text(skill)
        best_score = -1
        best_course = None

        for course in courses:
            course_text = f"{course.get('title', '')} {course.get('description', '')}"
            course_embedding = embed_text(course_text)
            similarity = util.pytorch_cos_sim(skill_embedding, course_embedding)[0][0].item()

            if similarity > best_score:
                best_score = similarity
                best_course = course

        if best_course:
            recommendations[skill] = {
                "title": best_course.get("title", "Unknown"),
                "url": best_course.get("url", "#")
            }
        else:
            recommendations[skill] = {
                "title": "No matching course found",
                "url": "#"
            }

    return recommendations
