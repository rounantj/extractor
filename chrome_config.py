"""
Configurações específicas para o Chrome no Heroku
"""
import os
import tempfile

def get_chrome_options_heroku():
    """Retorna as opções do Chrome otimizadas para Heroku"""
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    
    # Configurações ESSENCIAIS para Heroku
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Configurações para evitar conflitos de diretório
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--disable-background-timer-checking')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    
    # Configurações de memória e performance
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--no-report-upload')
    
    # Configurações de janela
    chrome_options.add_argument('--window-size=1366,768')
    
    # User agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Configurações experimentais
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # IMPORTANTE: NÃO usar --user-data-dir para evitar conflitos no Heroku
    # chrome_options.add_argument('--user-data-dir=/tmp/chrome-data')
    
    return chrome_options

def cleanup_chrome_temp_files():
    """Limpa arquivos temporários do Chrome"""
    try:
        temp_dir = tempfile.gettempdir()
        chrome_patterns = ['chrome', 'chromium', 'google-chrome']
        
        for pattern in chrome_patterns:
            for item in os.listdir(temp_dir):
                if pattern in item.lower():
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isdir(item_path):
                            import shutil
                            shutil.rmtree(item_path)
                        elif os.path.isfile(item_path):
                            os.remove(item_path)
                    except:
                        pass
    except:
        pass
