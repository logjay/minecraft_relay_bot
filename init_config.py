import os, sys, getopt

import load_config


class ConfigInfo():

    def __init__(self, config_directory):

        self.config_directory = config_directory

    def CONFIG_FOLDER_PATH(self):
        return self.config_directory

    def DISC_FOLDER_PATH(self):
        return os.path.join(self.CONFIG_FOLDER_PATH(),'discord')
    
    def DISCORD_CONFIG_PATH(self):
        return os.path.join(self.DISC_FOLDER_PATH(),'discord_config.json')
    
    def DISCORD_CHANNELS_PATH(self):
        return os.path.join(self.DISC_FOLDER_PATH(),'discord_channels.json')
    
    def ADMIN_ROLES_PATH(self):
        return os.path.join(self.DISC_FOLDER_PATH(),'admin_roles.json')
    
    def MC_FOLDER_PATH(self):
        return os.path.join(self.CONFIG_FOLDER_PATH(),'mc_server')
    
    def MC_CONFIG_PATH(self):
        return os.path.join(self.MC_FOLDER_PATH(),'mc_config.json')
    
    def gen_template_config(self):
        admin_roles_dict = \
            {
            "1000000000000000100":{
                "1011111111111111111": {
                    "admin_level": 1
                }
            },
            "1000000000000000200": {
                "1022222222222222222": {
                    "admin_level": 1
                }
                }
            }
        
        discord_channels_dict = \
            {
            "1000000000000000101": {
                "allow_commands": True,
                "printRCON": True,
                "print_log": False
            },
            "1000000000000000102": {
                "allow_commands": True,
                "printRCON": True,
                "print_log": True
            },
            "1000000000000000201": {
                "allow_commands": True,
                "printRCON": False,
                "print_log": True
            },
            }

        discord_config_dict = \
            {
            "API_TOKEN": "You must create your own discord bot and get its API key",
            "PERMISSIONS_INT": 377957256256
            }
                    
        minecraft_config_dict = \
            {
            "SERVER_DIR": "S:\\Minecraft Server\\Your Server",
            "RCON_DICT": None,
            "SERVER_IP_ADDR": "N/A",
            "UPDATE_FREQS": [
                60,
                30,
                30,
                30,
                15,
                10,
                5
            ],
            "USRNAME_DICT": {
                "MinecraftPlayer1": [
                "@DiscordUser1",
                123456789012345678
                ],
                "MinecraftPlayer2": [
                "@DiscordUser2",
                234567890123456789
                ],
                "MinecraftPlayer3": [
                "@DiscordUser3",
                345678901234567890
                ],
            }
            }

        os.makedirs(self.DISC_FOLDER_PATH())
        os.makedirs(self.MC_FOLDER_PATH())
        
        load_config.write_dict(admin_roles_dict, self.ADMIN_ROLES_PATH())
        load_config.write_dict(discord_channels_dict, self.DISCORD_CHANNELS_PATH())
        load_config.write_dict(discord_config_dict, self.DISCORD_CONFIG_PATH())
        load_config.write_dict(minecraft_config_dict, self.MC_CONFIG_PATH())



if __name__ == '__main__':
    config_directory = None
    gen_dir = True
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv,"hd:",["config-directory="])
    except getopt.GetoptError:
      print(f'Argument not recognized.\n\t init_config.py -d <config_directory>')
      print(f"Args: \n{argv}")
      sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('init_config.py -d <config_directory>')
            sys.exit()
        elif opt in ("-d", "--config-directory"):
            config_directory = arg  
            if os.path.exists(config_directory):
                confirm = input(f"The directory {config_directory} already exists. \
                    This script will overwrite your saved config files. \
                    To confirm, type 'yes'.")
                if confirm.lower() != 'yes':
                    gen_dir = False


    if config_directory is None:
        config_directory = os.path.join(os.path.dirname(__file__), 'configs')

    print (f'Config directory to be created @ {config_directory}', flush=True)

    config_inst = ConfigInfo(config_directory)

    if gen_dir:
        config_inst.gen_template_config()