import time
import random
import re
import getpass
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

from components.config_loader import ScraperConfig, UserCredentials, load_env_configurations
from components.browser_engine import setup_driver, highlight_element, close_possible_popups, Colors, print_banner

def login_to_catho(driver, credentials: UserCredentials, config: ScraperConfig) -> bool:
    wait = WebDriverWait(driver, 15)
    
    try:
        home_url = "https://www.catho.com.br/"
        print(f"\n[Login Process] Navigating to Catho homepage: {home_url}")
        driver.get(home_url)
        
        print("  -> Checking if already logged in via persistent session...")
        try:
            time.sleep(1.5)
            if driver.find_elements(By.CLASS_NAME, "i_signout") or \
               driver.find_elements(By.CLASS_NAME, "avatar") or \
               driver.find_elements(By.CSS_SELECTOR, "a.user-avatar") or \
               ("signin" not in driver.current_url.lower() and "login" not in driver.current_url.lower() and len(driver.find_elements(By.ID, "signin")) == 0):
                print("  [SUCCESS] Already logged in via persistent Chrome session! Skipping login flow.")
                return True
        except Exception:
            pass
        
        # Step 1: cookies
        print("  -> Checking for Cookie Consent Banner...")
        cookie_button_selectors = [
            (By.CSS_SELECTOR, "button.acceptAll"),
            (By.XPATH, "//button[contains(text(), 'Aceitar todos os cookies')]"),
            (By.XPATH, "//button[contains(@class, 'acceptAll')]")
        ]
        
        cookie_accepted = False
        for by, selector in cookie_button_selectors:
            try:
                cookie_btn = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((by, selector))
                )
                highlight_element(driver, cookie_btn, config, color="#25D366")
                cookie_btn.click()
                print("  [COOKIES] Clicked 'Aceitar todos os cookies' successfully.")
                cookie_accepted = True
                break
            except Exception:
                continue
                
        if not cookie_accepted:
            print("  [COOKIES] Cookie consent banner not found or already accepted. Proceeding...")
            
        time.sleep(1.0)
        
        print("  -> Locating 'Entrar' link to navigate to sign-in page...")
        signin_link_selectors = [
            (By.ID, "signin"),
            (By.CSS_SELECTOR, "a#signin"),
            (By.CSS_SELECTOR, 'a[data-event="entrar_link"]'),
            (By.XPATH, "//a[contains(@href, '/signin/')]"),
            (By.XPATH, "//a[text()='Entrar']")
        ]
        
        signin_clicked = False
        for by, selector in signin_link_selectors:
            try:
                signin_link = wait.until(EC.element_to_be_clickable((by, selector)))
                highlight_element(driver, signin_link, config, color="#3624d6")
                signin_link.click()
                print("  -> Clicked 'Entrar' link successfully.")
                signin_clicked = True
                break
            except Exception:
                continue
                
        if not signin_clicked:
            print("  [WARN] Could not click 'Entrar' link. Navigating directly to sign-in URL...")
            driver.get("https://www.catho.com.br/signin/")
        else:
            try:
                wait.until(EC.url_contains("/signin/"))
                print(f"  -> Redirection successful. Current URL: {driver.current_url}")
            except Exception:
                print(f"  [INFO] URL did not change immediately. Current URL: {driver.current_url}")
                
        time.sleep(2.0) 
    
        # Inject email/username and password
        email_selectors = [
            (By.NAME, "email"),
            (By.ID, "login"),
            (By.NAME, "login"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[name='email']"),
            (By.XPATH, "//input[@placeholder='Ex: Raquel@gmail.com']"),
            (By.XPATH, "//input[contains(@placeholder, 'E-mail')]")
        ]
        
        email_field = None
        for by, selector in email_selectors:
            try:
                email_field = wait.until(EC.element_to_be_clickable((by, selector)))
                break
            except Exception:
                continue
                
        if not email_field:
            raise Exception("Could not find the email/login input field.")
            
        print("  -> Entering email/CPF...")
        highlight_element(driver, email_field, config, color="#25D366" if config.TEST_MODE else "#3624d6")
        email_field.clear()
        email_field.send_keys(credentials.email)
        
        password_selectors = [
            (By.NAME, "password"),
            (By.ID, "password"),
            (By.ID, "senha"),
            (By.NAME, "senha"),
            (By.CSS_SELECTOR, "input[type='password']")
        ]
        
        password_field = None
        for by, selector in password_selectors:
            try:
                password_field = driver.find_element(by, selector)
                if password_field.is_displayed():
                    break
                else:
                    password_field = None
            except Exception:
                continue
                
        if not password_field:
            print("  -> Password field not immediately visible. Attempting multi-step 'Avançar' flow...")
            continue_selectors = [
                (By.XPATH, "//button[contains(text(), 'Avançar')]"),
                (By.XPATH, "//button[contains(text(), 'Continuar')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.CSS_SELECTOR, "button.button_primary")
            ]
            
            continue_btn = None
            for by, selector in continue_selectors:
                try:
                    continue_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    break
                except Exception:
                    continue
                    
            if not continue_btn:
                raise Exception("Could not locate the 'Avançar/Continuar' button.")
                
            continue_btn.click()
            print("  -> Clicked 'Avançar'. Waiting for password field to load...")
            time.sleep(1.5)
            
            for by, selector in password_selectors:
                try:
                    password_field = wait.until(EC.visibility_of_element_located((by, selector)))
                    break
                except Exception:
                    continue
                    
        if not password_field:
            raise Exception("Could not locate the password field.")
            
        print("  -> Entering password...")
        highlight_element(driver, password_field, config, color="#25D366" if config.TEST_MODE else "#3624d6")
        password_field.clear()
        password_field.send_keys(credentials.password)
        
        submit_selectors = [
            (By.XPATH, "//button[text()='Entrar']"),
            (By.XPATH, "//button[contains(text(), 'Entrar')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']")
        ]
        
        submit_btn = None
        for by, selector in submit_selectors:
            try:
                submit_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                break
            except Exception:
                continue
                
        if not submit_btn:
            raise Exception("Could not locate the submit/login button.")
            
        print("  -> Clicking final 'Entrar' button...")
        highlight_element(driver, submit_btn, config, color="#25D366" if config.TEST_MODE else "#3624d6")
        
        if config.TEST_MODE:
            time.sleep(2.0)
            
        submit_btn.click()
        print("  -> Login form submitted successfully!")
        
        if config.TEST_MODE:
            print("  [TEST MODE] Successfully simulated login flow locally. Settle delay...")
            time.sleep(3.0)
            return True
            
        print("\n[Security Check] Monitoring for CAPTCHAs or manual verifications...")
        print("  >> We ARE SO FUCKED UP...")
        print("  >> If a CAPTCHA or 'Prove que você é humano' check appears, please solve it manually in the Chrome window!")
        print("  >> The script will monitor the session and proceed once successful login is detected.")
        
        success = False
        start_time = time.time()
        while time.time() - start_time < 45:
            current_url = driver.current_url.lower()
            if "login" not in current_url and "auth" not in current_url and "signin" not in current_url:
                print("  [SUCCESS] Successfully logged in! Redirected away from login page.")
                success = True
                break
            
            try:
                if driver.find_elements(By.CLASS_NAME, "i_signout") or driver.find_elements(By.CLASS_NAME, "avatar"):
                    print("  [SUCCESS] Successfully logged in! Candidate profile indicators found.")
                    success = True
                    break
            except Exception:
                pass
                
            time.sleep(1.5)
            
        if not success:
            print("\n  [INFO] Timeout waiting for automatic login redirection.")
            print("  Continuing to the scraper. If login was successful, it will run correctly.")
        else:
            time.sleep(2.0)
            
        return True
            
    except Exception as e:
        print(f"\n[Login Failed] Could not automate the login flow: {e}")
        print("Continuing directly to the scraping page in case you are already logged in or want to log in manually.")
        return False

def contains_senior_terms(text: str, config: ScraperConfig) -> bool:
    joined = "|".join([re.escape(term) for term in config.SENIOR_TERMS])
    pattern = re.compile(rf'\b({joined})\b', re.IGNORECASE)
    return bool(pattern.search(text))

def process_page_buttons(driver, config: ScraperConfig) -> int:
    close_possible_popups(driver, config)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    initial_cards = driver.find_elements(By.XPATH, "//li[@data-offer-item]")
    total_cards_count = len(initial_cards)
    
    total_valid = 0
    card_ids = []
    
    for card in initial_cards:
        try:
            c_id = card.get_attribute("data-offer-item")
            if c_id:
                card_ids.append(c_id)
        except Exception:
            pass
            
        if card.find_elements(By.XPATH, ".//button[contains(text(), 'Quero me candidatar')]"):
            total_valid += 1
            
    print(f"\n{Colors.BLUE}🔍 [Page Scraper]{Colors.END} Found {Colors.BOLD}{total_cards_count}{Colors.END} total job cards. {Colors.BOLD}{total_valid}{Colors.END} are active for application.")
    
    clicked_count = 0
    skipped_count = 0
    valid_processed_count = 0
    
    for card_id in card_ids:
        try:
            close_possible_popups(driver, config)
            
            try:
                card = driver.find_element(By.XPATH, f"//li[@data-offer-item='{card_id}']")
            except Exception:
                continue
            
            buttons = card.find_elements(By.XPATH, ".//button[contains(text(), 'Quero me candidatar')]")
            if not buttons:
                continue
                
            button = buttons[0]
            valid_processed_count += 1
            
            card_text = card.text
            job_title = "Vaga Desconhecida"
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.title_offer a")
                job_title = title_elem.text
            except Exception:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "h2.title_offer")
                    job_title = title_elem.text
                except Exception:
                    pass
            
            if contains_senior_terms(card_text, config):
                skipped_count += 1
                if config.VERBOSE:
                    matched_term = "SENIOR/SN"
                    for term in config.SENIOR_TERMS:
                        if re.search(rf'\b{re.escape(term)}\b', card_text, re.IGNORECASE):
                            matched_term = term.upper()
                            break
                    print(f"  {Colors.YELLOW}⏭ [SKIPPED]{Colors.END} Skipping Senior role: '{Colors.BOLD}{job_title}{Colors.END}' (Matched: {Colors.YELLOW}{matched_term}{Colors.END})")
                continue
                
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", 
                button
            )
            print(f"  {Colors.CYAN}➤{Colors.END} Targeting: '{Colors.BOLD}{job_title}{Colors.END}' ({valid_processed_count}/{total_valid})... ", end="", flush=True)
            highlight_element(driver, button, config, color="#ff4393" if config.TEST_MODE else "#3624d6")
            
            try:
                actions = ActionChains(driver)
                actions.move_to_element(button).pause(random.uniform(0.1, 0.4)).click().perform()
                print(f"{Colors.GREEN}✔ [CLICK]{Colors.END}")
                clicked_count += 1
            except Exception as click_err:
                if config.VERBOSE:
                    print(f"\n  {Colors.YELLOW}⚡ [INFO]{Colors.END} Click intercepted or failed. Clearing popups & retrying...")
                close_possible_popups(driver, config)
                time.sleep(0.6)
                
                try:
                    card = driver.find_element(By.XPATH, f"//li[@data-offer-item='{card_id}']")
                    retry_buttons = card.find_elements(By.XPATH, ".//button[contains(text(), 'Quero me candidatar')]")
                    if retry_buttons:
                        button = retry_buttons[0]
                except Exception:
                    pass
                        
                try:
                    actions = ActionChains(driver)
                    actions.move_to_element(button).pause(0.2).click().perform()
                    print(f"{Colors.GREEN}✔ [CLICK (Retry)]{Colors.END}")
                    clicked_count += 1
                except Exception:
                    if config.VERBOSE:
                        print(f"\n  {Colors.YELLOW}⚙ [JS FALLBACK]{Colors.END} Standard click blocked. Clicking button via JavaScript...")
                    driver.execute_script("arguments[0].click();", button)
                    print(f"{Colors.GREEN}✔ [CLICK (JS)]{Colors.END}")
                    clicked_count += 1
                    
            time.sleep(0.6)
            close_possible_popups(driver, config)
            
            delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
            if config.VERBOSE:
                print(f"  {Colors.BLUE}⏳ [HUMAN DELAY]{Colors.END} Waiting {Colors.BOLD}{delay:.2f}{Colors.END} seconds...")
            time.sleep(delay)
            
        except StaleElementReferenceException:
            if config.VERBOSE:
                print(f"\n  {Colors.YELLOW}⚠️ [DOM Update]{Colors.END} Element went stale.")
            continue
        except Exception as e:
            print(f"\n  {Colors.RED}✘ [WARN]{Colors.END} Failed to process card {card_id}: {e}")
            
    print(f"\n{Colors.GREEN}✔ [Page Summary]{Colors.END} Applied: {Colors.BOLD}{clicked_count}{Colors.END} | Skipped Senior: {Colors.BOLD}{skipped_count}{Colors.END}")
    return clicked_count

def get_url_for_keyword(base_url: str, keyword: str) -> str:
    if "/vagas/" in base_url:
        parts = base_url.split("/vagas/")
        subparts = parts[1].split("/", 1)
        formatted_keyword = keyword.lower().replace(" ", "-")
        return parts[0] + "/vagas/" + formatted_keyword + "/" + subparts[1]
    return base_url

def run_scraper():
    config, credentials = load_env_configurations()
    print_banner()
    
    if not config.TEST_MODE:
        if credentials.email == "your_email@example.com" or not credentials.email:
            print(f"\n{Colors.BOLD}=== Catho Login Credentials ==={Colors.END}")
            credentials.email = input("Enter your Catho Email/CPF: ").strip()
        if credentials.password == "your_password" or not credentials.password:
            credentials.password = getpass.getpass("Enter your Catho Password (secure input, hidden): ")
            
    driver = setup_driver(config, headless=False)
    
    try:
        if not login_to_catho(driver, credentials, config):
            print(f"\n{Colors.RED}❌ [EXIT]{Colors.END} Login flow failed. Halting scraper to prevent loops on blank/login pages.")
            return
            
        for keyword in config.KEYWORDS_WORKLIST:
            formatted_keyword = keyword.lower().replace(" ", "-")
            target_url = get_url_for_keyword(config.REAL_BASE_URL, keyword)
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}\n📋 STARTING SCRAPING FOR KEYWORD: {Colors.YELLOW}{keyword.upper()}{Colors.CYAN}\n{'='*60}{Colors.END}")
            print(f"{Colors.BLUE}🎯 Target URL:{Colors.END} {Colors.UNDERLINE}{target_url}{Colors.END}")
            
            driver.get(target_url)
            time.sleep(2.5)
            
            if formatted_keyword not in driver.current_url or "order=dataAtualizacao" not in driver.current_url:
                print(f"\n{Colors.YELLOW}⚠️ [URL VERIFICATION]{Colors.END} Currently on: {Colors.UNDERLINE}{driver.current_url}{Colors.END}")
                print(f"-> Redirecting to target URL: {Colors.UNDERLINE}{target_url}{Colors.END}")
                driver.get(target_url)
                time.sleep(2.5)
                
            current_page = 1
            while current_page <= config.MAX_PAGES_TO_SCRAPE:
                print(f"\n{Colors.HEADER}{Colors.BOLD}{'-'*50}\n📄 SCRAPING {keyword.upper()} - PAGE {current_page}\n{'-'*50}{Colors.END}")            
                clicked_count = process_page_buttons(driver, config)
                
                if clicked_count == 0:
                    print(f"\n{Colors.YELLOW}📋 [Worklist]{Colors.END} Found 0 application buttons on page {current_page} for '{keyword}'. Moving to next keyword in worklist...")
                    break
                    
                if current_page >= config.MAX_PAGES_TO_SCRAPE:
                    print(f"\n{Colors.YELLOW}🛑 Reached maximum page limit ({config.MAX_PAGES_TO_SCRAPE}) for keyword '{keyword}'.{Colors.END}")
                    break
                    
                try:
                    next_button_selectors = [
                        (By.XPATH, "//button[@aria-label='Próxima página']"),
                        (By.CSS_SELECTOR, "li.next a"),
                        (By.XPATH, "//a[contains(text(), 'Próxima')]")
                    ]
                    
                    next_button = None
                    for by, selector in next_button_selectors:
                        try:
                            next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, selector)))
                            break
                        except Exception:
                            continue
                            
                    if next_button:
                        print(f"\n{Colors.BLUE}⏭️ Navigating to next page...{Colors.END}")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                        time.sleep(1.0)
                        driver.execute_script("arguments[0].click();", next_button)
                        current_page += 1
                        time.sleep(random.uniform(2.5, 4.0))
                    else:
                        print(f"\n{Colors.YELLOW}🛑 No 'Next' button found. Reached the end of results for '{keyword}'.{Colors.END}")
                        break
                except Exception as e:
                    print(f"\n{Colors.RED}❌ Error trying to navigate to the next page: {e}{Colors.END}")
                    break
                    
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL KEYWORDS PROCESSED SUCCESSFULLY!{Colors.END}")
        
    finally:
        print(f"\n{Colors.CYAN}Closing browser session in 5 seconds...{Colors.END}")
        time.sleep(5)
        try:
            driver.quit()
        except:
            pass
