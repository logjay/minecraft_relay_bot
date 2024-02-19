import os
import inspect
import discord

from load_config import *
from init_config import *

class BotCommand():

    def __init__(self,
                 cmd_name:str,
                 funct,
                 admin_level:int = 0,
                 description = ''
                 ):
        
        self.cmd_name = cmd_name
        self.admin_level = admin_level
        self.funct = funct
        self.description = description

class DiscordBotMgr():

    channels_dict = {}

    admin_role_dict = {}
    
    default_ch_params = {
        "allow_commands": True
    }


    def __init__(self, config_dict, config_info:ConfigInfo):

        self.config_dict = config_dict
        self.config_dict_file = config_info.DISCORD_CONFIG_PATH()
        self.channel_config_file = config_info.DISCORD_CHANNELS_PATH()
        self.admins_json = config_info.ADMIN_ROLES_PATH()

        if self.config_dict is None:
            self.config_dict = get_dict(self.config_dict_file)

        self.API_TOKEN = self.config_dict['API_TOKEN']

        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.client:discord.Client = discord.Client(intents=self.intents)

        self.cmd_trigger = '!'
        self.commands_list = [BotCommand('null', None)]

        self._get_admin_dict()
        self._get_supported_channels()

    def set_dict(self, key, param):
        try:
            self.config_dict[str(key)] = param
        except: 
            print(f"No parameter {str(key)} found.")
            return
        self.save_config_dict()

    def save_config_dict(self):
        write_dict(self.config_dict,self.config_dict_file)

    def all_chs(self):
        return [int(ch) for ch in self.channels_dict.keys()]

    def log_chs(self):
        return [ch for ch in self.all_chs() if self.channels_dict[str(ch)]['print_log']]
    
    def cmd_chs(self):
        return [ch for ch in self.all_chs() if self.channels_dict[str(ch)]['allow_commands']]

    def add_supported_channel(self, channel_id, ch_params=None):
        if str(channel_id) in self.channels_dict.keys():
            return
        
        if ch_params is None:
            ch_params = self.default_ch_params
        else: 
            for dfl_parameter in self.default_ch_params:
                if dfl_parameter not in ch_params:
                    ch_params[dfl_parameter] = self.default_ch_params[dfl_parameter]

        self.channels_dict[str(channel_id)] = ch_params

        self._write_supported_channels()
        self._get_supported_channels()


    def is_admin(self, user:discord.User, req_level = 1):        
        if req_level <= 0:
            return True # skip some looping
        
        server = user.guild.id
        user_level = 0
        for role in user.roles:
            if str(role.id) in self.admin_role_dict[str(server)].keys():
                role_lvl = self.admin_role_dict[str(server)][str(role.id)]['admin_level']
                if role_lvl > user_level:
                    user_level = role_lvl

                if req_level <= user_level:
                    return True
        if req_level <= user_level:
            return True
        return False
    
    def _write_new_admin_dict(self, new_dict):
        write_dict(new_dict, self.admins_json)

    def _get_admin_dict(self):
        self.admin_role_dict = get_dict(self.admins_json)

    def _write_supported_channels(self):
        write_dict(self.channels_dict, self.channel_config_file)
        
    def _get_supported_channels(self):
        self.channels_dict = get_dict(self.channel_config_file)
        updated = False
        for ch in self.channels_dict:
            for dflt_rule in self.default_ch_params:
                if dflt_rule not in self.channels_dict[ch]:
                    updated = True
                    self.channels_dict[ch][dflt_rule] = self.default_ch_params[dflt_rule]

        if updated:
            self._write_supported_channels()

    async def command_handler(self, message:discord.Message):
        """uses command_dict of parent functions to react to messages"""
        if message.clean_content.lower().startswith(self.cmd_trigger):
            for i, cmd_name in enumerate([cmd.cmd_name for cmd in self.commands_list]):
                if message.clean_content.lower().startswith(self.cmd_trigger + cmd_name):
                    if self.is_admin(message.author, self.commands_list[i].admin_level): # checks permission level
                        if self.commands_list[i].funct is None:
                            print(f"No command function specified for {cmd_name}")
                            return False
                        elif not inspect.iscoroutinefunction(self.commands_list[i].funct):
                            self.commands_list[i].funct(message)
                            return True

                        await self.commands_list[i].funct(message) #executes cmd function
                        return True
                    break # leave after first match
        
        return False

    def run(self):
        return self.client.run(self.API_TOKEN)
    