import re
import httpx
from typing import Dict
from bs4 import BeautifulSoup

def web_fetch(prompt: str) -> Dict[str, str]:
    """
    Processes content from URLs embedded in a prompt.
    """
    # Find all URLs in the prompt using a more robust regex
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prompt)

    if not urls:
        return {"error": "No URLs found in the prompt."}

    all_content = []
    # Use a single client for all requests
    with httpx.Client(follow_redirects=True) as client:
        for url in urls:
            try:
                # Add a reasonable timeout
                response = client.get(url, timeout=10.0)
                response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
                
                # Parse HTML and extract clean text
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                
                # Get text and clean up whitespace
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                clean_text = '\n'.join(line for line in lines if line)

                all_content.append(f"--- Content from {url} ---\n{clean_text}")

            except httpx.HTTPStatusError as e:
                all_content.append(f"--- Error fetching {url} ---\nHTTP Error: {e.response.status_code} {e.response.reason_phrase}")
            except httpx.RequestError as e:
                all_content.append(f"--- Error fetching {url} ---\nAn error occurred while requesting the URL: {e}")
            except Exception as e:
                all_content.append(f"--- Error fetching {url} ---\nAn unexpected error occurred: {e}")

    return {"content": "\n\n".join(all_content)}
