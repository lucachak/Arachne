import urllib.parse
from components.config_loader import load_env_configurations

class SearchBuilder:
    def __init__(self, search_time: str = "604800", keywords: str = ""):
        self.search_time = search_time
        self.keywords = keywords

    def make_url(self) -> str:
        """Gera a URL formatada e segura."""
        encoded_keyword = urllib.parse.quote(self.keywords.strip())
        # Base URL fixada internamente para LinkedIn ou buscar via conf, mantendo fallback de segurança
        base_url = "https://www.linkedin.com/jobs/search/"
        return f"{base_url}?keywords={encoded_keyword}&f_TPR=r{self.search_time}&f_AL=true"

    @staticmethod
    def build_all() -> list[str]:
        """Gera todas as URLs baseadas na WORKLIST centralizada."""
        config, _ = load_env_configurations()
        keywords = config.KEYWORDS_WORKLIST
        
        return [SearchBuilder(keywords=kw).make_url() for kw in keywords]


    @staticmethod
    def return_single_url() -> str:
        config, _ = load_env_configurations()
        keywords = config.KEYWORDS_WORKLIST
        
        if not keywords:
            return SearchBuilder(keywords="vaga").make_url()
            
        return SearchBuilder(keywords=keywords[0]).make_url()