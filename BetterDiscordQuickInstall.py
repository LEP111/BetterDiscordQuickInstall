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
import sys
import zipfile
import io


def setup_environment():
    if hasattr(sys, '_MEIPASS'):    # Pfad wenn .exe
        # Wenn als EXE ausgeführt, zeigt dies auf den temporären PyInstaller-Ordner
        base_path = sys._MEIPASS
    else:
        # Im normalen PyCharm/Script-Modus
        base_path = os.path.abspath(".")
    # Pfade
    bun_bin_path = os.path.join(base_path, "bin", "bun")

    new_path = f"{bun_bin_path};" + os.environ["PATH"]
    os.environ["PATH"] = new_path


def download_and_setup_bd(dir, zip_url):
    extract_path = dir

    print("Downloading BetterDiscord source...")
    r = requests.get(zip_url)

    if r.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(extract_path)

        # GitHubs Standard-Ordnername finden (z.B. BetterDiscord-main)
        downloaded_folder = os.path.join(extract_path, "BetterDiscord-main")
        target_folder = os.path.join(extract_path, "BetterDiscord")

        # Falls der Zielordner schon existiert, löschen
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder, onerror=remove_readonly)

        # Den Ordner von "BetterDiscord-main" in "BetterDiscord" umbenennen
        os.rename(downloaded_folder, target_folder)
        print("Setup complete. Folder is ready for Bun.")
    else:
        print("Download failed!")


def remove_readonly(func, path, _):
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
        return data.get("tag_name")
    else:
        return "No release found."


def get_current_version():
    with open(discord_dir + '\BetterDiscord\package.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('version')


setup_environment()
parser = configparser.ConfigParser()

if hasattr(sys, '_MEIPASS'):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(application_path, "config.cfg")

if not os.path.exists(config_path):
    print("Failed to read config.cfg")
    wait()
try:
    parser.read(config_path, encoding='utf-8')
    discord_dir = parser["DEFAULT"]["discord_dir"]
except Exception as e:
    print(e)
    print("Failed to read config.cfg")
    wait()

auto_start_dc = parser["DEFAULT"].getboolean("auto_start_dc")
copy_custom_ico = parser["DEFAULT"].getboolean("copy_custom_ico")
bd_url = parser["DEFAULT"]["bd_url"]
ico_dir = parser["DEFAULT"]["ico_dir"]
program_name = parser["DEFAULT"]["program_name"]
max_kill_tries = parser["DEFAULT"].getint("max_kill_tries")

betterdiscord_dir = discord_dir + r"\BetterDiscord"
current_version = ""
latest_version = ""

commands = [
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
        download_and_setup_bd(discord_dir, bd_url)
    except Exception as e:
        print(e)
        print("Failed to download form GitHub")
        wait()


for cmd in commands[0:2]:
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
    subprocess.run(commands[2], cwd=betterdiscord_dir, check=True)
    print("BetterDiscord installed successfully")
    if auto_start_dc:
        subprocess.Popen(discord_dir + r"\Update.exe --processStart " + program_name)
    wait()

else:
    print("Failed to kill Discord\nPlease close manually and run again")
    wait()
