from bs4 import BeautifulSoup
with open('linkedin_search.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

for a in soup.find_all('a'):
    href = a.get('href') or ''
    if '/jobs/view/' in href:
        p = a.parent
        print(f"Link: {a.get_text(strip=True)[:50]}")
        print(f"Classes: {a.get('class')}")
        while p and p.name != 'body':
            if p.name in ['li', 'ul']:
                print(f"  Parent {p.name} classes: {p.get('class')}")
            p = p.parent
