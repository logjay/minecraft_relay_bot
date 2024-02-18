import os

from rcon.source import Client

from init_config import *
from load_config import *

leave_join_msgs = ["lost connection",
                    "left the game",
                    "joined the game"]

ip_default = '127.0.0.1'
pwd_default = ''
port_default = 25575


class MinecraftRCON():
    def __init__(self, ip = None, pwd = None, port=None):
        self.ip = ip
        self.pwd = pwd
        self.port = port

        self.check_defaults()

    def __init__(self, config_dict):
        self.ip = config_dict['RCON_IP']
        self.pwd = config_dict['RCON_PWD']
        self.port = config_dict['RCON_PORT']
            
        self.check_defaults()
            
    def check_defaults(self):
        if self.ip is None:
            self.ip = ip_default
        if self.pwd is None:
            self.pwd = pwd_default
        if self.port is None:
            self.port = port_default

    def sendServerCommand(self, cmd, args=None):
        try:
            with Client(self.ip, self.port, passwd=self.pwd) as client:
                if args == None:
                    response = client.run(cmd)
                else: 
                    response = client.run(cmd,args)
            return True, response
        except:
            return False, None
        
    def sendServerMessage(self, message):
        return self.sendServerCommand('/say', message)[0]

    def getActivePlayers(self):
        result, msg = self.sendServerCommand('/list')
        if msg == None:
            return None
        players = msg.split('players online: ')[1].split(',')
        for player in players:
            if player == '':
                players.remove(player)

        return players


class MCServerManager():
    """
    Server manager for connecting remotely to a minecraft server.
    """

    CurrentPlayersList = []

    update_freq_idx = 0

    server_rcon = MinecraftRCON

    def __init__(self, config_dict, server_dir, config_info:ConfigInfo):

        self.config_dict = config_dict
        # self.config_folder = config_folder

        # self.config_dict_file = os.path.join(self.config_folder,'mc_config.json')
        self.config_dict_file = config_info.MC_CONFIG_PATH()

        if self.config_dict is None:
            self.config_dict = get_dict(self.config_dict_file)

        if server_dir is None:
            self.server_dir = self.config_dict['SERVER_DIR']
        else: 
            self.server_dir = server_dir

        if self.config_dict['RCON_DICT'] is None:
            self.get_RCON_settings()
            
        self.server_rcon = MinecraftRCON(self.config_dict['RCON_DICT'])
        
        self.server_ip       = self.config_dict['SERVER_IP_ADDR']
        
        self.username_dict   = self.config_dict['USRNAME_DICT']

        self.latest_log = self.read_latest_log()


    def set_dict(self, key, param):
        try:
            self.config_dict[str(key)] = param
        except: 
            print(f"No parameter {str(key)} found.")
            return
        self.save_config_dict()

    def save_config_dict(self):
        write_dict(self.config_dict,self.config_dict_file)

    def read_latest_log(self):
        with open(os.path.join(self.server_dir, "logs/latest.log"), "r") as f:
            log = f.readlines()
        return log
    
    def get_RCON_settings(self):
        with open(os.path.join(self.server_dir, "server.properties"), "r") as f:
            settings_lines = f.readlines()

        properties_dict = {}
        for line in settings_lines:
            line = line.split('\n')[0]
            if '=' in line:
                prop = line.removeprefix(line.split('=')[0] + '=')
                if prop == '':
                    prop = None
                properties_dict[line.split('=')[0]] = prop
                
            pass

        self.server_props = properties_dict

        self.config_dict['RCON_DICT'] = {}

        self.config_dict['RCON_DICT']['RCON_IP'] = self.server_props['server-ip']
        self.config_dict['RCON_DICT']['RCON_PWD'] = self.server_props['rcon.password']
        self.config_dict['RCON_DICT']['RCON_PORT'] = int(self.server_props['rcon.port'])

    def check_log_updates(self):
        new_lines = []
        current = self.read_latest_log()
        if self.latest_log != current:
            for line in current:
                if line not in self.latest_log:
                    new_lines.append(line)
            self.latest_log = current

        return new_lines
    
    def get_player_list(self):
        activePlayers = self.server_rcon.getActivePlayers()
        # if activePlayers is None:
        #     return None
        # else:
        self.CurrentPlayersList = activePlayers
        # for player in self.CurrentPlayersList:
        #     if player == '':
        #         self.CurrentPlayersList.remove(player)
        return self.CurrentPlayersList
    
    def parse_server_message(self, line = ""):
        timesplit = '@'+line.split("[")[1].split("]")[0]
        if 'thread/INFO]' not in line:
            return None
        elif ' [Server thread/INFO]: [Not Secure] ' in line:
            msg = line.split(' [Server thread/INFO]: [Not Secure] ')[1]
            if '[Rcon]' in msg:
                msg = msg.replace('[Rcon] ', '[Relay] ')
                # return None # TEMP? do we want to print the message back to discord to show?
            return timesplit + " " + msg
        elif 'advancement' in line and '<' not in line:
            try:
                achievement = line.split("]")[2].split("[")[1]
                namesplit = line.split(" has")[0].split("]: ")[1]
                if namesplit in self.username_dict.keys():
                    namesplit += f"({self.username_dict[namesplit][0]})"
                    
                return timesplit + " " + namesplit + " got _[" + achievement+"]_"
            except:
                return None
        elif line.split("[Server thread/INFO]: ")[1].split(" ")[0] in self.username_dict.keys():
            name = line.split("[Server thread/INFO]: ")[1].split(" ")[0]
            # means death message or join/leave message
            message = line.split(name)[1]
            barred = False
            for barred_msg in leave_join_msgs:
                if barred_msg in message:
                    barred = True
                    break

            if not barred:
                return timesplit + " " + name + message
        elif '/INFO]: /' not in line: # ignores help menu printouts
            try:
                namesplit = line.split("<")[1].split(">")[0]
                msg = line.split("> ")[1]

                for key in self.username_dict.keys():
                    if '@' + key in msg:
                        msg = msg.replace('@' + key, f"<@{self.username_dict[key][1]}>")
                return timesplit + " " + namesplit + ": " + msg
            except:
                return None

