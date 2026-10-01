#!/usr/bin/env python3
# ==============================================================================
# PROJECT     : CODE MASTER - CLOUD HTML DEPLOYER (ULTRA EDITION)
# AUTHOR      : CODE MASTER DEV TEAM
# ENVIRONMENT : TERMUX / LINUX / MACOS
# DESCRIPTION : INSTANT HTML-TO-URL DEPLOYMENT ENGINE (LIFETIME & TIMED)
# ==============================================================================

import os
import sys
import time
import random
import string
import datetime
import subprocess
import shutil
import hashlib
import json

# --- ANSI COLOR PALETTE ---
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"

# --- SECURITY LICENSE REPOSITORY ---
# Format: "LICENSE_KEY": "EXPIRATION_DATE (YYYY-MM-DD)"
ACTIVE_LICENSES = {
    "CM-VIP-2027": "2027-12-31",
    "CODEMASTER-ULTRA": "2028-06-30",
    "MASTER-DEV-2026": "2026-12-31",
    "PREMIUM-2026": "2026-12-31",
    "ELITE-EDITION": "2029-12-31"
}

SESSION_CACHE = os.path.expanduser("~/.cm_auth_session")
DEPLOY_CACHE  = os.path.expanduser("~/.cm_deploy_runtime")
CONFIG_FILE   = os.path.expanduser("~/.cm_config.json")

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def render_banner():
    clear_screen()
    print(f"{CYAN}{BOLD}")
    print(r"""
  ____ ___  ____  _____   __  __    _    ____ _____ _____ ____  
 / ___/ _ \|  _ \| ____| |  \/  |  / \  / ___|_   _| ____|  _ \ 
| |  | | | | | | |  _|   | |\/| | / _ \ \___ \ | | |  _| | |_) |
| |__| |_| | |_| | |___  | |  | |/ ___ \ ___) || | | |___|  _ < 
 \____\___/|____/|_____| |_|  |_/_/   \_\____/ |_| |_____|_| \_\
    """)
    print(f"{WHITE}{BOLD} ╭───────────────────────────────────────────────────────────╮")
    print(f" │  {YELLOW}CHANNEL : CODE MASTER OFFICIAL{WHITE}                          │")
    print(f" │  {GREEN}MODULE  : ADVANCED HTML CLOUD DEPLOYMENT SYSTEM{WHITE}          │")
    print(f" │  {MAGENTA}STATUS  : ENTERPRISE CLI ENGINE{WHITE}                          │")
    print(f" ╰───────────────────────────────────────────────────────────╯{RESET}\n")

def check_dependencies():
    """Validates if Node.js & Surge are installed."""
    if not shutil.which("surge"):
        print(f"{RED}[✗] ERROR: Surge CLI engine is not installed.{RESET}")
        print(f"{YELLOW}[•] Run command: {WHITE}npm install -g surge{RESET}")
        sys.exit(1)

def save_config(data):
    """সংরক্ষণ সমস্ত কনফিগারেশন ডেটা JSON ফাইলে"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"{RED}[✗] Config save failed: {str(e)}{RESET}")

def load_config():
    """লোড করুন সংরক্ষিত কনফিগারেশন"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def verify_license():
    """Authenticates tool license and checks expiration thresholds."""
    saved_key = None
    if os.path.exists(SESSION_CACHE):
        try:
            with open(SESSION_CACHE, "r", encoding="utf-8") as f:
                saved_key = f.read().strip()
        except Exception:
            saved_key = None

    if not saved_key or saved_key not in ACTIVE_LICENSES:
        render_banner()
        print(f"{YELLOW}[?] AUTHENTICATION REQUIRED{RESET}")
        print(f"{DIM}Enter your authorized VIP license key to proceed.{RESET}\n")
        saved_key = input(f"{CYAN}╭─ [License Key] ➔ {WHITE}").strip()
        print(f"{RESET}", end="")

    if saved_key in ACTIVE_LICENSES:
        exp_date_str = ACTIVE_LICENSES[saved_key]
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()

        if today > exp_date:
            print(f"\n{RED}[✗] LICENSE EXPIRED!{RESET}")
            print(f"{DIM}This key expired on: {exp_date_str}. Contact Administrator.{RESET}")
            if os.path.exists(SESSION_CACHE):
                os.remove(SESSION_CACHE)
            sys.exit(1)
        else:
            with open(SESSION_CACHE, "w", encoding="utf-8") as f:
                f.write(saved_key)
            print(f"\n{GREEN}[✓] LICENSE VERIFIED! Valid until: {exp_date_str}{RESET}")
            time.sleep(1)
            return saved_key
    else:
        print(f"\n{RED}[✗] ACCESS DENIED: Invalid license key.{RESET}")
        sys.exit(1)

def generate_subdomain(custom_name=None):
    """জেনারেট করুন রেন্ডম সাবডোমেইন"""
    if custom_name:
        return f"{custom_name}.surge.sh"
    unique_hash = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"cm-app-{unique_hash}.surge.sh"

def collect_html_payload():
    """Reads HTML input dynamically until 'DONE' or EOF is detected."""
    print(f"\n{YELLOW}[+] PASTE YOUR HTML SOURCE CODE BELOW:{RESET}")
    print(f"{DIM}Tip: Once pasted, hit [Enter], type {BOLD}'DONE'{RESET}{DIM} on a new line, and hit [Enter].{RESET}\n")
    print(f"{CYAN}--- BEGIN PAYLOAD INPUT ---{RESET}")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break

    print(f"{CYAN}--- END PAYLOAD INPUT ---{RESET}\n")
    payload = "\n".join(lines)
    return payload.strip()

def countdown_engine(duration_minutes, domain_name):
    """Monitors link runtime and executes automated teardown upon expiry."""
    total_seconds = duration_minutes * 60
    print(f"\n{YELLOW}[⚡] TIMER ENGAGED: Auto-destruction in {duration_minutes} minute(s)...{RESET}")
    
    try:
        while total_seconds > 0:
            mins, secs = divmod(total_seconds, 60)
            time_display = f"{mins:02d}:{secs:02d}"
            print(f"\r{CYAN}[⏳] REMAINING LIFESPAN: {WHITE}{BOLD}{time_display}{RESET} {DIM}(Abort with Ctrl+C){RESET}", end="", flush=True)
            time.sleep(1)
            total_seconds -= 1

        print(f"\n\n{RED}[!] LIFESPAN ELAPSED: Initiating global server teardown...{RESET}")
        subprocess.run(f"surge teardown {domain_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}[✓] SUCCESS: Cloud host purged permanently.{RESET}\n")

    except KeyboardInterrupt:
        print(f"\n\n{RED}[!] MANUAL INTERRUPT DETECTED: Deleting cloud host immediately...{RESET}")
        subprocess.run(f"surge teardown {domain_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}[✓] SUCCESS: Session cleared and host terminated.{RESET}\n")

def display_deployment_summary(url, mode, duration=0, license_key=""):
    """প্রদর্শন করুন সুন্দর ডিপ্লয়মেন্ট সামারি"""
    print("\n" + f"{GREEN}{BOLD}" + "=" * 70)
    print(f"       ★ DEPLOYMENT SUCCESSFUL - LIVE WEB HOST READY ★        ")
    print("=" * 70 + f"{RESET}")
    
    print(f"\n{BOLD}📊 DEPLOYMENT DETAILS:{RESET}")
    print(f"  {CYAN}├─ 🌐 PUBLIC URL    : {WHITE}{url}{RESET}")
    print(f"  {CYAN}├─ 🔒 PROTOCOL      : {GREEN}HTTPS (Encrypted / CDN Optimized){RESET}")
    print(f"  {CYAN}├─ 🎫 LICENSE KEY   : {YELLOW}{license_key}{RESET}")
    print(f"  {CYAN}├─ ⏳ MODE          : {MAGENTA}{'PERMANENT (24/7 Active)' if mode == '1' else f'TIMED ({duration} Minutes)'}{RESET}")
    print(f"  {CYAN}└─ 📅 DEPLOYED AT   : {WHITE}{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    print(f"\n{BOLD}💡 QUICK TIPS:{RESET}")
    if mode == "1":
        print(f"  {DIM}✓ Site remains online permanently (24/7 globally accessible){RESET}")
        print(f"  {DIM}✓ You can safely close this terminal or restart your device{RESET}")
        print(f"  {DIM}✓ Share the URL with anyone - it will remain active{RESET}")
    else:
        print(f"  {DIM}✓ Site will auto-destruct after {duration} minute(s){RESET}")
        print(f"  {DIM}✓ Keep this terminal running for timed mode to work{RESET}")
        print(f"  {DIM}✓ Use Ctrl+C to manually terminate early{RESET}")
    
    print(f"\n{BOLD}🎯 NEXT STEPS:{RESET}")
    print(f"  {CYAN}1. {WHITE}Copy the URL above and share it{RESET}")
    print(f"  {CYAN}2. {WHITE}Open in any browser (mobile/desktop){RESET}")
    print(f"  {CYAN}3. {WHITE}No installation needed on client-side{RESET}\n")

def manage_deployments():
    """পরিচালনা করুন বর্তমান ডিপ্লয়মেন্ট"""
    config = load_config()
    if "deployments" not in config:
        config["deployments"] = []
    
    deployments = config.get("deployments", [])
    
    if deployments:
        print(f"\n{YELLOW}[•] PREVIOUS DEPLOYMENTS:{RESET}\n")
        for i, dep in enumerate(deployments, 1):
            print(f"{CYAN}[{i}]{RESET} {dep.get('url')} - {dep.get('mode')} - {dep.get('timestamp')}")
        print()
    else:
        print(f"\n{DIM}[•] No previous deployments found.{RESET}\n")

def main():
    check_dependencies()
    license_key = verify_license()
    render_banner()

    print(f"{BOLD}SELECT HOSTING ARCHITECTURE:{RESET}")
    print(f"{CYAN}[1]{WHITE} Permanent Mode  {DIM}➔ Infinite lifetime (survives app exit & restarts){RESET}")
    print(f"{CYAN}[2]{WHITE} Timed Session   {DIM}➔ Auto-terminates after a specified duration{RESET}")
    print(f"{CYAN}[3]{WHITE} View History    {DIM}➔ Show previous deployments{RESET}")
    print(f"{CYAN}[0]{WHITE} Terminate CLI   {DIM}➔ Exit program{RESET}\n")

    mode_choice = input(f"{CYAN}╭─ [Select Mode: 1/2/3/0] ➔ {WHITE}").strip()

    if mode_choice == "0":
        print(f"\n{GREEN}[•] Thank you for using Code Master. Goodbye!{RESET}\n")
        sys.exit(0)
    
    if mode_choice == "3":
        manage_deployments()
        return

    timer_minutes = 0
    if mode_choice == "2":
        try:
            timer_minutes = int(input(f"{CYAN}╭─ [Duration in Minutes] ➔ {WHITE}"))
            if timer_minutes <= 0:
                print(f"{RED}[✗] Invalid duration.{RESET}")
                return
        except ValueError:
            print(f"{RED}[✗] Numeric input required.{RESET}")
            return
    elif mode_choice != "1":
        print(f"{RED}[✗] Invalid option selected.{RESET}")
        return

    # Custom domain option
    custom_domain = input(f"{CYAN}╭─ [Custom Domain (optional, press Enter for random)] ➔ {WHITE}").strip()

    # Process HTML input
    html_code = collect_html_payload()
    if not html_code:
        print(f"{RED}[✗] ABORTED: No HTML payload detected.{RESET}")
        return

    # Workspace directory preparation
    os.makedirs(DEPLOY_CACHE, exist_ok=True)
    index_path = os.path.join(DEPLOY_CACHE, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    subdomain = generate_subdomain(custom_domain if custom_domain else None)
    print(f"{YELLOW}[•] Provisioning cloud infrastructure... Please stand by...{RESET}\n")

    # Cloud deployment command
    cmd = f"surge {DEPLOY_CACHE} --domain {subdomain}"
    process = subprocess.run(cmd, shell=True)

    if process.returncode == 0:
        full_url = f"https://{subdomain}"
        
        # Save deployment info
        config = load_config()
        if "deployments" not in config:
            config["deployments"] = []
        
        config["deployments"].append({
            "url": full_url,
            "mode": "PERMANENT" if mode_choice == "1" else f"TIMED ({timer_minutes} mins)",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "license": license_key
        })
        save_config(config)
        
        display_deployment_summary(full_url, mode_choice, timer_minutes, license_key)
        
        if mode_choice == "1":
            pass
        elif mode_choice == "2":
            countdown_engine(timer_minutes, subdomain)
    else:
        print(f"\n{RED}[✗] DEPLOYMENT FAILED: Check internet connection or Surge credentials.{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[!] Session aborted by operator.{RESET}\n")
        sys.exit(0)