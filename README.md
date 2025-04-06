# CapitalismBot - Minecraft x Discord bot
A Discord bot that relays messages to/from a Minecraft server.

## Major features
- No minecraft account required
- Send feed of in-game messages to any associated Discord channels
- Gives Discord users ability to send messages in-server
- Enables Discord mods to act as server mods
- Allows players and discord users to ping each other from their respective platforms

## Requirements
- **A Discord bot API key**
https://discordpy.readthedocs.io/en/stable/discord.html
- **Admin access to your minecraft server**
This means either having access to the local folder running the server, 
or the RCON port + server logs as a file.
- **Ability to host the bot**
If you aren't familiar with hosting a Discord bot, it will need to run continuously on your own computer or a host server. Either your computer or the host server is what will need access to the minecraft server.

## Setup
1. Run **init_config.py** (first time only)
This will generate the config .json files you will need to configure.
2. Setup the config files with your basics
See **Configuration** section for details
3. Run **start_bot.py** (this will start the bot)

## Configuration
The following config files are found in the new config folder created by the **init_config.py** script - by default found in the top of the bot directory and called 'configs'.
- **discord_config.json**
  - API_TOKEN *(required)* - the string of your discord bot API
  - PERMISSIONS_INT - the permissions value for the bot

- **admin_roles.json**
Here is a breakdown of the admin_roles dictionary:

```
  {
    "[serverID]": {
      "[serverRoleID]": {
        "admin_level": 1
  }}}
```

| Item | Description | Example |
| ------: | ----------- | ----------- |
| serverID *(required)* | the ID for a server you added the bot to | "1000000000000000100"|
| serverRoleID *(required)*| the existing server role authorized to control this bot | "1011111111111111111"|
| admin_level | currently only '1' is supported | 1 |

- **discord_channels.json**
This will self-populate as needed. After assigning a role ID as admin, type '*#addbot*' as a user with the admin role to allow the bot into the channel.  
By default, the command will enable bot commands to be triggered from that channel.  
To enable all in-game log prints on that channel or change other settings, you'll also need to run #rule command

```
{
  "[channelID]": {
    "allow_commands": true,
    "printRCON": true,
    "print_log": false
}}
```
| Rule | Description | type |
| ------: | :----------- | ----------- |
| allow_commands | allow bot commands in channel |bool|
| print_log | print ALL server messages to channel |bool|
| printRCON | print #say commands back to the channel |bool|


- **mc_config.json**
For minecraft server related settings
```
{
  "SERVER_DIR": "S:\\Minecraft Server\\Your Server",
  "SERVER_IP_ADDR": "N/A",
  "UPDATE_FREQS": [
    600,
    15,
    5
  ],
  "USRNAME_DICT": {
    "MinecraftPlayer1": [
      "@DiscordUser1",
      123456789012345678
    ],
    ...
  }
  "RCON_DICT": {
    "RCON_IP": "127.0.0.1"
    "RCON_PWD": "mypassword"
    "RCON_PORT": 25575
  }
}
```
| Item | Description | Example |
| ------: | :----------- | ----------- |
| SERVER_DIR *(required)*| path for minecraft server |"C:\\Minecraft Server\\Your Server"|
| SERVER_IP_ADDR | IP for user minecraft connection |"123.234.12.56:25565"|
| UPDATE_FREQS | polling frequency to check for new minecraft messages. This example will check every 600s, but change to 5s once it sees any new message. Then 30s, 60s, etc. |[600,60,30,5]|
| USRNAME_DICT | Minecraft<->Discord name mapping |MinecraftName-> DiscordPreferredName-> DiscordUserID|
| RCON_DICT | dictionary with the following: ||
| RCON_IP | IP address for rcon connection |"127.0.0.1"|
| RCON_PWD | password for rcon connection |"mypassword"|
| RCON_PORT | port for rcon connection |"127.0.0.1"|

USRNAME_DICT will be auto-populated by the #addusername command.  
RCON_DICT will be auto-populated from the server.properties if you supply it.  
SERVER_IP_ADDR is just for bot print, the bot will not connect this way.  

## FAQ
- **Can I use my existing Discord bot?**
You should be able to open this bot as a new session using the same API key. This is untested.