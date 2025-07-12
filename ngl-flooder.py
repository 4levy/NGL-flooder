import os
import requests
import httpx
import uuid
import random
import asyncio
import fade
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn


# CONFIG
BANNER = f"""
           _             __        __        __              
 _      __(_)___  ____ _/ /_____ _/ /_____  / /__  __________
| | /| / / / __ \/ __ `/ __/ __ `/ //_/ _ \/ / _ \/ ___/ ___/
| |/ |/ / / / / / /_/ / /_/ /_/ / ,< /  __/ /  __(__  |__  ) 
|__/|__/_/_/ /_/\__, /\__/\__,_/_/|_|\___/_/\___/____/____/  
               /____/                                         
               
"""

# value
console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def title():
    os.system('title NGL Flooder - By 4levy') if os.name == 'nt' else None
    


def user_agents():
    try:
        url = "https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/refs/heads/master/Chrome.txt"
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading user agents: {e}")
        return []

def get_https_proxies():
    try:
        url = "https://raw.githubusercontent.com/4levy/NGL-flooder/refs/heads/main/proxies_checked.txt"
        response = requests.get(url)
        response.raise_for_status()
        proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
        return proxies
    except requests.exceptions.RequestException as e:
        print(f"Error downloading proxies: {e}")
        return []

async def send_message(client, target, message, agents, proxies, delay=0):
    user_agent = random.choice(agents)
    headers = {
        "User-Agent": user_agent,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "username": target,
        "question": message,
        "deviceId": str(uuid.uuid4()),
        "gameSlug": None,
        "referrer": None
    }
    proxy = None
    if proxies:
        proxy = random.choice(proxies)
        proxy_url = f"http://{proxy}"
    while True:
        try:
            if proxy:
                transport = httpx.AsyncHTTPTransport(proxy=proxy_url, verify=False)
                async with httpx.AsyncClient(transport=transport, verify=False) as proxy_client:
                    response = await proxy_client.post("https://ngl.link/api/submit", headers=headers, data=payload)
            else:
                response = await client.post("https://ngl.link/api/submit", headers=headers, data=payload)
            if response.status_code == 200:
                print(f"[+] Sent! - {response.status_code}")
                break
            elif response.status_code == 429:
                print(f"[!] Failed - {response.status_code} (Too Many Requests). Retrying with longer delay...")
                await asyncio.sleep(5 + random.uniform(0, 2)) 
            elif response.status_code == 503:
                print(f"[!] Failed - {response.status_code} (Service Unavailable)")
                break
            else:
                print(f"[!] Failed - {response.status_code}")
                break
        except httpx.HTTPError as e:
            msg = str(e)
            if 'CERTIFICATE_VERIFY_FAILED' in msg:
                print("[!] SSL Error: CERTIFICATE_VERIFY_FAILED (certificate verify failed)")
            elif not msg.strip():
                print("[!] Error: (empty error message)")
            else:
                print(f"[!] Error: {msg}")
            return False
        except Exception as e:
            msg = str(e)
            if not msg.strip():
                print("[!] Error: (empty error message)")
            else:
                print(f"[!] Error: {msg}")
            return False
    if delay > 0:
        await asyncio.sleep(delay)
    try:
        return response.status_code == 200
    except:
        return False

async def spam(target, message, agents, amount, delay=0):
    async with httpx.AsyncClient() as client:
        for _ in range(amount):
            await send_message(client, target, message, agents, delay)

async def check_ngl_user(username: str) -> bool:
    url = f"https://ngl.link/{username}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if "Could not find user" in response.text or response.status_code == 404:
                return False
            return True
    except Exception as e:
        console.print(f"[red]❌ Error checking username: {e}[/red]")
        return False

def feliy():
    title()
    agents = user_agents()
    if not agents:
        console.print("[red]❌ Failed to load user agents. Exiting.[/red]")
        return

    proxies = get_https_proxies()
    if not proxies:
        console.print("[yellow]⚠️ Failed to load HTTPS proxies. Continuing without proxies.[/yellow]")
    print(f"{BANNER}")
    console.print(f"[green] Loaded {len(agents)} user agents[/green]")
    console.print(f"[green] Loaded {len(proxies)} HTTPS proxies[/green]\n")

    while True:
        t = Prompt.ask("[bold cyan] (?) [/bold cyan] Username")
        if asyncio.run(check_ngl_user(t)):
            break
        else:
            console.print("[red]❌ Could not find user. Please enter a valid NGL username.[/red]")

    m = Prompt.ask("[bold cyan] (?) [/bold cyan] Enter message to send")

    while True:
        delay_input = Prompt.ask("[bold cyan] (?) [/bold cyan] Delay between requests (seconds)", default="1")
        try:
            delay = float(delay_input.lstrip('0') or '0')
            break
        except ValueError:
            console.print("[red]❌ Invalid delay. Please enter a valid number (e.g., 2 or 0.5).[/red]")

    success_count = 0
    success_count_lock = asyncio.Lock()

    async def worker(client, t, m, agents, proxy, delay):
        nonlocal success_count
        while True:
            result = await send_message(client, t, m, agents, [proxy], delay)
            if result:
                async with success_count_lock:
                    success_count += 1

    async def inm():
        proxies = get_https_proxies()
        async with httpx.AsyncClient() as client:
            tasks = [asyncio.create_task(worker(client, t, m, agents, proxy, delay)) for proxy in proxies]
            await asyncio.gather(*tasks)

    try:
        asyncio.run(inm())
    except KeyboardInterrupt:
        console.print(f"\n[bold red]⛔ Interrupted by user.[/bold red] Successfully sent: [green]{success_count}[/green]")

if __name__ == '__main__':
    clear()
    try:
        feliy()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user during input.")
