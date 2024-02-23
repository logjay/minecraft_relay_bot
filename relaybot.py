"""
Written by Logan Williams January 2024
"""
import os
import random
from typing import List

import discord
from discord.ext import tasks

import mc_server_manager
import discord_util
import init_config


class RelayBot():
    """
    Managing class for RelayBot, bridging DiscordBotMgr and MCServerManager and managing all bot-specifics
    """
    def __init__(self,
                 discord_config_dict:dict,
                 minecraft_config_dict:dict,
                #  config_folder:str,
                 config_info:init_config.ConfigInfo,
                 poll_frequencies:list = [1000],
                 minecraft_server_dir = None):

        self.disc_bot = discord_util.DiscordBotMgr(
            config_dict = discord_config_dict,
            config_info = config_info
        )

        addtl_bot_default_rules = {"printRCON": True,
                                   "print_log": False}
        
        self.editable_server_props = {"motd":str, 
                                 "pvp":bool, 
                                 "difficulty":str}

        for rule in addtl_bot_default_rules: # add more non-generic rules to the discord class
            self.disc_bot.default_ch_params[rule] = addtl_bot_default_rules[rule]
        self.disc_bot._get_supported_channels()

        self.disc_bot.cmd_trigger = "#"
        self.disc_bot.commands_list = [
            discord_util.BotCommand("help", self.print_help,                    description = 'for this message'),
            discord_util.BotCommand("log", self.log_cmd,                        description = 'for recent messages not seen yet by server'),
            discord_util.BotCommand("list", self.list_cmd,                      description = 'for current player list'),
            discord_util.BotCommand("ip", self.ip_cmd,                          description = 'show IP address for server'),
            discord_util.BotCommand("say", self.say_cmd,                        description = 'to send message to the server. (or reply to one of the game messages)'),
            discord_util.BotCommand("admin", self.print_help_admin_cmd,         description = 'for admin cmd list'),
            discord_util.BotCommand("op", self.op_cmd,                          description = 'make user an admin', admin_level=1),
            discord_util.BotCommand("rule", self.rule_cmd,                      description = '[rulename] to change bot rule, or print all rules', admin_level=1),
            discord_util.BotCommand("addbot", self.add_channel,                 description = 'adds bot to the relevant channel', admin_level=1),
            discord_util.BotCommand("addusername", self.add_username_to_dict,   description = '[MCUsername] [@DiscordName] associates MC name with Discord name', admin_level=1),
            discord_util.BotCommand("server_prop", self.server_prop_cmd,        description = 'changes server settings', admin_level=1),
            discord_util.BotCommand("makeadmin", self.make_admin_cmd,          description = '[roleID][admin_level] makes a role into bot admin', admin_level=1),    
        ]

        self.mc_bot = mc_server_manager.MCServerManager(
            config_dict = minecraft_config_dict,
            config_info = config_info,
            server_dir = minecraft_server_dir
        )

        self.poll_frequencies = poll_frequencies
        self.curr_freq_idx = 0

        self.on_ready = self.disc_bot.client.event(self.on_ready) # equal to @disc_bot.client.event before def on_ready
        self.on_message = self.disc_bot.client.event(self.on_message)

    def run(self):
        self.disc_bot.run()

    @tasks.loop(seconds=1000)
    async def pollforupdates(self):
        update_lines = self.check_server_updates()
        self.pollforupdates.change_interval(seconds=self.shift_interval())
        for channelID in self.disc_bot.log_chs():
            channel = self.disc_bot.client.get_channel(channelID)
            for line in update_lines:
                if '[Relay]' in line and not self.disc_bot.channels_dict[str(channel.id)]['printRCON']:
                    continue # don't print
                await channel.send(line)
        if len(update_lines) > 0:
            self.pollforupdates.change_interval(seconds=self.reset_interval())

        a = self.mc_bot.get_player_list()
        if a is None:
            message=f"Server is offline"
        else: 
            message=f"Minecraft w/ {len(a)} online"
        await self.disc_bot.client.change_presence(activity=discord.Activity(name=message, type = discord.ActivityType.playing))

    @pollforupdates.before_loop
    async def before(self):
        await self.disc_bot.client.wait_until_ready()

    async def broadcast_to_game(self, broadcast, channel):
        if not self.mc_bot.server_rcon.sendServerMessage(broadcast):
            await channel.send("Message couldn't send. Server may be offline.")
            return 
        self.pollforupdates.change_interval(seconds=5)
    
    def check_server_updates(self, requested = False) -> List[str]:
        new_lines = self.mc_bot.check_log_updates()
        return_strings = []
        if new_lines == []:
            if requested:
                return ["No new updates"]
            else:
                return []
        else:
            for line in new_lines:
                parsed_line = self.mc_bot.parse_server_message(line)
                if parsed_line is not None:
                    return_strings.append(parsed_line)

        return return_strings
    
    # @disc_bot.client.event
    async def on_ready(self):
        print(f'We have logged in as {self.disc_bot.client.user}', flush=True)
        self.pollforupdates.start()    

    async def add_username_to_dict(self, message:discord.Message):
        split_msg = message.content.split()
        if len(split_msg) != 3 or split_msg[0] != '#addusername':
            await message.channel.send(f"Syntax is #addusername [MCUsername] [@DiscordName]")
            return 
        for member in self.disc_bot.client.get_all_members():
            if member.mention == split_msg[2] and message.guild == member.guild:
                self.mc_bot.username_dict[split_msg[1]] = ['@'+ member.name, member.id]
                self.mc_bot.set_dict(self.mc_bot.username_dict_key, self.mc_bot.username_dict)
                return 

    async def add_channel(self, message:discord.Message):
        if message.channel.id not in self.disc_bot.cmd_chs():
            if self.disc_bot.is_admin(message.author):
                self.disc_bot.add_supported_channel(message.channel.id)
            else: 
                return
        else: 
            await message.channel.send(f"This channel is already on list")
            
    async def print_help(self, message:discord.Message):
        help_message = "RelayBot supports:"
        for i, cmd in enumerate(self.disc_bot.commands_list):
            if cmd.admin_level <= 0:
                help_message += '\n\t'
                help_message += self.disc_bot.cmd_trigger + cmd.cmd_name + ' - ' + cmd.description
        await message.channel.send(help_message)

    async def print_help_admin_cmd(self, message:discord.Message):
        help_message = "RelayBot admins can perform:"
        for i, cmd in enumerate(self.disc_bot.commands_list):
            if cmd.admin_level >=1:
                help_message += '\n\t'
                help_message += self.disc_bot.cmd_trigger + cmd.cmd_name + ' - ' + cmd.description
        await message.channel.send(help_message)

    async def say_cmd(self, message:discord.Message):
        broadcast = message.clean_content.split(self.disc_bot.cmd_trigger + "say")[1]
        broadcast = "@" + message.author.display_name + ": " + broadcast
        await self.broadcast_to_game(broadcast, message.channel)

    async def ip_cmd(self, message:discord.Message):
        await message.channel.send(f"Minecraft Server IP Address is: {self.mc_bot.server_ip}")

    async def log_cmd(self, message:discord.Message):
        update_lines = self.check_server_updates(requested = True)
        for line in update_lines:
            await message.channel.send(line)

    async def op_cmd(self, message:discord.Message):
        pass

    async def rule_cmd(self, message:discord.Message):
        split_msg = message.content.split()
        ch_rules = self.disc_bot.channels_dict[str(message.channel.id)]

        if len(split_msg) == 1:
            await message.channel.send(ch_rules)
            return 
        elif len(split_msg) == 3 and split_msg[1] in self.disc_bot.default_ch_params.keys():
            # ch_rules[split_msg[1]] = (split_msg[2].lower() in ["1", "true", "yes"])
            self.disc_bot.channels_dict[str(message.channel.id)][split_msg[1]] = (split_msg[2].lower() in ["1", "true", "yes"])
            self.disc_bot._write_supported_channels()
            await message.channel.send(f"Channel rule {split_msg[1]} set to {self.disc_bot.channels_dict[str(message.channel.id)][split_msg[1]]}")

    async def server_prop_cmd(self, message:discord.Message): 
        split_msg = message.content.split()
        if len(split_msg) == 1:
            prop_message = f"These are the available properties to change: \n"
            for prop in self.editable_server_props:
                prop_message += f"\t{prop} : {self.editable_server_props[prop].__name__}\n"
            await message.channel.send(prop_message)
            return 
        elif len(split_msg) >= 3 and split_msg[1] in self.editable_server_props.keys():
            try:
                if self.editable_server_props[split_msg[1]] == str:
                    new_param = message.content.removeprefix(f"{split_msg[0]} {split_msg[1]} ")
                else: 
                    new_param = self.editable_server_props[split_msg[1]](split_msg[2])
            except:
                await message.channel.send(f"Setting {split_msg[1]} must be of type {self.editable_server_props[split_msg[1]]}")

            self.mc_bot.server_props[split_msg[1]] = str(new_param)
            self.mc_bot.set_server_properties()

            await message.channel.send(f"Setting {split_msg[1]} to {split_msg[2]}")

    async def make_admin_cmd(self, message:discord.Message):
        split_msg = message.content.split()
        if len(split_msg) == 1:
            await message.channel.send(f"Syntax is #makeadmin [role ID #] [admin level]")
            return 
        elif len(split_msg) == 3:
            roleID = str(split_msg[1])
            admin_level = split_msg[2]
            server = str(message.guild.id)

            # if server in self.disc_bot.admin_role_dict:
                # if str(roleID) in self.disc_bot.admin_role_dict[server]:
            
                # sender must be a level ABOVE to change level of role
            if not self.disc_bot.is_admin(message.author, int(admin_level) + 1): 
                # await message.channel.send(f"Must be higher level than {self.disc_bot.client.get_guild(int(roleID)).id} to change")
                await message.channel.send(f"Must be higher level than {admin_level} to change")
                return 
                    
            
            self.disc_bot.add_admin_role(server, roleID, admin_level)
            await message.channel.send(f"Made {roleID} admin level {admin_level}")

    async def list_cmd(self, message:discord.Message):
        self.mc_bot.get_player_list()
        playerList = self.mc_bot.CurrentPlayersList
        if playerList == []:
            playerList = "None"
            if random.random() < 0.035:
                playerList = "None...\nbut you could be ;)"
        await message.channel.send(f"Current online players: {playerList}")

    # @disc_bot.client.event
    async def on_message(self, message:discord.Message):
        if message.author == self.disc_bot.client.user:
            return
        
        await self.disc_bot.command_handler(message)

        if message.reference is not None: 
            if message.reference.resolved.author.id == self.disc_bot.client.user.id and \
                message.reference.resolved.clean_content[0] == '@': # is a reply to this bot
                await self.broadcast_to_game("@" + message.author.display_name + ": " + message.clean_content, message.channel)

                # TODO - edit the replied-to message to @ the player's discord, so they get a reply notification

        if message.clean_content.lower().startswith('@'+self.disc_bot.client.user.display_name):
            await message.channel.send("Don't @ me please :'( it hurts my feelings.")


    def shift_interval(self) -> int:
        if self.curr_freq_idx > 0:
            self.curr_freq_idx -= 1
        return self.get_freq()

    def reset_interval(self) -> int:
        self.curr_freq_idx = len(self.poll_frequencies) - 1
        return self.get_freq()
    
    def get_freq(self) -> int:
        return self.poll_frequencies[self.curr_freq_idx]
