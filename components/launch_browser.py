import time
from components.browser_engine import setup_driver
from components.config_loader import load_env_configurations



class LaunchBrowser:



    @staticmethod
    def run():
        print("Loading configurations...")
        config, credentials = load_env_configurations()
        
        print("Launching browser. Please wait...")
        # Launch without headless mode to allow manual interaction
        driver = setup_driver(config, headless=False)
        
        print("\n✅ Browser is now open!")
        print("👉 You can use this window to log in or solve captchas manually.")
        print("👉 Your session will be automatically saved to the 'bot_profile' folder.")
        print("⚠️ Press Ctrl+C in this terminal when you are finished to close the browser safely.")
        
        try:
            # Keep the script running so the browser stays open
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nClosing browser...")
            try:
                driver.quit()
            except:
                pass
            print("Done.")
