from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

app = Flask(__name__)

def validate_url(url):
    """Validate if the URL format is correct"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_emails_from_text(text):
    """Extract email addresses from text using regex"""
    # Regular expression pattern for email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Remove duplicates

def scrape_emails(url):
    """Scrape email addresses from the given URL"""
    try:
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Send GET request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from the webpage
        text_content = soup.get_text()
        
        # Find emails in the text
        emails = extract_emails_from_text(text_content)
        
        # Also check mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        for link in mailto_links:
            email = str(link['href']).replace('mailto:', '').split('?')[0]
            if email and '@' in email:
                emails.append(email)
        
        return list(set(emails))  # Return unique emails
        
    except requests.RequestException as e:
        return {'error': f'Failed to fetch the URL: {str(e)}'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        
        # Validate URL
        if not url:
            return render_template('index.html', error='Please enter a URL')
        
        if not validate_url(url):
            # Add https:// if no protocol specified
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                if not validate_url(url):
                    return render_template('index.html', error='Invalid URL format')
            else:
                return render_template('index.html', error='Invalid URL format')
        
        # Scrape emails
        result = scrape_emails(url)
        
        if isinstance(result, dict) and 'error' in result:
            return render_template('index.html', error=result['error'])
        
        return render_template('index.html', emails=result, url=url)
    
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('index.html', about=True)

if __name__ == '__main__':
    app.run(debug=True)