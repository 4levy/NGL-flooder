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

async def send_message(client, target, message, agents, delay=0):
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
    while True:
        try:
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

    print(BANNER)
    print(f"\nLoaded {len(agents)} user agents\n")

    t = input("Username target: ")
    m = input("Message: ")
    delay = float(input("Delay between requests (seconds): "))

    async def inm():
        async with httpx.AsyncClient() as client:
            while True:
                await send_message(client, t, m, agents, delay)

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
