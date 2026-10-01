#!/usr/bin/env python3
"""
Tool Name: CODE MASTER - HTML Web Deployer
Channel: Code Master (কোড মাস্টার)
Features: Key System, Expiry Check, Permanent & Timer Based Hosting
"""

import os
import sys
import time
import random
import string
import datetime
import subprocess

# কালার কোড
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

# ================== KEY ও EXPIRATION কনফিগারেশন ==================
# আপনি চাইলে নতুন Key এবং Expiration Date (YYYY-MM-DD) যোগ করতে পারেন
ACTIVE_KEYS = {
    "CM-VIP-2026": "2026-12-31",
    "CODEMASTER-PRO": "2026-11-30",
    "MASTER-FREE": "2026-10-15"
}

AUTH_FILE = os.path.expanduser("~/.cm_auth")

def show_banner():
    os.system('clear')
    print(f"{CYAN}{BOLD}")
    print(r"""
  ____ ___  ____  _____   __  __    _    ____ _____ _____ ____  
 / ___/ _ \|  _ \| ____| |  \/  |  / \  / ___|_   _| ____|  _ \ 
| |  | | | | | | |  _|   | |\/| | / _ \ \___ \ | | |  _| | |_) |
| |__| |_| | |_| | |___  | |  | |/ ___ \ ___) || | | |___|  _ < 
 \____\___/|____/|_____| |_|  |_/_/   \_\____/ |_| |_____|_| \_\
    """)
    print(f"{YELLOW}          [+] চ্যানেল: কোড মাস্টার (CODE MASTER) [+]          ")
    print(f"{GREEN}          [+] HTML Instant Lifetime & Timer Host [+]         {RESET}")
    print("=" * 65)

def verify_key():
    """Key এবং এক্সপায়ার ডেট চেক করার সিস্টেম"""
    show_banner()
    saved_key = None

    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            saved_key = f.read().strip()

    if not saved_key or saved_key not in ACTIVE_KEYS:
        print(f"{BOLD}টুলটি ব্যবহারের জন্য সিকিউরিটি KEY প্রয়োজন।{RESET}")
        saved_key = input(f"{YELLOW}[?] আপনার KEY দিন: {RESET}").strip()

    # Key ভ্যালিডেশন
    if saved_key in ACTIVE_KEYS:
        exp_date_str = ACTIVE_KEYS[saved_key]
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()

        if today > exp_date:
            print(f"\n{RED}[!] এই KEY-টির মেয়াদ {exp_date_str} তারিখে শেষ (Expired) হয়ে গেছে!{RESET}")
            if os.path.exists(AUTH_FILE):
                os.remove(AUTH_FILE)
            sys.exit(1)
        else:
            # সফল হলে কী সেভ রাখা যাতে বারবার না চায়
            with open(AUTH_FILE, "w") as f:
                f.write(saved_key)
            print(f"\n{GREEN}[✓] KEY অনুমোদিত! মেয়াদের শেষ তারিখ: {exp_date_str}{RESET}")
            time.sleep(1.5)
    else:
        print(f"\n{RED}[!] ভুল KEY! সঠিক KEY সংগ্রহ করতে চ্যানেল অ্যাডমিনের সাথে যোগাযোগ করুন।{RESET}")
        sys.exit(1)

def random_domain():
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    return f"cm-{rand}.surge.sh"

def countdown_timer(minutes, domain):
    """টাইমার শেষ হলে লিংক স্বয়ংক্রিয়ভাবে মুছে দেওয়ার ফাংশন"""
    total_seconds = minutes * 60
    print(f"\n{YELLOW}[*] টাইমার চালু হয়েছে। {minutes} মিনিট পর সাইট স্বয়ংক্রিয়ভাবে ডিলিট হবে...{RESET}")
    try:
        while total_seconds > 0:
            mins, secs = divmod(total_seconds, 60)
            time_format = f"{mins:02d}:{secs:02d}"
            print(f"\r{CYAN}[⏳] লিঙ্কটির মেয়াদ বাকি: {BOLD}{time_format}{RESET} (বন্ধ করতে Ctrl+C)", end="")
            time.sleep(1)
            total_seconds -= 1

        print(f"\n\n{RED}[!] সময় শেষ! ওয়েবসাইটটি সার্ভার থেকে ডিলিট করা হচ্ছে...{RESET}")
        subprocess.run(f"surge teardown {domain}", shell=True, stdout=subprocess.DEVNULL)
        print(f"{GREEN}[✓] ওয়েবসাইটটি সফলভাবে ডিলিট করা হয়েছে!{RESET}")

    except KeyboardInterrupt:
        print(f"\n{RED}[!] ব্যবহারকারী দ্বারা টাইমার থামানো হয়েছে। সাইট রিমুভ করা হচ্ছে...{RESET}")
        subprocess.run(f"surge teardown {domain}", shell=True, stdout=subprocess.DEVNULL)
        print(f"{GREEN}[✓] লিঙ্ক বাতিল করা হয়েছে।{RESET}")

def main():
    verify_key()
    show_banner()

    print(f"{BOLD}হোস্টিং মোড সিলেক্ট করুন:{RESET}")
    print("1. পার্মানেন্ট মোড (লাইফটাইম - Termux কেটে দিলেও আজীবন লাইভ থাকবে)")
    print("2. কাস্টম টাইমার মোড (নির্দিষ্ট সময় পর লিঙ্ক স্বয়ংক্রিয় ডিলিট হবে)")
    
    choice = input(f"\n{BOLD}মোড নম্বর লিখুন (1/2): {RESET}").strip()
    timer_minutes = 0

    if choice == "2":
        try:
            timer_minutes = int(input(f"{YELLOW}[?] ওয়েবসাইটটি কত মিনিট লাইভ রাখতে চান? (যেমন: 10, 60): {RESET}"))
        except ValueError:
            print(f"{RED}[!] সঠিক সংখ্যা দিন!{RESET}")
            return
    elif choice != "1":
        print(f"{RED}[!] ভুল অপশন!{RESET}")
        return

    # HTML কোড ইনপুট নেওয়া
    print(f"\n{YELLOW}[+] আপনার সম্পূর্ণ HTML কোডটি নিচে পেস্ট করুন:{RESET}")
    print(f"{CYAN}(পেস্ট করার পর কিবোর্ডে একবার Enter চাপুন, তারপর Ctrl + D চাপুন){RESET}\n")

    try:
        html_code = sys.stdin.read()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] বাতিল করা হয়েছে।{RESET}")
        return

    if not html_code.strip():
        print(f"{RED}[!] কোনো কোড পাওয়া যায়নি!{RESET}")
        return

    # টেম্প ফাইল প্রিপারেশন
    deploy_dir = os.path.expanduser("~/cm_public_site")
    os.makedirs(deploy_dir, exist_ok=True)
    with open(os.path.join(deploy_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_code)

    domain = random_domain()
    print(f"\n{YELLOW}[*] ক্লাউডে ওয়েবসাইট স্থাপন করা হচ্ছে... অনুগ্রহ করে অপেক্ষা করুন...{RESET}\n")

    cmd = f"surge {deploy_dir} --domain {domain}"
    proc = subprocess.run(cmd, shell=True)

    if proc.returncode == 0:
        print("\n" + "=" * 65)
        print(f"{GREEN}{BOLD}🎉 অভিনন্দন! আপনার ওয়েবসাইট লাইভ হয়েছে!{RESET}")
        print(f"{CYAN}{BOLD}🌐 লাইভ লিঙ্ক: https://{domain}{RESET}")
        print("=" * 65)

        if choice == "1":
            print(f"{GREEN}[✓] এটি একটি পার্মানেন্ট লিঙ্ক। Termux কেটে দিলেও সবসময় কাজ করবে।{RESET}\n")
        elif choice == "2":
            countdown_timer(timer_minutes, domain)
    else:
        print(f"\n{RED}[!] হোস্টিং ব্যর্থ হয়েছে। ইন্টারনেট ও Surge লগইন চেক করুন।{RESET}")

if __name__ == "__main__":
    main()