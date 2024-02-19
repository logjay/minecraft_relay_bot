import os, sys, getopt

import relaybot
import init_config


def parse_args(argv) -> dict:
    arg_dict = {
        "config_folder" : None,
        "minecraft_folder": None
    }

    try:
      opts, args = getopt.getopt(argv,"hc:m:",["config-file=","mc-dir="])
    except getopt.GetoptError:
      print(f'Argument not recognized.\n\t start_bot.py -c <config_folder> -m <minecraft_folder>')
      print(f"Args: \n{argv}")
      sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('start_bot.py -c <config_folder>')
            sys.exit()
        elif opt in ("-c", "--config-file"):
            arg_dict["config_folder"] = arg
        elif opt in ("-m", "--mc-dir"):
            arg_dict["minecraft_folder"] = arg   

    print (f'Input args are: {arg_dict}', flush=True)

    return arg_dict

# load dictionaries and values from config files
CONFIG_FOLDER = os.path.join(os.path.dirname(__file__), 'configs')
MINECRAFT_FOLDER = None
UPDATE_FREQS = [60,30,30,30,15,10,5]

args_dict = parse_args(sys.argv[1:])

if args_dict["config_folder"] is not None:
    CONFIG_FOLDER = args_dict["config_folder"]

if args_dict["minecraft_folder"] is not None:
    MINECRAFT_FOLDER = args_dict["minecraft_folder"]

config_info = init_config.ConfigInfo(CONFIG_FOLDER)

# initialize relaybot
bot = relaybot.RelayBot(discord_config_dict = None, 
                        minecraft_config_dict = None, 
                        config_info = config_info,
                        minecraft_server_dir=MINECRAFT_FOLDER,
                        poll_frequencies = UPDATE_FREQS)

bot.run()