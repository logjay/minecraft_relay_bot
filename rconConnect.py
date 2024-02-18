from rcon.source import Client


class MinecraftRCON():
    def __init__(self, ip = '127.0.0.1', pwd = '', port=25565):
        self.ip = ip
        self.pwd = pwd
        self.port = port

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