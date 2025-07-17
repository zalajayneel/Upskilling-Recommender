# utils/fetch_courses.py
import requests
import os
import time
from urllib.parse import quote_plus
from collections import Counter

def generate_platform_search_links(skill, platform):
    """Generate Google search links for a specific platform"""
    platform_domains = {
        "coursera": "coursera.org",
        "udemy": "udemy.com",
        "edx": "edx.org",
        "khan-academy": "khanacademy.org"
    }
    
    if platform not in platform_domains:
        return []
    
    domain = platform_domains[platform]
    courses = []
    
    search_variations = [
        f"{skill} course",
        f"{skill} tutorial",
        f"learn {skill}",
        f"{skill} certification"
    ]
    
    for i, variation in enumerate(search_variations, 1):
        search_query = f"site:{domain} {variation}"
        encoded_query = quote_plus(search_query)
        google_search_url = f"https://www.google.com/search?q={encoded_query}"
        
        courses.append({
            "title": f"{skill} - {platform.title()} Search {i}",
            "description": f"Search for '{variation}' on {platform.title()}",
            "url": google_search_url,
            "source": platform,
            "duration": "Search Results",
            "skill": skill,
            "is_search_link": True
        })
    
    print(f"✅ Generated {len(courses)} {platform} search links for '{skill}'")
    return courses

def load_youtube_courses(skill):
    """Fetch specific YouTube videos (direct play links)"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("❌ YouTube API key not configured")
        return []

    search_url = "https://www.googleapis.com/youtube/v3/search"
    
    # Targeted queries to find actual course videos
    search_queries = [
        f"{skill} complete course",
        f"{skill} full tutorial",
        f"learn {skill} step by step"
    ]
    
    videos = []
    
    for query in search_queries:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 3,
            "key": api_key,
            "order": "relevance",
            "videoDuration": "long",
            "videoEmbeddable": "true"
        }

        try:
            response = requests.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get("items", []):
                video_id = item["id"].get("videoId")
                if not video_id:
                    continue
                
                # Create PROPER direct video URL
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                videos.append({
                    "title": item["snippet"].get("title", "").strip(),
                    "description": item["snippet"].get("description", "")[:200] + "...",
                    "url": video_url,  # This is the critical fix
                    "source": "youtube",
                    "duration": "Video Course",
                    "channel": item["snippet"].get("channelTitle", ""),
                    "skill": skill,
                    "is_search_link": False
                })
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ YouTube API error for '{skill}': {e}")
            continue
    
    # Select only the best video (highest ranked by YouTube)
    if videos:
        best_video = videos[0]  # First result is most relevant
        return [best_video]
    if videos:
        print(f"✅ Found YouTube video for '{skill}': {videos[0]['title']} → {videos[0]['url']}")
        return [videos[0]]
    else:
        print(f"❌ No YouTube videos found for '{skill}'")
        return []

    return []

def load_course_data_from_all_sources(skills=None):
    """Load courses from all sources using Google search links and YouTube API"""
    print("🔄 Loading course data from all sources...")
    
    all_courses = []
    
    if skills:
        print(f"📚 Generating course links for skills: {skills}")
        
        for i, skill in enumerate(skills):
            print(f"🔍 Processing skill {i+1}/{len(skills)}: {skill}")
            
            try:
                # Generate platform search links
                for platform in ["coursera", "udemy"]:
                    platform_links = generate_platform_search_links(skill, platform)
                    if platform_links:
                        all_courses.extend(platform_links)
                
                # Get YouTube courses (real API data)
                youtube_courses = load_youtube_courses(skill)
                if youtube_courses:
                    all_courses.extend(youtube_courses)
                
                # Add delay between skills to avoid rate limiting
                if i < len(skills) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error processing skill '{skill}': {e}")
                continue
    
    print(f"✅ Total course links generated: {len(all_courses)}")
    print("📊 Course sources count:", Counter([c.get("source", "unknown") for c in all_courses]))
    
    return all_courses