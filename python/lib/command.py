import client_helpers as CLIENT
import discord
import random

class CommandManager:
    def __init__(
            self, 
            client, 
            dict_com, 
            config):
        
        self.client = client
        self._dict_com = {x: dict_com[x]['func'] for x in dict_com}
        self.com = list(self._dict_com.keys())
        self.config = config
        self.last_msg = dict()
        
    async def run(self, message, command, args):
        try:
            f_name = self._dict_com[command]
            f = CommandManager.__getattribute__(self, f_name)
            return await f(self, message, command, args)
        except AttributeError as ne:
            raise NameError(f"Attribute {f_name} not found.") from ne
        except KeyError as ke:
            raise KeyError(f"No match found for {command}.") from ke
    
    @staticmethod
    async def sed(coma, msg, command, args):
        if msg.channel.id in coma.last_msg and \
                not coma.last_msg[msg.channel.id].empty():
                    prev_msg = coma.last_msg[msg.channel.id].get()
                    s = [{'s': i.split('/')[0], 
                        'r': i.split('/')[1], 
                        'f': None if len(i.split('/')) < 3 else i.split('/')[2]}
                        for i in args]
                    m = prev_msg.content
                    for i in s:
                        if i['f'] and i['f'].isdigit():
                            m = m.replace(i['s'], i['r'], int(i['f']))
                        else:
                            m = m.replace(i['s'], i['r'])
                    await coma.client.edit_message(prev_msg, m)    
                    #coma.last_msg[msg.channel.id].put(prev_msg)
                    await coma.client.delete_message(msg)
                    return prev_msg
        return msg

    @staticmethod
    async def spongemock(coma, msg, command, args):
        m = ' '.join(args).lower()
        r = [ bool(random.getrandbits(1)) for i in range(len(m)) ]
        s = [ j.upper() if r[i] else j for i, j in enumerate(m) ]
        e = await coma.client.edit_message(msg, ''.join(s))
        return e
