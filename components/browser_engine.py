import os
import sys
import time
import re
import traceback
import types

try:
    import distutils.version
except ImportError:
    class LooseVersion:
        def __init__(self, versionstring):
            self.version = versionstring
            self.vstring = versionstring
            self.parts = [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', versionstring) if x]
        def __str__(self):
            return self.version
        def __repr__(self):
            return f"LooseVersion('{self.version}')"
        def __eq__(self, other):
            if not isinstance(other, LooseVersion):
                return NotImplemented
            return self.parts == other.parts
        def __lt__(self, other):
            if not isinstance(other, LooseVersion):
                return NotImplemented
            return self.parts < other.parts
        def __le__(self, other):
            if not isinstance(other, LooseVersion):
                return NotImplemented
            return self.parts <= other.parts
        def __gt__(self, other):
            if not isinstance(other, LooseVersion):
                return NotImplemented
            return self.parts > other.parts
        def __ge__(self, other):
            if not isinstance(other, LooseVersion):
                return NotImplemented
            return self.parts >= other.parts

    distutils = types.ModuleType("distutils")
    distutils_version = types.ModuleType("distutils.version")
    distutils_version.LooseVersion = LooseVersion
    distutils.version = distutils_version
    sys.modules["distutils"] = distutils
    sys.modules["distutils.version"] = distutils_version

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from components.config_loader import ScraperConfig

# ==========================================
# BEAUTIFUL TERMINAL STYLING
# ==========================================
def supports_color():
    supported_platform = sys.platform != 'win32' or 'ANSICON' in os.environ
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty

USE_COLOR = supports_color()

class Colors:
    HEADER = '\033[95m' if USE_COLOR else ''
    BLUE = '\033[94m' if USE_COLOR else ''
    CYAN = '\033[96m' if USE_COLOR else ''
    GREEN = '\033[92m' if USE_COLOR else ''
    YELLOW = '\033[93m' if USE_COLOR else ''
    RED = '\033[91m' if USE_COLOR else ''
    BOLD = '\033[1m' if USE_COLOR else ''
    DIM = '\033[2m' if USE_COLOR else ''
    UNDERLINE = '\033[4m' if USE_COLOR else ''
    END = '\033[0m' if USE_COLOR else ''

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}   ⚡======================================================================⚡
{Colors.BLUE}{Colors.BOLD}    ██████╗ █████╗ ████████╗██╗  ██╗ ██████╗     ███████╗██████╗ ███╗   ███╗
    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║██╔═══██╗    ██╔════╝██╔══██╗████╗ ████║
    ██║  ╚═╝███████║   ██║   ███████║██║   ██║    ███████╗██████╔╝██╔████╔██║
    ██║  ██╗██╔══██║   ██║   ██╔══██║██║   ██║    ╚════██║██╔═══╝ ██║╚██╔╝██║
    ╚██████╔╝██║  ██║   ██║   ██║  ██║╚██████╔╝    ███████║██║     ██║ ╚═╝ ██║
     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝     ╚══════╝╚═╝     ╚═╝     ╚═╝
{Colors.CYAN}{Colors.BOLD}   ⚡======================================================================⚡
                        {Colors.GREEN}{Colors.BOLD}Arachne Invincible Stealth Engine{Colors.END}
    """
    print(banner)

def setup_driver(config: ScraperConfig, headless: bool = False):
    """
    Elite browser initialization module using undetected_chromedriver.
    """
    # Retorna o diretório raiz do projeto subindo um nível a partir de 'components'
    workspace_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    
    # Caminho da Raposa: Tenta usar a sessão nativa do usuário para evitar login manual
    bot_profile = os.path.join(workspace_dir, "bot_profile")
    
    if hasattr(config, 'CHROME_PROFILE_DIR') and config.CHROME_PROFILE_DIR and os.path.exists(config.CHROME_PROFILE_DIR):
        bot_profile = config.CHROME_PROFILE_DIR
    elif os.path.exists(os.path.expanduser("~/.config/google-chrome/Default/Cookies")):
        bot_profile = os.path.expanduser("~/.config/google-chrome")
    elif os.path.exists(os.path.expanduser("~/.config/chromium/Default/Cookies")):
        bot_profile = os.path.expanduser("~/.config/chromium")
        
    try:
        chrome_options = uc.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1280,800")
        
        chrome_options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        
        # Garante que o undetected_chromedriver foque no Default profile
        chrome_options.add_argument("--profile-directory=Default")
        
        print(f"\n{Colors.BLUE}🌐{Colors.END} {Colors.BOLD}[Chrome]{Colors.END} Starting undetected-chromedriver with profile: {Colors.DIM}{bot_profile}{Colors.END}")
        
        driver = uc.Chrome(
            version_main=148,
            options=chrome_options,
            user_data_dir=bot_profile
        )
        return driver
        
    except Exception as chrome_err:
        print(f"\n{Colors.RED}❌ [FATAL]{Colors.END} Chromium initialization failed: {chrome_err}")
        if config.VERBOSE:
            traceback.print_exc()
        raise

def highlight_element(driver, element, config: ScraperConfig, color="#ff4393"):
    try:
        original_style = element.get_attribute("style")
        driver.execute_script(
            f"arguments[0].setAttribute('style', 'border: 3px dashed {color} !important; box-shadow: 0 0 10px {color} !important;');", 
            element
        )
        time.sleep(0.8) 
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, original_style)
    except Exception:
        if config.VERBOSE:
            traceback.print_exc()

def close_possible_popups(driver, config: ScraperConfig):
    # Detect visible modal/popup/consent/dialog containers first to avoid false-positive clicks
    modal_container_selectors = [
        "div[class*='modal' i]", 
        "div[class*='popup' i]", 
        "div[role='dialog']", 
        "div[role='alertdialog']",
        "div[class*='overlay' i]",
        "[class*='cookie' i]",
        "[class*='consent' i]",
        "[class*='lgpd' i]"
    ]
    
    visible_containers = []
    for selector in modal_container_selectors:
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, selector)
            for container in containers:
                if container.is_displayed():
                    visible_containers.append(container)
        except Exception:
            continue
            
    if not visible_containers:
        return
        
    popup_selectors = [
        (By.CSS_SELECTOR, "button.button_close"),
        (By.CSS_SELECTOR, "span.i_close"),
        (By.CSS_SELECTOR, ".i_close"),
        (By.CSS_SELECTOR, "button[data-modal-close]"),
        (By.CSS_SELECTOR, "button[aria-label*='Fechar']"),
        (By.CSS_SELECTOR, "button[aria-label='Close']"),
        (By.CSS_SELECTOR, ".modal-close"),
        (By.CSS_SELECTOR, ".close-button"),
        (By.CSS_SELECTOR, "[data-testid='modal-close']"),
        (By.XPATH, ".//*[self::button or self::span][text()='x' or text()='X']"),
        (By.XPATH, ".//button[contains(text(), 'Entendi')]"),
        (By.XPATH, ".//button[contains(text(), 'Fechar')]")
    ]
    
    closed_any = False
    for container in visible_containers:
        for by, selector in popup_selectors:
            try:
                elements = container.find_elements(by, selector)
                for elem in elements:
                    try:
                        is_shown = elem.is_displayed()
                    except Exception:
                        is_shown = True
                        
                    if is_shown:
                        print(f"  {Colors.RED}🚨 [POPUP]{Colors.END} Closing popup inside container using: {Colors.DIM}{selector}{Colors.END}")
                        driver.execute_script("arguments[0].click();", elem)
                        closed_any = True
                        time.sleep(0.5)
            except Exception:
                continue
                
    # Fallback: ESC key dismissal if we detected active containers but couldn't click any specific close button
    if not closed_any:
        try:
            active_elem = driver.switch_to.active_element
            if active_elem:
                active_elem.send_keys(Keys.ESCAPE)
        except Exception:
            pass
