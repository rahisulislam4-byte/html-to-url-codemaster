#!/usr/bin/env python3
# ==============================================================================
# CODE MASTER v3.0 - PROFESSIONAL HTML HOSTING SYSTEM
# ETeam71 | Persistent Cloud & Local Hosting with Custom Domains & Versioning
# ==============================================================================

import os
import sys
import json
import time
import datetime
import hashlib
import uuid
import threading
import socket
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import re
import base64
import subprocess
import shutil

# ============================================================================
# ANSI COLOR CODES
# ============================================================================
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

# ============================================================================
# STORAGE & CONFIGURATION
# ============================================================================
STORAGE_BASE = os.path.expanduser("~/.codemaster")
PROJECTS_DIR = os.path.join(STORAGE_BASE, "projects")
CONFIG_FILE = os.path.join(STORAGE_BASE, "config.json")
REGISTRY_FILE = os.path.join(STORAGE_BASE, "registry.json")
AUTH_FILE = os.path.join(STORAGE_BASE, ".auth_session")

DEFAULT_CONFIG = {
    "server_port": 8080,
    "max_file_size_mb": 10,
    "branding_name": "CODE MASTER",
    "branding_team": "ETeam71",
    "telegram_channel": "@ETeam71_Official",
    "custom_domain": "localhost:8080",
    "expiry_options": ["1 Hour", "1 Day", "7 Days", "30 Days", "90 Days", "1 Year", "Lifetime"],
}

# ACTIVE SECURITY LICENSES
ACTIVE_LICENSES = {
    "CM-VIP-2027": "2027-12-31",
    "CODEMASTER-ULTRA": "2028-06-30",
    "MASTER-DEV-2026": "2026-12-31",
    "ETEAM71-PRO": "2027-06-30"
}

# ============================================================================
# INITIALIZATION
# ============================================================================

def init_storage():
    """Initialize storage directories and config files."""
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    
    if not os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

def load_config():
    """Load configuration from file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def load_registry():
    """Load project registry."""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_registry(registry):
    """Save project registry."""
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_screen():
    """Clear terminal screen."""
    os.system("clear" if os.name != "nt" else "cls")

def generate_project_id():
    """Generate unique project ID."""
    return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:10]

def get_current_time():
    """Get current time in ISO format."""
    return datetime.datetime.now().isoformat()

def validate_html(html_content):
    """Validate HTML content."""
    if not html_content or not html_content.strip():
        return False, "HTML content cannot be empty"
    
    if len(html_content.encode('utf-8')) > 50 * 1024 * 1024:  # 50MB limit
        return False, "HTML content exceeds 50MB limit"
    
    return True, "Valid HTML"

def get_expiry_timestamp(expiry_option):
    """Convert expiry option to timestamp."""
    now = datetime.datetime.now()
    expiry_map = {
        "1 Hour": now + datetime.timedelta(hours=1),
        "1 Day": now + datetime.timedelta(days=1),
        "7 Days": now + datetime.timedelta(days=7),
        "30 Days": now + datetime.timedelta(days=30),
        "90 Days": now + datetime.timedelta(days=90),
        "1 Year": now + datetime.timedelta(days=365),
        "Lifetime": datetime.datetime(2099, 12, 31),
    }
    return expiry_map.get(expiry_option, now + datetime.timedelta(days=30)).isoformat()

def is_project_expired(expiry_date):
    """Check if project has expired."""
    if "2099-12-31" in expiry_date:
        return False
    try:
        expiry = datetime.datetime.fromisoformat(expiry_date)
        return datetime.datetime.now() > expiry
    except Exception:
        return False

def get_expiry_status(expiry_date):
    """Get expiry status string."""
    if "2099-12-31" in expiry_date:
        return f"{Colors.GREEN}PERMANENT (LIFETIME){Colors.RESET}"
    
    try:
        expiry = datetime.datetime.fromisoformat(expiry_date)
        now = datetime.datetime.now()
        if now > expiry:
            return f"{Colors.RED}EXPIRED{Colors.RESET}"
        
        remaining = expiry - now
        days = remaining.days
        hours = remaining.seconds // 3600
        mins = (remaining.seconds % 3600) // 60
        if days > 0:
            return f"{Colors.YELLOW}{days}d {hours}h remaining{Colors.RESET}"
        return f"{Colors.YELLOW}{hours}h {mins}m remaining{Colors.RESET}"
    except Exception:
        return f"{Colors.DIM}UNKNOWN{Colors.RESET}"

# ============================================================================
# BANNERS & OUTPUTS
# ============================================================================

def print_main_banner():
    """Print main banner."""
    clear_screen()
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print(r"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                    CODE MASTER v3.0                            ║
    ║                       ETeam71                                  ║
    ║            Professional HTML Hosting System                    ║
    ║         Persistent Cloud Hosting with Custom Domains           ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    config = load_config()
    print(f"{Colors.MAGENTA}📱 Official Channel: {config['telegram_channel']}{Colors.RESET}")
    print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

# ============================================================================
# SECURITY / LICENSE SYSTEM
# ============================================================================

def verify_license():
    """Authenticates tool license and checks expiration."""
    saved_key = None
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                saved_key = f.read().strip()
        except Exception:
            saved_key = None

    if not saved_key or saved_key not in ACTIVE_LICENSES:
        print_main_banner()
        print(f"{Colors.YELLOW}[?] AUTHENTICATION REQUIRED{Colors.RESET}")
        print(f"{Colors.DIM}Enter an authorized VIP license key to proceed.{Colors.RESET}\n")
        saved_key = input(f"{Colors.CYAN}╭─ [License Key] ➔ {Colors.WHITE}").strip()
        print(f"{Colors.RESET}", end="")

    if saved_key in ACTIVE_LICENSES:
        exp_date_str = ACTIVE_LICENSES[saved_key]
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()

        if today > exp_date:
            print_error(f"License Key Expired on {exp_date_str}! Contact Admin.")
            if os.path.exists(AUTH_FILE):
                os.remove(AUTH_FILE)
            sys.exit(1)
        else:
            with open(AUTH_FILE, "w", encoding="utf-8") as f:
                f.write(saved_key)
            print_success(f"License Verified! Valid until: {exp_date_str}")
            time.sleep(0.6)
    else:
        print_error("ACCESS DENIED: Invalid license key.")
        sys.exit(1)

# ============================================================================
# PROJECT MANAGEMENT
# ============================================================================

def create_project(project_name, html_content, expiry_option, custom_url=None):
    """Create new hosting project."""
    valid, msg = validate_html(html_content)
    if not valid:
        return None, msg
    
    project_id = generate_project_id()
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    current_dir = os.path.join(project_dir, "current")
    versions_dir = os.path.join(project_dir, "versions")
    
    os.makedirs(current_dir, exist_ok=True)
    os.makedirs(versions_dir, exist_ok=True)
    
    # Save current version
    index_path = os.path.join(current_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Save version 1
    v1_dir = os.path.join(versions_dir, "v1")
    os.makedirs(v1_dir, exist_ok=True)
    with open(os.path.join(v1_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    
    expiry_timestamp = get_expiry_timestamp(expiry_option)
    config = load_config()
    
    live_url = custom_url if custom_url else f"http://{config['custom_domain']}/site/{project_id}"
    
    project_data = {
        "project_id": project_id,
        "project_name": project_name,
        "live_url": live_url,
        "status": "Active",
        "current_version": 1,
        "created_date": get_current_time(),
        "updated_date": get_current_time(),
        "expiry_date": expiry_timestamp,
        "hosting_plan": expiry_option,
        "version_count": 1,
        "disabled": False,
        "custom_url": live_url
    }
    
    metadata_file = os.path.join(project_dir, "metadata.json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2)
    
    registry = load_registry()
    registry[project_id] = project_data
    save_registry(registry)
    
    return project_id, project_data

def list_projects():
    """List all active projects."""
    registry = load_registry()
    return [data for data in registry.values() if not data.get("disabled")]

def get_project(project_id):
    """Get project details."""
    registry = load_registry()
    return registry.get(project_id)

def update_project(project_id, new_html):
    """Update project with new HTML (maintains same URL)."""
    registry = load_registry()
    project = registry.get(project_id)
    if not project:
        return False, "Project not found"
    
    valid, msg = validate_html(new_html)
    if not valid:
        return False, msg
    
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    current_dir = os.path.join(project_dir, "current")
    versions_dir = os.path.join(project_dir, "versions")
    
    next_version = project.get("current_version", 1) + 1
    
    # Save to versions
    version_dir = os.path.join(versions_dir, f"v{next_version}")
    os.makedirs(version_dir, exist_ok=True)
    with open(os.path.join(version_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(new_html)
    
    # Update current
    with open(os.path.join(current_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(new_html)
    
    project["current_version"] = next_version
    project["updated_date"] = get_current_time()
    project["version_count"] = next_version
    project["status"] = "Active"
    
    metadata_file = os.path.join(project_dir, "metadata.json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2)
    
    registry[project_id] = project
    save_registry(registry)
    
    return True, f"Successfully updated to Version {next_version}"

def get_project_versions(project_id):
    """Get all versions of a project."""
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    versions_dir = os.path.join(project_dir, "versions")
    if not os.path.exists(versions_dir):
        return []
    
    versions = []
    for v in sorted(os.listdir(versions_dir)):
        v_path = os.path.join(versions_dir, v, "index.html")
        if os.path.exists(v_path):
            versions.append(v)
    return versions

def restore_version(project_id, version):
    """Restore a previous version (maintains same URL)."""
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    version_path = os.path.join(project_dir, "versions", version, "index.html")
    current_path = os.path.join(project_dir, "current", "index.html")
    
    if not os.path.exists(version_path):
        return False, "Version archive not found"
    
    with open(version_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    with open(current_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    registry = load_registry()
    project = registry.get(project_id)
    if project:
        project["updated_date"] = get_current_time()
        project["status"] = "Active"
        metadata_file = os.path.join(project_dir, "metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2)
        registry[project_id] = project
        save_registry(registry)
    
    return True, f"Project restored to {version}"

def extend_hosting(project_id, new_expiry_option):
    """Extend hosting expiry."""
    registry = load_registry()
    project = registry.get(project_id)
    if not project:
        return False, "Project not found"
    
    new_expiry = get_expiry_timestamp(new_expiry_option)
    project["expiry_date"] = new_expiry
    project["hosting_plan"] = new_expiry_option
    project["updated_date"] = get_current_time()
    
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    metadata_file = os.path.join(project_dir, "metadata.json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2)
    
    registry[project_id] = project
    save_registry(registry)
    
    return True, f"Hosting extended: {new_expiry_option}"

def change_custom_domain(project_id, new_domain):
    """Change custom domain (keeps everything else same)."""
    registry = load_registry()
    project = registry.get(project_id)
    if not project:
        return False, "Project not found"
    
    clean_domain = new_domain.replace("https://", "").replace("http://", "").strip("/")
    if not clean_domain or len(clean_domain) < 3:
        return False, "Invalid domain specified"
    
    project["custom_url"] = f"https://{clean_domain}" if "." in clean_domain else clean_domain
    project["live_url"] = project["custom_url"]
    project["updated_date"] = get_current_time()
    
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    metadata_file = os.path.join(project_dir, "metadata.json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2)
    
    registry[project_id] = project
    save_registry(registry)
    return True, f"Domain changed to {project['custom_url']}"

def delete_project(project_id):
    """Delete project permanently."""
    registry = load_registry()
    if project_id in registry:
        del registry[project_id]
        save_registry(registry)
    
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir, ignore_errors=True)
    return True, "Project deleted permanently"

# ============================================================================
# HTTP SERVER ROUTER
# ============================================================================

class CodeMasterHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip("/")
        
        # Format: /site/<project_id>
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "site":
            project_id = parts[1]
            registry = load_registry()
            project = registry.get(project_id)
            
            if not project or project.get("disabled"):
                self.send_error(404, "Site Not Found")
                return
            
            if is_project_expired(project.get("expiry_date", "")):
                self.send_response(410)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<h1>410 - Link Expired</h1><p>This hosting session has ended.</p>")
                return
            
            file_path = os.path.join(PROJECTS_DIR, project_id, "current", "index.html")
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
        
        # Root welcome
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        welcome_html = f"""
        <html>
        <head><title>Code Master Server</title></head>
        <body style="font-family:sans-serif;text-align:center;padding:50px;background:#0f172a;color:#fff;">
            <h1>Code Master Cloud Server v3.0</h1>
            <p>Server Engine Active & Healthy</p>
        </body>
        </html>
        """
        self.wfile.write(welcome_html.encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Suppress default server console spam

def start_server_daemon(port=8080):
    """Run local hosting server in background thread."""
    def run():
        try:
            server = HTTPServer(("0.0.0.0", port), CodeMasterHTTPHandler)
            server.serve_forever()
        except Exception:
            pass
    t = threading.Thread(target=run, daemon=True)
    t.start()

# ============================================================================
# CLOUD SURGE INTEGRATION (PUBLIC LIFETIME LINK)
# ============================================================================

def deploy_to_surge(project_id, custom_subdomain=None):
    """Deploy project to Surge cloud for world-wide public HTTPS URL."""
    if not shutil.which("surge"):
        return False, "Surge is not installed (run 'npm install -g surge')"
    
    current_dir = os.path.join(PROJECTS_DIR, project_id, "current")
    if not os.path.exists(current_dir):
        return False, "Project files missing"
    
    if custom_subdomain:
        clean = custom_subdomain.replace("https://", "").replace("http://", "").strip("/")
        domain = clean if ("." in clean) else f"{clean}.surge.sh"
    else:
        domain = f"cm-{project_id}.surge.sh"
    
    # Write CNAME
    with open(os.path.join(current_dir, "CNAME"), "w", encoding="utf-8") as f:
        f.write(domain)
    
    cmd = f"surge {current_dir} --domain {domain}"
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if proc.returncode == 0:
        full_url = f"https://{domain}"
        change_custom_domain(project_id, full_url)
        return True, full_url
    return False, "Surge deployment failed. Check internet/login."

# ============================================================================
# INPUT CAPTURE
# ============================================================================

def get_multiline_html():
    """Reads HTML input dynamically until 'DONE' or EOF is detected."""
    print(f"\n{Colors.YELLOW}[+] PASTE YOUR HTML SOURCE CODE BELOW:{Colors.RESET}")
    print(f"{Colors.DIM}Tip: Paste code, hit [Enter], type {Colors.BOLD}'DONE'{Colors.RESET}{Colors.DIM} on a new line, and hit [Enter].{Colors.RESET}\n")
    print(f"{Colors.CYAN}--- BEGIN PAYLOAD ---{Colors.RESET}")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break

    print(f"{Colors.CYAN}--- END PAYLOAD ---{Colors.RESET}\n")
    return "\n".join(lines).strip()

# ============================================================================
# USER INTERACTION MENUS
# ============================================================================

def handle_create_project():
    print_main_banner()
    print(f"{Colors.BOLD}DEPLOY NEW HOSTING PROJECT{Colors.RESET}\n")
    
    name = input(f"{Colors.CYAN}Project Name: {Colors.WHITE}").strip()
    if not name:
        name = "Untitled Project"
    
    html = get_multiline_html()
    if not html:
        print_error("Deployment cancelled: No HTML code provided.")
        time.sleep(1.5)
        return
    
    config = load_config()
    print(f"\n{Colors.BOLD}Select Hosting Validity Plan:{Colors.RESET}")
    for idx, opt in enumerate(config["expiry_options"], 1):
        print(f"[{idx}] {opt}")
    
    choice = input(f"\n{Colors.CYAN}Option (1-{len(config['expiry_options'])}): {Colors.WHITE}").strip()
    try:
        plan = config["expiry_options"][int(choice) - 1]
    except Exception:
        plan = "Lifetime"
    
    print(f"\n{Colors.BOLD}Choose Deployment Route:{Colors.RESET}")
    print(f"[{Colors.GREEN}1{Colors.RESET}] Public Global Cloud (Surge HTTPS Link - Active Worldwide)")
    print(f"[{Colors.CYAN}2{Colors.RESET}] Local Server Route (localhost)")
    deploy_route = input(f"\n{Colors.CYAN}Select Route (1/2): {Colors.WHITE}").strip()
    
    pid, pdata = create_project(name, html, plan)
    
    if deploy_route == "1":
        print_info("Connecting to Cloud Surge Infrastructure...")
        sub = input(f"{Colors.CYAN}Custom Subdomain (Leave blank for auto): {Colors.WHITE}").strip()
        success, url_or_msg = deploy_to_surge(pid, sub if sub else None)
        if success:
            print_success(f"Deployed Worldwide at: {url_or_msg}")
        else:
            print_warning(f"Cloud fallback: {url_or_msg}")
            print_info(f"Local Access: {pdata['live_url']}")
    else:
        print_success(f"Project deployed locally at: {pdata['live_url']}")
    
    input(f"\n{Colors.DIM}Press Enter to return to menu...{Colors.RESET}")

def handle_update_project():
    print_main_banner()
    projects = list_projects()
    if not projects:
        print_warning("No active projects found to update.")
        time.sleep(1.5)
        return
    
    print(f"{Colors.BOLD}SELECT PROJECT TO UPDATE (Same URL will be preserved):{Colors.RESET}\n")
    for idx, p in enumerate(projects, 1):
        print(f"[{idx}] {p['project_name']} (ID: {p['project_id']}) - v{p['current_version']}")
        print(f"    URL: {Colors.CYAN}{p['live_url']}{Colors.RESET}")
    
    choice = input(f"\n{Colors.CYAN}Select project number: {Colors.WHITE}").strip()
    try:
        selected = projects[int(choice) - 1]
    except Exception:
        print_error("Invalid selection.")
        time.sleep(1)
        return
    
    new_html = get_multiline_html()
    if not new_html:
        print_error("Update cancelled: Empty payload.")
        time.sleep(1.5)
        return
    
    success, msg = update_project(selected["project_id"], new_html)
    if success:
        print_success(msg)
        if "surge.sh" in selected["live_url"]:
            print_info("Syncing updates to Global Cloud...")
            deploy_to_surge(selected["project_id"], selected["live_url"])
            print_success(f"Cloud URL is refreshed: {selected['live_url']}")
    else:
        print_error(msg)
    
    input(f"\n{Colors.DIM}Press Enter to return to menu...{Colors.RESET}")

def handle_list_projects():
    print_main_banner()
    projects = list_projects()
    if not projects:
        print_warning("No active projects found in repository.")
    else:
        print(f"{Colors.BOLD}ACTIVE HOSTED SITES ({len(projects)} Total):{Colors.RESET}\n")
        for idx, p in enumerate(projects, 1):
            exp_status = get_expiry_status(p.get("expiry_date", ""))
            print(f"{Colors.BOLD}#{idx}. {p['project_name']}{Colors.RESET} (ID: {p['project_id']})")
            print(f"   🌐 URL      : {Colors.CYAN}{p['live_url']}{Colors.RESET}")
            print(f"   📦 Version  : v{p['current_version']} (Total Versions: {p.get('version_count', 1)})")
            print(f"   ⏳ Expiry   : {exp_status}")
            print(f"   📅 Created  : {p['created_date'][:10]}\n")
    
    input(f"{Colors.DIM}Press Enter to return to menu...{Colors.RESET}")

def handle_manage_project():
    print_main_banner()
    projects = list_projects()
    if not projects:
        print_warning("No projects available to manage.")
        time.sleep(1.5)
        return
    
    for idx, p in enumerate(projects, 1):
        print(f"[{idx}] {p['project_name']} (ID: {p['project_id']}) - {p['live_url']}")
    
    choice = input(f"\n{Colors.CYAN}Select project to manage: {Colors.WHITE}").strip()
    try:
        p = projects[int(choice) - 1]
    except Exception:
        print_error("Invalid selection.")
        time.sleep(1)
        return
    
    pid = p["project_id"]
    print(f"\n{Colors.BOLD}Actions for '{p['project_name']}':{Colors.RESET}")
    print("[1] Restore a Previous Version")
    print("[2] Extend Expiry Date")
    print("[3] Change Custom Domain / URL")
    print("[4] Delete Project Permanently")
    print("[0] Back")
    
    act = input(f"\n{Colors.CYAN}Select Action (1-4): {Colors.WHITE}").strip()
    if act == "1":
        versions = get_project_versions(pid)
        print(f"\nAvailable versions: {', '.join(versions)}")
        v = input("Version to restore (e.g. v1): ").strip()
        ok, msg = restore_version(pid, v)
        print_success(msg) if ok else print_error(msg)
    elif act == "2":
        config = load_config()
        for i, opt in enumerate(config["expiry_options"], 1):
            print(f"[{i}] {opt}")
        sel = input("Select plan: ").strip()
        try:
            plan = config["expiry_options"][int(sel) - 1]
            ok, msg = extend_hosting(pid, plan)
            print_success(msg) if ok else print_error(msg)
        except Exception:
            print_error("Invalid plan.")
    elif act == "3":
        new_dom = input("Enter new domain / URL: ").strip()
        ok, msg = change_custom_domain(pid, new_dom)
        print_success(msg) if ok else print_error(msg)
    elif act == "4":
        confirm = input(f"Type 'DELETE' to confirm deletion of {p['project_name']}: ").strip()
        if confirm == "DELETE":
            delete_project(pid)
            print_success("Project deleted.")
    
    time.sleep(1.5)

# ============================================================================
# MAIN ENTRY
# ============================================================================

def main():
    init_storage()
    verify_license()
    
    config = load_config()
    start_server_daemon(config.get("server_port", 8080))
    
    while True:
        print_main_banner()
        print(f"{Colors.BOLD}CORE SYSTEM MENU:{Colors.RESET}")
        print(f"[{Colors.GREEN}1{Colors.RESET}] Deploy New HTML Project        {Colors.DIM}(Lifetime or Timed Cloud/Local){Colors.RESET}")
        print(f"[{Colors.CYAN}2{Colors.RESET}] Update Existing Project        {Colors.DIM}(Preserves Same Live Link){Colors.RESET}")
        print(f"[{Colors.YELLOW}3{Colors.RESET}] Active Projects Dashboard      {Colors.DIM}(View Details, URLs, Status){Colors.RESET}")
        print(f"[{Colors.MAGENTA}4{Colors.RESET}] Version & Domain Management    {Colors.DIM}(Rollback, Extend, Custom Domain){Colors.RESET}")
        print(f"[{Colors.RED}0{Colors.RESET}] Exit System\n")
        
        choice = input(f"{Colors.CYAN}╭─ [Select Operation] ➔ {Colors.WHITE}").strip()
        
        if choice == "1":
            handle_create_project()
        elif choice == "2":
            handle_update_project()
        elif choice == "3":
            handle_list_projects()
        elif choice == "4":
            handle_manage_project()
        elif choice == "0":
            clear_screen()
            print(f"{Colors.GREEN}Exiting Code Master v3.0. Goodbye!{Colors.RESET}\n")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Session halted by user.{Colors.RESET}\n")
        sys.exit(0)