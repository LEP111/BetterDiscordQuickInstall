# BetterDiscordQuickInstall
This is a small project of mine to quickly install BetterDiscord and set a custom icon for discord 
of your choice.
Its written completely in python.
# What it does
It downloads BetterDiscord from the official [GitHub](https://github.com/BetterDiscord/BetterDiscord),
installs the needed resources, builds it and finally injects it.

As a nice to have, you can activate the copy icon funktion to set a custom Discord icon.
It will automatically reload the cache (the screen will most likely turn black for a sec).
# How it works
It runs the official [BetterDiscord Manual Installation](https://docs.betterdiscord.app/users/getting-started/installation#manual-installation) \
`git clone --single-branch -b main https://github.com/BetterDiscord/BetterDiscord.git` \
`cd BetterDiscord`\
`bun install`\
`bun run build`\
`bun inject`
# Config
I wouldn't suggest changing the `config.cfg` besides of
`auto_start_dc` `copy_custom_ico` `discord_dir`\

`auto_start_dc` True: Starts Discord automatically after installation\
`copy_custom_ico` True: Copies `app.ico` from root to `Discord` and `app-*` folder\
`discord_dir` Set the path to Discord if it's not the default one\
`ico_dir` Set another path for the .ico to be copied from\
`program_name` Dont change unless you know what you are doing\
`max_kill_tries` Maximum number of tries to close Discord before installation

# What do I need to have installed?
Only Discord\
You don't need to have python,
git or bun installed as the release contains everything in it, so nothing will be installed.
That's why it's relatively large for a script of this size.

# Platforms
As of now, I only designed it for **Windows**. I don't know if it works on linux or MaxOS.

# I'm not affiliated with Discord or BetterDiscord
Use this at your own risk!