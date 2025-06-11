import requests
import random
import string
import json
import names
from eth_account import Account
from faker import Faker
import time
from bs4 import BeautifulSoup
import re
import asyncio
from colorama import init, Fore, Style
from rich.console import Console
from rich.style import Style as RichStyle

# Initialize colorama and rich
init(autoreset=True)
console = Console()

# Initialize Faker
fake = Faker()

# File to store account data
DATA_FILE = 'data.json'
WALLET_FILE = 'pkevm.txt'
PROXY_FILE = 'proxy.txt'

# SCTG API Key
SCTG_API_KEY = "YOUR_API_KEY_HERE"

# Load existing data
try:
    with open(DATA_FILE, 'r') as f:
        accounts = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    accounts = []

# Generate EVM wallet address
def generate_wallet():
    acct = Account.create()
    address = acct.address
    private_key = acct.key.hex()
    
    with open(WALLET_FILE, 'a') as f:
        f.write(f"Address: {address}\nPrivate Key: {private_key}\n\n")
    
    console.print(f"[*] Generated wallet: {address} ✨", style=RichStyle(color="cyan"))
    return address

# Get proxy from file
def get_proxy():
    try:
        with open(PROXY_FILE, 'r') as f:
            proxies = f.read().splitlines()
            if proxies:
                proxy = random.choice(proxies).strip()
                return {
                    'http': proxy,
                    'https': proxy
                }
    except FileNotFoundError:
        console.print("[!] Proxy file not found. 😅", style=RichStyle(color="red"))
    return None

# Generate temp email
def generate_email(domain):
    first_name = names.get_first_name().lower()
    last_name = names.get_last_name().lower()
    random_nums = ''.join(random.choices(string.digits, k=4))
    email_base = f"{first_name}{random_nums}@{domain}"
    
    if len(email_base) > 128:
        email_base = email_base[:128]
    
    console.print(f"[*] Generated email: {email_base} 📧", style=RichStyle(color="cyan"))
    return email_base

# Generate password
def generate_password():
    first_name = names.get_first_name().capitalize()
    random_nums = ''.join(random.choices(string.digits, k=5))
    password = f"{first_name}{random_nums}@@"
    console.print(f"[*] Generated password: {password} 🔑", style=RichStyle(color="cyan"))
    return password

# Fetch temporary email domains
async def get_domains(max_retries=5):
    attempt = 0
    proxy = get_proxy()
    while attempt < max_retries:
        try:
            key = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2))
            response = requests.get(f"https://generator.email/search.php?key={key}", timeout=120, proxies=proxy)
            
            if response.ok:
                try:
                    json_data = response.json()
                    if isinstance(json_data, list) and json_data:
                        return json_data
                except ValueError:
                    console.print("[!] Failed to parse JSON response for domains. 😓", style=RichStyle(color="red"))
            attempt += 1
            await asyncio.sleep(2)
        except requests.exceptions.RequestException as error:
            console.print(f"[!] Error fetching domains: {error} 😅", style=RichStyle(color="red"))
            attempt += 1
            await asyncio.sleep(2)
    console.print("[!] Failed to get temp mail domains after retries. 😢", style=RichStyle(color="red"))
    return []

# Hardcode reCAPTCHA v3 site key
def get_recaptcha_site_key(url, proxy=None):
    return "6LeHFokUAAAAABceXPpNEEuvJcBwxtcDYB1_nVc6"

# Generic CAPTCHA solver
def solve_captcha(captcha_type, params, proxy=None, max_retries=3):
    in_url = "https://api.sctg.xyz/in.php"
    res_url = "https://api.sctg.xyz/res.php"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    
    payload = {
        "key": SCTG_API_KEY,
        "method": captcha_type,
    }
    payload.update(params)
    
    if proxy:
        proxy_str = proxy.get('http').replace('http://', '')
        if '@' in proxy_str:
            user_pass, ip_port = proxy_str.split('@')
            payload.update({
                "proxy": ip_port,
                "proxytype": "HTTP",
                "proxyuser": user_pass.split(':')[0],
                "proxypass": user_pass.split(':')[1]
            })
        else:
            payload.update({
                "proxy": proxy_str,
                "proxytype": "HTTP"
            })
    
    for attempt in range(max_retries):
        try:
            response = requests.post(in_url, headers=headers, data=payload, timeout=30)
            response_text = response.text.strip()
            
            if not response_text.startswith("OK|"):
                console.print(f"[!] SCTG task creation failed: {response_text} 😓", style=RichStyle(color="red"))
                time.sleep(5)
                continue
            
            request_id = response_text.split("|")[1]
            console.print(f"[*] SCTG task created: {request_id} 🚀", style=RichStyle(color="cyan"))
            
            for _ in range(30):
                result_url = f"{res_url}?key={SCTG_API_KEY}&action=get&id={request_id}"
                result_response = requests.get(result_url, timeout=30)
                result_text = result_response.text.strip()
                
                if result_text == "CAPCHA_NOT_READY":
                    console.print(f"[*] Waiting for SCTG {captcha_type} solution... ⏳", style=RichStyle(color="yellow"))
                    time.sleep(3)
                    continue
                
                if result_text.startswith("OK|"):
                    captcha_token = result_text.split("|")[1]
                    console.print(f"[*] {captcha_type} solved successfully! 🎉", style=RichStyle(color="green"))
                    return captcha_token
                
                console.print(f"[!] SCTG result error: {result_text} 😅", style=RichStyle(color="red"))
                break
            
            console.print(f"[!] SCTG {captcha_type} solving timed out. 😢", style=RichStyle(color="red"))
        except Exception as e:
            console.print(f"[!] Error solving {captcha_type}: {e} 😓", style=RichStyle(color="red"))
        time.sleep(5)
    
    console.print(f"[!] Failed to solve {captcha_type} after retries. 😢", style=RichStyle(color="red"))
    return None

# Solve reCAPTCHA v3
def solve_recaptcha_v3(site_key, page_url, proxy=None):
    params = {
        "googlekey": site_key,
        "pageurl": page_url,
        "min_score": "0.7",
        "version": "v3"
    }
    return solve_captcha("userrecaptcha", params, proxy)

class LoopFiBot:
    def __init__(self, use_proxy=False):
        self.session = requests.Session()
        self.use_proxy = use_proxy
        self.proxy = get_proxy() if use_proxy else None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    
    def get_headers(self, additional_headers=None):
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://giveaway.loopfi.xyz",
            "referer": "https://giveaway.loopfi.xyz/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": self.user_agent
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers
    
    def sign_up(self, email):
        url = "https://leads.kickofflabs.com/lead/188520"
        page_url = "https://giveaway.loopfi.xyz"
        
        site_key = get_recaptcha_site_key(page_url, self.proxy)
        if not site_key:
            console.print("[!] Failed to get reCAPTCHA site key. 😅", style=RichStyle(color="red"))
            return None
        
        captcha_token = solve_recaptcha_v3(site_key, page_url, self.proxy)
        if not captcha_token:
            console.print("[!] Failed to solve reCAPTCHA v3. 😓", style=RichStyle(color="red"))
            return None
        
        payload = {
            "email": email,
            "__form_name": "Default Form",
            "__source": "kfp.397471",
            "__custom": {
                "theme": "nft_giveaway",
                "pageType": "single_page"
            },
            "__kd": 1,
            "__kid": "",
            "__kol_captcha_response": captcha_token,
            "__kol_captcha_version": 3,
            "__language": "en-US",
            "__lid": "188520",
            "__mm": 149,
            "__rid": fake.uuid4(),
            "__sid": fake.uuid4(),
            "__uid": fake.uuid4(),
            "__url": "https://giveaway.loopfi.xyz/"
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=self.get_headers(),
                proxies=self.proxy,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"[*] Sign up successful! Social ID: {data.get('social_id')} 🎉", style=RichStyle(color="green"))
                return data.get("social_id")
            else:
                console.print(f"[!] Sign up failed: {response.status_code} - {response.text} 😢", style=RichStyle(color="red"))
                return None
        except Exception as e:
            console.print(f"[!] Error during sign up: {e} 😓", style=RichStyle(color="red"))
            return None
    
    def submit_wallet(self, social_id, wallet_address):
        url = "https://leads.kickofflabs.com/action/188520"
        
        payload = {
            "aid": "236334",
            "data": {
                "crypto_wallet": wallet_address
            },
            "kid": social_id,
            "__source": "koljs.397471"
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=self.get_headers(),
                proxies=self.proxy,
                timeout=30
            )
            
            if response.status_code == 200:
                console.print("[*] Wallet submitted successfully! 🥳", style=RichStyle(color="green"))
                console.print(f"{json.dumps({'message': 'Action Logged'})} {{wallet address: {wallet_address}}} ✨", style=RichStyle(color="green"))
                return True
            else:
                console.print(f"[!] Wallet submission failed: {response.status_code} - {response.text} 😢", style=RichStyle(color="red"))
                return False
        except Exception as e:
            console.print(f"[!] Error during wallet submission: {e} 😓", style=RichStyle(color="red"))
            return False
    
    def complete_task(self, social_id, action_id):
        url = "https://leads.kickofflabs.com/action/188520"
        
        payload = {
            "aid": action_id,
            "data": {},
            "kid": social_id,
            "__source": "koljs.397471"
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=self.get_headers(),
                proxies=self.proxy,
                timeout=30
            )
            
            if response.status_code == 200:
                console.print(f"[*] Task {action_id} completed successfully! 🚀", style=RichStyle(color="green"))
                return True
            else:
                console.print(f"[!] Task {action_id} failed: {response.status_code} - {response.text} 😅", style=RichStyle(color="red"))
                return False
        except Exception as e:
            console.print(f"[!] Error during task completion: {e} 😓", style=RichStyle(color="red"))
            return False
    
    def complete_all_tasks(self, social_id):
        task_ids = [
            "236334",  # Enter wallet address
            "238223",  # Live $5K winner reveal
            "236371",  # Follow on X
            "238545",  # Repost on X
            "236374",  # Join Telegram
            "236375",  # Join Discord
            "236376",  # Subscribe YouTube
            "237170",  # Follow LinkedIn
            "237171",  # Follow Debank
            "238209",  # Follow Hemi
            "238210",  # Follow Avalon Finance
            "238211",  # Follow ListaDAO
            "238212",  # Follow Royco Protocol
            "238213",  # Follow Rings Protocol
            "238214",  # Follow ThenaFi
            "238215",  # Follow OneClickFi
            "238216",  # Follow InceptionLRT
            "238217",  # Follow TermMaxFi
            "238417",  # Follow IMO Invest
            "238418",  # Follow XDC Network
            "238419",  # Follow XP Labs
            "238420",  # Follow OpenEden
            "238421",  # Follow KelpDAO
            "238422",  # Follow Kernel DAO
            "238423",  # Follow Louround
            "238424",  # Follow CryptoGrills
            "238426",  # Follow TheLearningPill
            "238538",  # Follow CarreNFT
            "238543",  # Follow Pratas.eth
            "238544"   # Follow Mr.Lin
        ]
        
        success_count = 0
        for task_id in task_ids:
            if self.complete_task(social_id, task_id):
                success_count += 1
            time.sleep(random.uniform(1, 3))
        
        console.print(f"[*] Completed {success_count}/{len(task_ids)} tasks 🎉", style=RichStyle(color="cyan"))
        return success_count

async def main():
    # Display author information
    console.print("=============================================================", style=RichStyle(color="magenta"))
    console.print("🌟 author: t.me/airdropdxns 😎", style=RichStyle(color="bright_magenta", bold=True))
    console.print("=============================================================", style=RichStyle(color="magenta"))
    
    iterations = int(input(f"{Fore.CYAN}[?] How many accounts to create: {Style.RESET_ALL}"))
    use_proxy = input(f"{Fore.CYAN}[?] Use proxy? (y/n): {Style.RESET_ALL}").lower() == 'y'
    
    domains = await get_domains()
    if not domains:
        console.print("[!] Failed to get temp mail domains 😢", style=RichStyle(color="red"))
        return
    
    for i in range(iterations):
        console.print(f"\n[*] Processing account #{i+1}/{iterations} 🚀", style=RichStyle(color="yellow"))
        
        domain = random.choice(domains)
        email = generate_email(domain)
        password = generate_password()
        wallet_address = generate_wallet()
        
        bot = LoopFiBot(use_proxy=use_proxy)
        
        social_id = bot.sign_up(email)
        if not social_id:
            continue
        
        bot.submit_wallet(social_id, wallet_address)
        bot.complete_all_tasks(social_id)
        
        accounts.append({
            "email": email,
            "password": password,
            "wallet": wallet_address,
            "social_id": social_id
        })
        
        with open(DATA_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)
        
        console.print("[*] Account data saved to data.json 📝", style=RichStyle(color="cyan"))
        console.print("[*] Wallet saved to pkevm.txt 💾", style=RichStyle(color="cyan"))
        
        delay = 1  # 1-second delay to avoid detection
        console.print(f"[*] Waiting {delay} seconds before next account... ⏰", style=RichStyle(color="yellow"))
        time.sleep(delay)

if __name__ == "__main__":
    asyncio.run(main())