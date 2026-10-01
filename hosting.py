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
    "MASTER-DEV-2026": "2026-12-31"
}

SESSION_CACHE = os.path.expanduser("~/.cm_auth_session")
DEPLOY_CACHE  = os.path.expanduser("~/.cm_deploy_runtime")

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
    else:
        print(f"\n{RED}[✗] ACCESS DENIED: Invalid license key.{RESET}")
        sys.exit(1)

def generate_subdomain():
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
            print(f"\r{CYAN}[⏳] REMAINING LIFESPAN: {WHITE}{BOLD}{time_display}{RESET} {DIM}(Abort with Ctrl+C){RESET}", end="")
            time.sleep(1)
            total_seconds -= 1

        print(f"\n\n{RED}[!] LIFESPAN ELAPSED: Initiating global server teardown...{RESET}")
        subprocess.run(f"surge teardown {domain_name}", shell=True, stdout=subprocess.DEVNULL)
        print(f"{GREEN}[✓] SUCCESS: Cloud host purged permanently.{RESET}\n")

    except KeyboardInterrupt:
        print(f"\n\n{RED}[!] MANUAL INTERRUPT DETECTED: Deleting cloud host immediately...{RESET}")
        subprocess.run(f"surge teardown {domain_name}", shell=True, stdout=subprocess.DEVNULL)
        print(f"{GREEN}[✓] SUCCESS: Session cleared and host terminated.{RESET}\n")

def main():
    check_dependencies()
    verify_license()
    render_banner()

    print(f"{BOLD}SELECT HOSTING ARCHITECTURE:{RESET}")
    print(f"{CYAN}[1]{WHITE} Permanent Mode  {DIM}➔ Infinite lifetime (survives app exit & restarts){RESET}")
    print(f"{CYAN}[2]{WHITE} Timed Session   {DIM}➔ Auto-terminates after a specified duration{RESET}")
    print(f"{CYAN}[0]{WHITE} Terminate CLI   {DIM}➔ Exit program{RESET}\n")

    mode_choice = input(f"{CYAN}╭─ [Select Mode: 1/2/0] ➔ {WHITE}").strip()

    if mode_choice == "0":
        print(f"\n{GREEN}[•] Thank you for using Code Master. Goodbye!{RESET}\n")
        sys.exit(0)

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

    subdomain = generate_subdomain()
    print(f"{YELLOW}[•] Provisioning cloud infrastructure... Please stand by...{RESET}\n")

    # Cloud deployment command
    cmd = f"surge {DEPLOY_CACHE} --domain {subdomain}"
    process = subprocess.run(cmd, shell=True)

    if process.returncode == 0:
        print("\n" + f"{GREEN}{BOLD}" + "=" * 62)
        print(f"       ★ DEPLOYMENT SUCCESSFUL - LIVE WEB HOST READY ★        ")
        print("=" * 62 + f"{RESET}")
        print(f"\n{BOLD}🌐 PUBLIC URL : {CYAN}https://{subdomain}{RESET}")
        print(f"{BOLD}🔒 PROTOCOL   : {GREEN}HTTPS (Encrypted / CDN Optimized){RESET}")
        
        if mode_choice == "1":
            print(f"{BOLD}⏳ RETENTION  : {YELLOW}PERMANENT (Active 24/7 indefinitely){RESET}")
            print(f"\n{DIM}[Tip] You can now safely close Termux. The link remains online globally.{RESET}\n")
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