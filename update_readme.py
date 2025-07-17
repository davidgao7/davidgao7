import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Get the blog feed URL from environment variables
BLOG_FEED_URL = os.getenv('BLOG_FEED_URL')
README_FILE = 'README.md'

if not BLOG_FEED_URL:
    print("Error: BLOG_FEED_URL environment variable is not set.")
    exit(1)

def fetch_and_parse_feed(url):
    """Fetches the RSS feed and parses it."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'xml') # Parse as XML
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching feed from {url}: {e}")
        return None

def generate_blog_posts_markdown(soup, latest_n = 10):
    """Generates Markdown for the latest blog posts with the requested format."""
    if not soup:
        # Changed to return a placeholder message if feed fetching fails
        return "" # Changed from empty string to a message for clarity

    posts_markdown = []
    import heapq

    # Find all 'item' tags in the RSS feed
    for item in soup.find_all('item'):
        print("=======item=======")
        print(item)
        print("=======item=======")
        title_tag = item.find('title')
        link_tag = item.find('link')
        pubdate_tag = item.find('pubDate')

        title = title_tag.text if title_tag else "No Title"
        link = link_tag.text if link_tag else "#"
        print("=====link raw=======")
        print(link)
        print("=====link raw=======")


        # print("==========link========")
        # print(link)
        # print("==========link========")
        pub_date_str = pubdate_tag.text if pubdate_tag else ""

        # Format the date and time as 'YYYY-MM-DD HH:MM:SS'
        formatted_datetime = ""
        try:
            # RSS dates are often in RFC 822 format (e.g., 'Mon, 14 Jul 2025 13:59:09 +0800')
            dt_object = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
            formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            timestamp = dt_object.timestamp()
        except ValueError:
            # Fallback for other date formats or if parsing fails
            print(f"Warning: Could not parse date format '{pub_date_str}'. Using raw string.")
            # formatted_datetime = pub_date_str.split(' ')[0] if ' ' in pub_date_str else pub_date_str # Attempt to get just date if possible
            continue

        markdown_line = f"{formatted_datetime} [{title}]({link})"
        posts_markdown.append((timestamp, markdown_line))

    latest_posts_sorted = heapq.nlargest(latest_n, posts_markdown, key=lambda x: x[0])
    # Extract just the markdown strings
    posts_markdown_lines = [post[1] for post in latest_posts_sorted]

    return "\n\n".join(posts_markdown_lines)

def update_readme(new_content):
    """Updates the README.md file with the new blog post content."""
    try:
        with open(README_FILE, 'r', encoding='utf-8') as f:
            readme_lines = f.readlines()

        start_marker = '<!-- BLOG_POSTS_START -->'
        end_marker = '<!-- BLOG_POSTS_END -->'

        start_index = -1
        end_index = -1

        for i, line in enumerate(readme_lines):
            if start_marker in line:
                start_index = i
            if end_marker in line:
                end_index = i

        if start_index != -1 and end_index != -1 and start_index < end_index:
            # Replace content between markers
            new_readme_lines = (
                readme_lines[:start_index + 1] +
                [new_content + '\n'] + # Add a newline after the content
                readme_lines[end_index:]
            )
            print("Successfully updated README content between markers.")
        else:
            print(f"Warning: Markers '{start_marker}' and '{end_marker}' not found or out of order in {README_FILE}. Appending to end.")
            # This fallback might not be ideal, but it ensures content is added.
            new_readme_lines = readme_lines + [f"\n{start_marker}\n{new_content}\n{end_marker}\n"]

        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_readme_lines)
        print(f"Successfully wrote updated content to {README_FILE}")

    except FileNotFoundError:
        print(f"Error: {README_FILE} not found. Please ensure it exists.")
    except Exception as e:
        print(f"An error occurred while updating {README_FILE}: {e}")

if __name__ == "__main__":
    print(f"Fetching blog posts from: {BLOG_FEED_URL}")
    soup = fetch_and_parse_feed(BLOG_FEED_URL)
    blog_posts_markdown = generate_blog_posts_markdown(soup)
    print("Generated Markdown:\n", blog_posts_markdown)
    update_readme(blog_posts_markdown)
