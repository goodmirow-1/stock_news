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
WP_URL = os.getenv("WP_URL")  # e.g., https://your-site.com
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    You are a professional financial blogger. Write a blog post for today ({today}).
    
    Topic: {topic}
    
    Context Data:
    {data_context}
    
    Requirements:
    1. Title: Catchy and relevant.
    2. Content: Informative, easy to read, formatted with HTML (use <h2>, <p>, <ul>, <li>).
    3. Tone: Professional yet engaging.
    4. Language: Korean (Hangul).
    5. Length: About 500-800 words.
    
    Output format:
    Title: [Your Title Here]
    Content: [Your HTML Content Here]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse title and content
        title = "Market Update"
        content = text
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("Title:") or line.strip().startswith("제목:"):
                title = line.split(':', 1)[1].strip()
            elif line.strip().startswith("Content:") or line.strip().startswith("내용:"):
                content = "\n".join(lines[i+1:])
                break
                
        return title, content
    except Exception as e:
        print(f"Error generating content: {e}")
        return None, None

def post_to_wordpress(title, content):
    """Posts content to WordPress."""
    print("Posting to WordPress...")
    
    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        print("Error: WordPress credentials missing.")
        return False

    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    
    post_data = {
        "title": title,
        "content": content,
        "status": "publish"  # or 'draft'
    }
    
    try:
        api_url = f"{WP_URL}/wp-json/wp/v2/posts"
        response = requests.post(api_url, headers=headers, json=post_data)
        response.raise_for_status()
        print(f"Successfully posted: {response.json().get('link')}")
        return True
    except Exception as e:
        print(f"Error posting to WordPress: {e}")
        if response:
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

    # Generate Content
    title, content = generate_blog_content(topic, data)
    
    if title and content:
        # Post to WordPress
        post_to_wordpress(title, content)
    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    main()
