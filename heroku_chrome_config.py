"""
Configurações do Chrome baseadas em soluções comprovadas do Heroku
Baseado em: https://github.com/heroku/heroku-buildpack-google-chrome
"""

import os
import tempfile
import shutil

def get_heroku_chrome_options():
    """Retorna opções do Chrome que funcionam no Heroku"""
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    
    # SOLUÇÃO COMPROVADA: Configurações essenciais que funcionam
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # SOLUÇÃO COMPROVADA: Diretório temporário único por processo
    temp_dir = f"/tmp/chrome-{os.getpid()}-{int(tempfile.time.time())}"
    os.makedirs(temp_dir, exist_ok=True)
    
    chrome_options.add_argument(f'--user-data-dir={temp_dir}')
    chrome_options.add_argument(f'--data-path={temp_dir}')
    chrome_options.add_argument(f'--homedir={temp_dir}')
    chrome_options.add_argument(f'--disk-cache-dir={temp_dir}/cache')
    
    # SOLUÇÃO COMPROVADA: Configurações de isolamento
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--no-zygote')
    chrome_options.add_argument('--disable-setuid-sandbox')
    
    # SOLUÇÃO COMPROVADA: Configurações de memória
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--max_old_space_size=4096')
    
    # SOLUÇÃO COMPROVADA: Configurações de rede
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--no-report-upload')
    
    # SOLUÇÃO COMPROVADA: Configurações de janela
    chrome_options.add_argument('--window-size=1366,768')
    chrome_options.add_argument('--start-maximized')
    
    # SOLUÇÃO COMPROVADA: User agent realista
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # SOLUÇÃO COMPROVADA: Configurações experimentais
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # SOLUÇÃO COMPROVADA: Configurações de segurança
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    
    return chrome_options, temp_dir

def cleanup_heroku_chrome_temp(temp_dir):
    """Limpa arquivos temporários do Chrome no Heroku"""
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 Diretório temporário do Heroku limpo: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Erro ao limpar diretório do Heroku: {e}")

def get_heroku_environment():
    """Retorna configurações de ambiente do Heroku"""
    return {
        'CHROME_BIN': '/usr/bin/google-chrome',
        'CHROMEDRIVER_PATH': '/usr/local/bin/chromedriver',
        'GOOGLE_CHROME_SHIM': '/app/.apt/usr/bin/google-chrome'
    }
