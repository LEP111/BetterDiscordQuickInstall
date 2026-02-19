import subprocess
import os
import psutil
import shutil
import glob
import time
import configparser
import msvcrt
import requests
import json
import stat


def remove_readonly(func, path, _):
    """Löscht das Read-only-Attribut und versucht es erneut."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def wait():
    print("Press any key to continue")
    msvcrt.getch()
    quit()


def rebuild_icon_cache():
    print("Stopping Windows Explorer...")
    subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(2)

    local_appdata = os.getenv("LOCALAPPDATA")

    # Main icon cache
    icon_cache_db = os.path.join(local_appdata, "IconCache.db")
    if os.path.exists(icon_cache_db):
        os.remove(icon_cache_db)

    # Explorer icon cache folder
    explorer_cache = os.path.join(local_appdata, "Microsoft", "Windows", "Explorer")

    if os.path.exists(explorer_cache):
        for file in os.listdir(explorer_cache):
            if file.startswith("iconcache"):
                try:
                    os.remove(os.path.join(explorer_cache, file))
                except Exception:
                    pass

    print("Restarting Windows Explorer...")
    subprocess.Popen("explorer.exe")

    print("Icon cache rebuilt successfully.")


def is_program_running(name):
    for proc in psutil.process_iter(['name']):
        try:
            if name.lower() in proc.as_dict(attrs=['name'])['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_latest_version():
    url = f"https://api.github.com/repos/BetterDiscord/BetterDiscord/releases/latest"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # 'tag_name' ist meist die Versionsnummer (z.B. v1.2.3)
        return data.get("tag_name")
    else:
        return "Kein Release gefunden oder Fehler bei der Abfrage."


def get_current_version():
    with open(discord_dir + '\BetterDiscord\package.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('version')


parser = configparser.ConfigParser()

parser.read(r"config.cfg")

auto_start_dc = parser["DEFAULT"].getboolean("auto_start_dc")
copy_custom_ico = parser["DEFAULT"].getboolean("copy_custom_ico")
discord_dir = parser["DEFAULT"]["discord_dir"]
ico_dir = parser["DEFAULT"]["ico_dir"]
program_name = parser["DEFAULT"]["program_name"]
max_kill_tries = parser["DEFAULT"].getint("max_kill_tries")

betterdiscord_dir = discord_dir + r"\BetterDiscord"

commands = [
    ["git", "clone", "--single-branch", "-b", "main", "https://github.com/BetterDiscord/BetterDiscord.git"],
    ["bun", "install"],
    ["bun", "run", "build"],
    ["bun", "inject"]
]


try:
    latest_version = get_latest_version()                           # neuste version
    print(f"Newest Version: {latest_version}")
except Exception as e:
    print(e)
    print("Failed to request the newest version number")
    wait()

try:
    current_version = "v" + get_current_version()                         # aktuelle version
    print(f"Current Version: {current_version}")
except Exception as e:
    print(e)
    print("Failed to read the current version number")
    try:
        shutil.rmtree(betterdiscord_dir, onerror=remove_readonly)
    except:
        pass

if latest_version != current_version:
    try:
        shutil.rmtree(betterdiscord_dir, onerror=remove_readonly)
    except:
        pass
    subprocess.run(commands[0], cwd=discord_dir, check=True)  # Clone im Standard Ordner


for cmd in commands[1:3]:
    subprocess.run(cmd, cwd=betterdiscord_dir, check=True)
    time.sleep(1)


tries = 0
while is_program_running(program_name) and tries < max_kill_tries:       # Dc beenden
    tries += 1
    os.system("taskkill /F /im " + program_name)
    time.sleep(1)


if copy_custom_ico:
    try:                                                            # .ico kopieren
        shutil.copy2(ico_dir, discord_dir)
        muster = os.path.join(discord_dir, "app-*")
        for ordner in glob.glob(muster):
            if os.path.isdir(ordner):
                shutil.copy2(ico_dir, ordner)

        rebuild_icon_cache()

    except Exception as e:
        print(e)
        print('Failed to copy "app.ico"')
        time.sleep(5)


if not is_program_running(program_name):
    subprocess.run(commands[3], cwd=betterdiscord_dir, check=True)
    print("BetterDiscord installed successfully")
    if auto_start_dc:
        subprocess.Popen(discord_dir + r"\Update.exe --processStart " + program_name)
    wait()

else:
    print("Failed to kill Discord\nPlease close manually and run again")
    wait()
