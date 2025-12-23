#!/usr/bin/env python3
"""
ChronoGram - Instagram OSINT Tool by m0us3r
Version: 1.0 (Bio, HD Avatar, Folder Organization & HTML Report)

Usage:
    # Search by User ID
    python3 chronogram.py -i 123456789 -s YOUR_SESSIONID

    # Search by Username
    python3 chronogram.py -u username -s YOUR_SESSIONID

    # Search by Phone Number
    python3 chronogram.py -n +556199999-9999 -s YOUR_SESSIONID

License: GNU General Public License v3.0
"""

import argparse
import requests
from urllib.parse import quote_plus
from json import dumps
import os
import sys
import time
import subprocess
import shutil

# Network Settings
DEFAULT_PROXY = "socks5://127.0.0.1:9050"
LOOKUP_HEADERS = {
    "User-Agent": "Instagram 101.0.0.15.120",
    "X-IG-App-ID": "124024574287414",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Colors for terminal
GREEN, BLUE, YELLOW, RED, RESET = "\033[92m", "\033[94m", "\033[93m", "\033[91m", "\033[0m"

ASCII_ART = r"""
 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗ ██████╗  ██████╗ ██████╗  █████╗ ███╗   ███╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
██║     ███████║██████╔╝██║   ██║██╔██╗ ██║██║   ██║██║  ███╗██████╔╝███████║██╔████╔██║
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██║   ██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
"""

MOUSE_ASCII = r"""
      (q\_/p)
       (o o)
   ==m==\_/==m==
      m0us3r
"""

def check_infrastructure():
    print(f"{BLUE}[*] Initializing Security Check (Stealth Mode)...{RESET}")
    if not shutil.which("tor"):
        print(f"{RED}[!] Error: TOR is not installed.{RESET}")
        sys.exit(1)
    subprocess.run(["sudo", "systemctl", "restart", "tor"], capture_output=True)
    time.sleep(2)
    try:
        proxies = {"http": DEFAULT_PROXY, "https": DEFAULT_PROXY}
        r = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=10)
        data = r.json()
        print(f"{GREEN}[+] TOR Active | IP: {data.get('query')} ({data.get('country')}){RESET}")
    except:
        print(f"{RED}[!] Error: SOCKS5 Connection failed.{RESET}")
        sys.exit(1)

def download_hd_avatar(url, folder_path, username):
    proxies = {"http": DEFAULT_PROXY, "https": DEFAULT_PROXY}
    try:
        r = requests.get(url, proxies=proxies, stream=True, timeout=15)
        file_path = os.path.join(folder_path, f"{username}_avatar.jpg")
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(1024): f.write(chunk)
        return f"{username}_avatar.jpg"
    except: return None

def generate_html_report(data, folder_path, avatar_filename):
    username = data['profile'].get('username')
    file_path = os.path.join(folder_path, f"report_{username}.html")
    html_content = f"""
    <html>
    <head><meta charset="UTF-8"><style>
        body {{ font-family: sans-serif; background: #f4f7f6; padding: 40px; }}
        .card {{ max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .avatar {{ width: 150px; height: 150px; border-radius: 50%; border: 4px solid #3498db; object-fit: cover; display: block; margin: 0 auto 20px; }}
        .bio {{ font-style: italic; background: #f9f9f9; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
    </style></head>
    <body>
        <div class="card">
            <img src="{avatar_filename}" class="avatar">
            <h1 style="text-align:center;">@{username}</h1>
            <p><b>User ID:</b> {data['uid']}</p>
            <p><b>Email:</b> {data['recovery'].get('obfuscated_email')}</p>
            <p><b>Phone:</b> {data['recovery'].get('obfuscated_phone')}</p>
            <div class="bio"><b>Biography:</b><br>{data['profile'].get('biography', 'N/A')}</div>
        </div>
    </body></html>
    """
    with open(file_path, "w", encoding="utf-8") as f: f.write(html_content)

def get_data(query, sessionid, uid=None):
    proxies = {"http": DEFAULT_PROXY, "https": DEFAULT_PROXY}
    cookies = {'sessionid': sessionid}
    data_payload = {"q": query, "device_id": "android-check", "skip_recovery": "1"}
    payload = "signed_body=SIGNATURE." + quote_plus(dumps(data_payload, separators=(",", ":")))
    try:
        r_rec = requests.post('https://i.instagram.com/api/v1/users/lookup/', headers=LOOKUP_HEADERS, data=payload, cookies=cookies, proxies=proxies).json()
        user_id = uid or r_rec.get("user", {}).get("pk")
        r_prof = requests.get(f'https://i.instagram.com/api/v1/users/{user_id}/info/', headers={"User-Agent": "Instagram 64.0.0.14.96"}, cookies=cookies, proxies=proxies).json().get("user", {})
        return {"uid": user_id, "recovery": r_rec, "profile": r_prof}
    except: return None

if __name__ == "__main__":
    # Header Section
    print(f"{GREEN}{ASCII_ART}{RESET}")
    print(f"{YELLOW}The one who anticipates, wins. Tracking shadows, revealing secrets!{RESET}")
    print(f"{BLUE}{MOUSE_ASCII}{RESET}")

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--username")
    group.add_argument("-i", "--id")
    group.add_argument("-n", "--number")
    parser.add_argument("-s", "--sessionid", required=True)
    args = parser.parse_args()

    check_infrastructure()

    query = args.username or args.id or args.number
    print(f"[*] Targeting: {YELLOW}{query}{RESET}...")

    data = get_data(query, args.sessionid, uid=args.id)

    if data and data.get('profile'):
        username = data['profile'].get('username', 'unknown')
        if not os.path.exists(username): os.makedirs(username)

        avatar_url = data['profile'].get('hd_profile_pic_url_info', {}).get('url') or data['profile'].get('profile_pic_url')
        avatar_file = download_hd_avatar(avatar_url, username, username)
        generate_html_report(data, username, avatar_file)

        print(f"\n{BLUE}=== EXTRACTION REPORT: @{username} ==={RESET}")
        print(f"{GREEN}[+] USER ID   : {data['uid']}{RESET}")
        print(f"{GREEN}[+] EMAIL     : {data['recovery'].get('obfuscated_email', 'Not found')}{RESET}")
        print(f"{GREEN}[+] PHONE     : {data['recovery'].get('obfuscated_phone', 'Not found')}{RESET}")
        print(f"{GREEN}[+] BIO       : {data['profile'].get('biography', 'N/A')}{RESET}")
        print(f"\n[DONE] Files saved in ./{username}/")
    else:
        print(f"{RED}[!] Error: Extraction failed. Verify SessionID.{RESET}")

