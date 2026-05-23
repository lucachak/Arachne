import time
from search_builder import SearchBuilder
from click_button import setup_driver, load_env_configurations

conf, _ = load_env_configurations()
driver = setup_driver(conf, headless=True)

urls = SearchBuilder.build_all()
print(f"Target URL: {urls[0]}")
driver.get(urls[0])
time.sleep(8)
driver.save_screenshot('linkedin_search.png')
print("Screenshot saved to linkedin_search.png")
driver.quit()
