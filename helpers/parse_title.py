from bs4 import BeautifulSoup
with open('linkedin_search.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
print(soup.title.string if soup.title else "No Title")
# check for "No results" text
if soup.find(text=lambda t: t and 'No matching jobs found' in t):
    print("Found 'No matching jobs found'")
# find how many elements with <a> have "href" containing "/jobs/"
links = soup.find_all('a')
jobs_links = [l for l in links if l.get('href') and '/jobs/' in l.get('href')]
print(f"Total /jobs/ links: {len(jobs_links)}")
