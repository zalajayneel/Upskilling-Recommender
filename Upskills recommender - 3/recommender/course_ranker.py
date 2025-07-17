# recommender/course_ranker.py

from recommender.embedder import get_embedding
from sentence_transformers.util import pytorch_cos_sim
import re

def clean_skill_name(skill):
    """Clean and normalize skill names"""
    if not isinstance(skill, str):
        return str(skill)
    
    # Remove special characters and normalize
    skill = re.sub(r'[^\w\s]', '', skill)
    skill = skill.strip().title()
    return skill

def calculate_course_score(skill, course):
    """Calculate relevance score for a course given a skill"""
    skill_lower = skill.lower()
    title = course.get("title", "").lower()
    description = course.get("description", "").lower()
    
    # 1. Exact skill match in title or description
    exact_match = 0.5 if skill_lower in title else 0.0
    
    # 2. Partial skill match bonus
    partial_match = 0.3 if any(word in title for word in skill_lower.split()) else 0.0
    
    # 3. Source preference (YouTube gets higher score for being real content)
    source = course.get("source", "").lower()
    source_bonus = {
        "youtube": 0.8,      # Real video content
        "coursera": 0.6,     # Search links
        "udemy": 0.6,        # Search links
        "google": 0.4,       # General search
        "edx": 0.5,          # Alternative platform
        "khan-academy": 0.5  # Alternative platform
    }.get(source, 0.4)
    

    # 4. Course type bonus
    type_bonus = 0.0
    if "complete" in title or "full course" in title:
        type_bonus += 0.2
    if "tutorial" in title:
        type_bonus += 0.1
    if "search" in title.lower():
        type_bonus -= 0.1  # Slightly lower for search results
    
    # 5. Skill-specific matching for YouTube content
    if source == "youtube":
        try:
            # Use semantic similarity for YouTube videos (real content)
            skill_embedding = get_embedding(skill)
            course_text = f"{course.get('title', '')} {course.get('description', '')}"
            course_embedding = get_embedding(course_text)
            similarity = pytorch_cos_sim(skill_embedding, course_embedding)[0][0].item()
            semantic_bonus = similarity * 0.3
        except:
            semantic_bonus = 0.0
    else:
        # For search links, use exact matching
        semantic_bonus = 0.2 if skill_lower in course.get("skill", "").lower() else 0.0
    
    final_score = exact_match + partial_match + source_bonus + type_bonus + semantic_bonus
    return max(0.0, min(1.0, final_score))  # Clamp between 0 and 1

def get_best_courses_per_platform(skill, courses):
    """Get the best course from each platform for a skill"""
    platform_best = {
        "coursera": {"score": -1, "course": None},
        "udemy": {"score": -1, "course": None},
        "youtube": {"score": -1, "course": None}
    }
    
    for course in courses:
        source = course.get("source", "").lower()
        if source in platform_best:
            score = calculate_course_score(skill, course)
            if score > platform_best[source]["score"]:
                platform_best[source] = {"score": score, "course": course}
    
    # Prepare final recommendations
    recommendations = []
    for platform in ["coursera", "udemy", "youtube"]:
        if platform_best[platform]["course"]:
            course = platform_best[platform]["course"]
            recommendations.append({
                "title": course["title"],
                "url": course["url"],
                "source": platform,
                "duration": course.get("duration", ""),
                "description": course.get("description", ""),
                "relevance_score": platform_best[platform]["score"]
            })
    
    return recommendations

def rank_all_skills(skills, course_list):
    """Rank courses for all skills with Google search links"""
    print(f"🔄 Ranking courses for {len(skills)} skills...")
    skill_course_map = {}
    
    for skill in skills:
        skill_clean = clean_skill_name(skill)
        print(f"📊 Processing courses for: {skill_clean}")
        
        # Filter courses for this specific skill
        skill_courses = []
        skill_lower = skill_clean.lower()
        
        for course in course_list:
            course_skill = course.get("skill", "").lower()
            title = course.get("title", "").lower()
            description = course.get("description", "").lower()
            
            # Check if course is relevant to this skill
            if (course_skill == skill_lower or 
                skill_lower in title or 
                skill_lower in description or
                any(word in title for word in skill_lower.split())):
                skill_courses.append(course)
        
        # If no skill-specific courses found, this shouldn't happen with our new approach
        if not skill_courses:
            print(f"⚠️ No courses found for '{skill_clean}' - this shouldn't happen!")
            continue
        
        # Get best courses per platform
        best_courses = get_best_courses_per_platform(skill_clean, skill_courses)
        
        # Ensure we have at least one course per platform
        platforms_found = {course["source"] for course in best_courses}
        for platform in ["coursera", "udemy", "youtube"]:
            if platform not in platforms_found:
                # Create a fallback search link
                from urllib.parse import quote_plus
                
                if platform == "coursera":
                    search_query = f"site:coursera.org {skill_clean}"
                    url = f"https://www.google.com/search?q={quote_plus(search_query)}"
                elif platform == "udemy":
                    search_query = f"site:udemy.com {skill_clean}"
                    url = f"https://www.google.com/search?q={quote_plus(search_query)}"
                else:  # youtube
                    url = f"https://www.youtube.com/results?search_query={quote_plus(skill_clean + ' tutorial')}"
                
                best_courses.append({
                    "title": f"Search {skill_clean} on {platform.title()}",
                    "url": url,
                    "source": platform,
                    "duration": "Search Results",
                    "description": f"Find {skill_clean} courses on {platform.title()}",
                    "relevance_score": 0.3
                })
        
        # Sort by relevance score
        best_courses.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        skill_course_map[skill_clean] = best_courses
        
        # Count real vs search results
        real_courses = len([c for c in best_courses if c['relevance_score'] > 0.5])
        search_links = len([c for c in best_courses if c['relevance_score'] <= 0.5])
        print(f"✅ For '{skill_clean}': {real_courses} real courses, {search_links} search links")
    
    return skill_course_map

# === Enhanced scoring for different content types ===
def get_content_type_score(course):
    """Get additional score based on content type"""
    title = course.get("title", "").lower()
    source = course.get("source", "").lower()
    
    score = 0.0
    
    # YouTube content type scoring
    if source == "youtube":
        if "complete" in title or "full course" in title:
            score += 0.3
        elif "tutorial" in title:
            score += 0.2
        elif "crash course" in title:
            score += 0.25
        elif "masterclass" in title:
            score += 0.2
    
    # Search link scoring
    elif "search" in title.lower():
        if "coursera" in title.lower():
            score += 0.15
        elif "udemy" in title.lower():
            score += 0.15
        else:
            score += 0.1
    
    return score

def prioritize_courses_by_type(courses):
    """Prioritize courses by content type and quality"""
    def get_priority(course):
        source = course.get("source", "").lower()
        title = course.get("title", "").lower()
        
        # Priority order: Real YouTube content > Search links > Fallbacks
        if source == "youtube" and "youtube.com/watch" in course.get("url", ""):
            return 3  # Highest priority for real YouTube videos
        elif source in ["coursera", "udemy"] and "google.com/search" in course.get("url", ""):
            return 2  # Medium priority for Google search links
        else:
            return 1  # Lower priority for direct platform links
    
    return sorted(courses, key=get_priority, reverse=True)