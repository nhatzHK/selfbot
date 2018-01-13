import sys
import discord
import logging
import asyncio
import json
import queue

PATH = dict ()
try:
    with open (sys.argv [1]) as path_file:
        PATH = json.load (path_file)
except IndexError: #FileNotFoundError
    print ('Usage: python {} path/to/priv.bot.path.json'.format (sys.argv [0]))
    exit (1)
except FileNotFoundError:
    print ('Unable to open file: {}'.format (sys.argv[1]))
    exit (2)

sys.path.insert (0, PATH['lib'])
print(sys.path[0])
try:
    import client_helpers as CLIENT
    from command import CommandManager
except ImportError:
    print ('Error: One or more modules were not found in path.')
    exit (2)

JSON = PATH['json']
# Yep you should rename your config.json and append priv to it
# This way you won't add even more private stuff on github
CONFIG = JSON + "priv.nhk.config.json"
COMMANDS = JSON + "nhk.command.json"

logging.basicConfig (level = logging.INFO)

nhatz_config = CLIENT.loadJson (CONFIG)
commands = CLIENT.loadJson (COMMANDS)
censored = nhatz_config['censored']

Nhatz = discord.Client ()
last_msg = dict()

comanager = CommandManager(
        Nhatz,
        commands,
        nhatz_config)

def record_message(msg): 
    if msg.channel.id in comanager.last_msg:
        comanager.last_msg[msg.channel.id].put (msg)
    else:
        comanager.last_msg[msg.channel.id] = queue.LifoQueue()
        comanager.last_msg[msg.channel.id].put (msg)


@Nhatz.event
async def on_ready ():
    CLIENT.greet (Nhatz)

@Nhatz.event
async def on_message (msg):
    val = None
    if msg.author.id != Nhatz.user.id:
        return

    if any(word in msg.content for word in censored):
        await Nhatz.delete_message(msg)
        return

    if msg.content.startswith (nhatz_config['prefix']):
        args = msg.content.split (' ')
        if len(args) > 0:
            com = args[0].replace (nhatz_config['prefix'], '')
            args = args[1:]
            if com in comanager.com:
                val = await comanager.run (msg, com, args)
    
    if val:
        record_message(val)
    else:
        record_message(msg)

Nhatz.run (nhatz_config['token'], bot=False)
