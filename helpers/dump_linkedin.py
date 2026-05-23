import time
from search_builder import SearchBuilder
from click_button import setup_driver, load_env_configurations

conf, _ = load_env_configurations()
driver = setup_driver(conf, headless=False)

urls = SearchBuilder.build_all()
print(f"Target URL: {urls[0]}")
driver.get(urls[0])
time.sleep(8) # wait for page to load

with open('linkedin_search.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)

driver.quit()
print("Saved to linkedin_search.html")
