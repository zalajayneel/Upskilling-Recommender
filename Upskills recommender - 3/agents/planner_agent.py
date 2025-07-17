# agents/planner_agent.py
def generate_learning_plan(goal, skills, recommendations):
    learning_plan = {}
    
    for week, skill in enumerate(skills, 1):
        courses = recommendations.get(skill, [])
        
        # Ensure we have one course per platform
        platform_courses = {
            "coursera": None,
            "udemy": None,
            "youtube": None
        }
        
        for course in courses:
            source = course.get("source", "").lower()
            url = course.get("url", "")
            
            # Only assign if not already filled AND the link is valid
            if (
                source in platform_courses
                and platform_courses[source] is None
                and url.startswith("http")
            ):
                platform_courses[source] = course

        
        # Create final resources list
        resources = []
        for platform in ["coursera", "udemy", "youtube"]:
            if platform_courses[platform]:
                resources.append(platform_courses[platform])
            else:
                resources.append({
                    "title": f"{skill} Course ({platform.title()})",
                    "url": "#",
                    "source": platform,
                    "duration": "Coming soon",
                    "relevance_score": 0.0
                })
        
        learning_plan[week] = {
            "skill": skill,
            "resources": resources
        }
    
    return learning_plan