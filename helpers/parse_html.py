from bs4 import BeautifulSoup

def analyze(filename):
    print(f"\n--- Analyzing {filename} ---")
    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # check old selectors
    print("Checking old list container:")
    old_list = soup.select("ul.scaffold-layout__list-container, .jobs-search-results-list")
    print(f"  Found {len(old_list)} elements")
    
    print("\nChecking old card container:")
    old_cards = soup.select("li.jobs-search-results__list-item, div.job-card-container")
    print(f"  Found {len(old_cards)} elements")

    # If old ones failed, let's find data-job-id or data-occludable-job-id
    cards = soup.find_all(lambda tag: tag.has_attr('data-job-id') or tag.has_attr('data-occludable-job-id') or tag.name == 'li' and 'job' in "".join(tag.get('class', [])).lower())
    print(f"\nFound {len(cards)} elements that might be job cards.")
    if cards:
        print(f"  Sample card classes: {cards[0].get('class')}")
        print(f"  Sample card attrs: {list(cards[0].attrs.keys())}")
        
    # How about links to /jobs/view/
    import re
    links = soup.find_all('a', href=re.compile(r'/jobs/view/'))
    print(f"\nFound {len(links)} links to job views.")
    if links:
        for i, a in enumerate(links[:2]):
            print(f"  Link {i} text: {a.get_text(strip=True)[:40]}")
            print(f"  Link {i} classes: {a.get('class')}")
            # print its parents until a list item or max 3 levels
            p = a.parent
            for level in range(4):
                if p:
                    print(f"    Parent {level} <{p.name}> class: {p.get('class')} id: {p.get('id')} data: {[k for k in p.attrs if k.startswith('data-')]}")
                    p = p.parent

analyze('linkedin_search.html')
