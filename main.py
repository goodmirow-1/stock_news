import os
import datetime
import requests
import yfinance as yf
import google.generativeai as genai
from bs4 import BeautifulSoup
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Constants
CATEGORY_US_STOCKS = "미국주식"
CATEGORY_KR_STOCKS = "한국주식"

def get_wp_headers():
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

def get_or_create_category(category_name):
    """Gets category ID by name, or creates it if it doesn't exist."""
    print(f"Checking category: {category_name}...")
    headers = get_wp_headers()
    
    # 1. Search for category
    try:
        search_url = f"{WP_URL}/wp-json/wp/v2/categories?search={category_name}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        categories = response.json()
        
        for cat in categories:
            if cat['name'] == category_name:
                return cat['id']
                
        # 2. Create if not found
        print(f"Creating category: {category_name}...")
        create_url = f"{WP_URL}/wp-json/wp/v2/categories"
        data = {"name": category_name}
        response = requests.post(create_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['id']
        
    except Exception as e:
        print(f"Error managing category {category_name}: {e}")
        return None

def get_or_create_tag(tag_name):
    """Gets tag ID by name, or creates it if it doesn't exist."""
    # Similar logic to categories but for tags
    headers = get_wp_headers()
    try:
        search_url = f"{WP_URL}/wp-json/wp/v2/tags?search={tag_name}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        tags = response.json()
        
        for tag in tags:
            if tag['name'] == tag_name:
                return tag['id']
        
        create_url = f"{WP_URL}/wp-json/wp/v2/tags"
        data = {"name": tag_name}
        response = requests.post(create_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['id']
    except Exception as e:
        print(f"Error managing tag {tag_name}: {e}")
        return None


# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_nasdaq_data():
    """Fetches Nasdaq Composite data for the previous trading day."""
    print("Fetching Nasdaq data...")
    nasdaq = yf.Ticker("^IXIC")
    # Get recent history (last 5 days to ensure we get the previous trading day)
    hist = nasdaq.history(period="5d")
    
    if hist.empty:
        return None
        
    # Get the last row (most recent trading day)
    last_day = hist.iloc[-1]
    prev_day = hist.iloc[-2] if len(hist) > 1 else last_day # Compare with day before if possible
    
    change = last_day['Close'] - prev_day['Close']
    change_percent = (change / prev_day['Close']) * 100
    
    data = {
        "date": last_day.name.strftime('%Y-%m-%d'),
        "close": round(last_day['Close'], 2),
        "open": round(last_day['Open'], 2),
        "high": round(last_day['High'], 2),
        "low": round(last_day['Low'], 2),
        "volume": last_day['Volume'],
        "change": round(change, 2),
        "change_percent": round(change_percent, 2)
    }
    return data

def get_google_finance_news():
    """Scrapes top news from Google Finance."""
    print("Fetching Google Finance news...")
    url = "https://www.google.com/finance"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This selector is based on common Google Finance structures, but might change.
        # We look for news items.
        news_items = []
        
        # Try to find news headlines (often in div with specific classes or just look for text)
        # A generic approach for "Top Stories" or "Market News"
        # Google Finance often puts news in 'div.Yfwt5' or similar. 
        # Let's try to find elements that look like news headlines.
        
        # Fallback: Search for specific news sections
        articles = soup.find_all('div', class_='yY3Lee') # Common class for news item container
        if not articles:
             articles = soup.find_all('div', class_='F2KAFc') # Another potential class
             
        for article in articles[:5]: # Get top 5
            title_el = article.find('div', class_='Yfwt5')
            if title_el:
                title = title_el.get_text()
                link_el = article.find('a')
                link = link_el['href'] if link_el else "#"
                if link.startswith('./'):
                    link = "https://www.google.com/finance" + link[1:]
                elif link.startswith('/'):
                    link = "https://www.google.com" + link
                
                news_items.append(f"- {title} ({link})")
        
        if not news_items:
            # Fallback if specific classes fail: Get text from 'News' section if identifiable
            # Or just return a generic message for AI to handle
            return "Could not scrape specific headlines. Please generate a general market overview based on recent global financial events."
            
        return "\n".join(news_items)
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return "Error fetching news."

def generate_blog_content(topic, data_context):
    """Generates blog post content using Gemini."""
    print(f"Generating content for: {topic}...")
    
    if not GEMINI_API_KEY:
        return "Error: Gemini API Key not found.", "Error"

    model = genai.GenerativeModel('gemini-flash-latest')
    
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    prompt = f"""
    You are a professional financial analyst and SEO expert. Write a high-quality blog post for today ({today}).
    
    Topic: {topic}
    
    Context Data:
    {data_context}
    
    Requirements:
    1. **Structure**:
       - **Title**: Catchy, SEO-optimized, includes key tickers if applicable.
       - **Introduction**: Hook the reader, summarize the market mood.
       - **Key Takeaways**: Bullet points of the most important numbers or events.
       - **Detailed Analysis**: Use <h2> and <h3> headers. Break down the data.
       - **Conclusion**: Summary and future outlook.
    2. **Formatting**: Use HTML tags (<h2>, <h3>, <p>, <ul>, <li>, <strong>).
    3. **SEO**:
       - Generate a **Meta Description** (150-160 characters).
       - Generate 3-5 relevant **Tags** (keywords).
    4. **Tone**: Professional, insightful, yet accessible.
    5. **Language**: Korean (Hangul).
    6. **Encoding**: Ensure output is properly JSON formatted.
    
    Output format: JSON
    {{
        "title": "Your Title Here",
        "content": "Your HTML Content Here (do not include <html> or <body> tags, just the inner content)",
        "meta_description": "Your meta description here",
        "tags": ["tag1", "tag2", "tag3"]
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        import json
        result = json.loads(response.text)
        
        return result
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

def post_to_wordpress(post_data_dict):
    """Posts content to WordPress with categories and tags."""
    print("Posting to WordPress...")
    
    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        print("Error: WordPress credentials missing.")
        return False

    headers = get_wp_headers()
    
    # Prepare tags
    tag_ids = []
    if 'tags' in post_data_dict:
        for tag_name in post_data_dict['tags']:
            tid = get_or_create_tag(tag_name)
            if tid:
                tag_ids.append(tid)
    
    wp_post_data = {
        "title": post_data_dict.get('title'),
        "content": post_data_dict.get('content'),
        "excerpt": post_data_dict.get('meta_description'),
        "status": "publish",
        "categories": post_data_dict.get('category_ids', []),
        "tags": tag_ids
    }
    
    try:
        api_url = f"{WP_URL}/wp-json/wp/v2/posts"
        response = requests.post(api_url, headers=headers, json=wp_post_data)
        response.raise_for_status()
        print(f"Successfully posted: {response.json().get('link')}")
        return True
    except Exception as e:
        print(f"Error posting to WordPress: {e}")
        if 'response' in locals() and response:
            print(f"Response: {response.text}")
        return False

def main():
    print(f"Starting automation script at {datetime.datetime.now()}")
    
    # Check day of the week
    # Monday=0, Sunday=6
    weekday = datetime.datetime.now().weekday()
    
    # User rule: Sunday (6) and Monday (0) -> Google Finance News
    # Tuesday (1) to Saturday (5) -> Nasdaq Data (from previous trading day)
    
    if weekday in [6, 0]:
        # Sunday or Monday
        mode = "NEWS"
        print("Mode: Google Finance News")
        data = get_google_finance_news()
        topic = "Global Financial Market News & Updates"
    else:
        # Tuesday to Saturday
        mode = "MARKET"
        print("Mode: Nasdaq Market Data")
        data = get_nasdaq_data()
        if data:
            topic = f"Nasdaq Market Review ({data['date']})"
            data_context = f"""
            Date: {data['date']}
            Close: {data['close']}
            Open: {data['open']}
            High: {data['high']}
            Low: {data['low']}
            Change: {data['change']} ({data['change_percent']}%)
            """
            data = data_context # Reassign for prompt
        else:
            print("Failed to fetch Nasdaq data.")
            return

    if not data:
        print("No data collected. Exiting.")
        return

    # Prepare Category
    category_id = None
    if mode == "MARKET":
        category_id = get_or_create_category(CATEGORY_US_STOCKS)
    elif mode == "NEWS":
        # For now, put global news in US stocks or both? Let's default to US for now as it's global/US centric
        category_id = get_or_create_category(CATEGORY_US_STOCKS)
        
    # Ensure "Korean Stocks" category exists for future use
    get_or_create_category(CATEGORY_KR_STOCKS)

    # Generate Content
    generated_data = generate_blog_content(topic, data)
    
    if generated_data:
        # Add category to data
        if category_id:
            generated_data['category_ids'] = [category_id]
            
        # Post to WordPress
        post_to_wordpress(generated_data)
    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    main()
