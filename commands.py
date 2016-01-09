import os.path
import users
from utils import extract_cards
from pymongo import MongoClient

client = MongoClient()
db = client.test_database

class Command:
    def __init__(self, fn, name, mod=False):
        self.name = name
        self.fn = fn
        self.mod = mod
        self.enabled = True
    def __str__(self):
        return '[{}]'.format(name)

def init_custom_commands():
    cursor = db.custom_commands.find()
    result = {}
    for doc in cursor:
        name = doc['name']
        response = doc['response']
        fn = lambda username, message: response
        result[name] = Command(fn, name)
    return result

_CARDS_FILE = 'cards.json'
_custom_commands = init_custom_commands()
_commands = {} 
_cards = extract_cards(_CARDS_FILE)

def command(name, mod=False):
    def add(fn):
        cmd = Command(fn, name, mod)
        _commands[name] = cmd
        return fn
    return add


def add_custom_command(name, response):
    cmd = Command(lambda username, message: response, name)
    _custom_commands[name] = cmd
    db.custom_commands.insert_one(
        {
            'name': name,
            'response': response
        }
    )

def remove_custom_command(name):
    if name in _custom_commands:
        del _custom_commands[name]
        db.custom_commands.delete_many({'name': name})
        return True
    else:
        return False

def process_command(username, msg, command):
    if command in _commands:
        cmd = _commands[command]
        if cmd.mod and not users.get_user(username)['mod']:
            return 'You are not authorized to perform this command'
        elif cmd.enabled:
            return _commands[command].fn(username,msg)
        else:
            return 'This command has been disabled'
    elif command in _custom_commands:
        cmd = _custom_commands[command]
        if cmd.mod and not users.get_user(username)['mod']:
            return 'You are not authorized to perform this command'
        elif cmd.enabled:
            return _custom_commands[command].fn(username, msg)
        else:
            return 'This command has been disabled'
    else:
        return '!{} is not a valid command. Use !commands for available commands'.format(command)

@command('add', mod=True)
def add_command(username, msg):
    parsed = msg.partition(' ')
    name = parsed[0]
    response = parsed[2]
    if response=='':
        return 'Not a valid command, use !add {command name} {command response}'
    elif name in _commands:
        return 'The command is built-in, it cannot be modified'
    elif name in _custom_commands:
        return 'The command already exists, use !remove to remove it'
    else:
        add_custom_command(name, response)
        return 'Command !{} added'.format(name)

@command('remove', mod=True)
def remove_command(username, msg):
    name = msg
    if name in _commands:
        return 'This command is built-in, it cannot be removed'
    elif name in _custom_commands:
        remove_custom_command(name)
        return 'Command !{} removed'.format(name)
    else:
        return 'This command does not exist'

@command('enable', mod=True)
def enable(username, msg):
    name = msg
    if name in _commands:
        cmd = _commands[name]
    elif name in _custom_commands:
        cmd = _custom_commands[name]
    else:
        return 'The command !{} does not exist'.format(name)
    if cmd.enabled:
        return 'This command is already enabled'
    else:
        cmd.enabled = True
        return 'The command !{} has been enabled'.format(cmd.name)

@command('disable', mod=False)
def disable(username, msg):
    name = msg
    if name in _commands:
        cmd = _commands[name]
    elif name in _custom_commands:
        cmd = _custom_commands[name]
    else:
        return 'The command !{} does not exist'.format(name)
    if cmd.enabled:
        if cmd.name=='disable' or cmd.name=='enable':
            return 'Cannot disable this command'
        else:
            cmd.enabled = False
            return 'The command !{} has been disabled'.format(cmd.name)
    else:
        return 'This command is already disabled'

@command("echo")
def echo(username, msg):
    return '{} said {}'.format(username, msg)


@command("card")
def card_info(username, msg):
    index = msg.lower()
    if index in _cards:
        card = _cards[index]
        name = card['name']
        if card['type']=='MINION':
            health = card['health']
            attack = card['attack']
            cost = card['cost']
            if 'text' in card:
                text = card['text']
                return '{}: {} mana {}/{} minion: {}'.format(name, cost, attack, health, text)
            else:
                return '{}: {} mana {}/{} minion'.format(name, cost, attack, health)
        elif card['type']=='SPELL':
            text = card['text']
            cost = card['cost']
            return '{}: {} mana spell: {}'.format(name, cost, text)
        elif card['type']=='WEAPON':
            attack = card['attack']
            durability = card['durability']
            cost = card['cost']
            if 'text' in card:
                text = card['text']
                return '{}: {} mana {}/{} weapon: {}'.format(name, cost, attack, durability, text)
            else:
                return '{}: {} mana {}/{} weapon'.format(name, cost, attack, durability)
        elif card['type']=='HERO':
            player_class = card['playerClass'].lower()
            return '{}: {} class'.format(name, player_class)
        else:
            name = card['name']
            if 'text' in card:
                text = card['text']
                return '{}: {}'.format(name, text)
            else:
                return '{}: A card'.foramt(name)
    else:
        return 'Could not find {} in the card collection'.format(msg)

@command("count")
def count(username, msg):
    user = users.get_user(username)
    user['count']+=1
    users.update_user(user)
    return '{} typed !count {} times'.format(user['name'],user['count'])

@command("commands")
def commands(username, msg):
    s = 'These are the commands I respond to: '
    for name, command in _commands.items():
        if not command.mod and command.enabled:
            s+='!'+name+' '
    for name, command in _custom_commands.items():
        if not command.mod and command.enabled:
            s+='!'+name+' '
    return s[:-1]

@command("points")
def points(username, msg):
    user = users.get_user(username)
    return '{} has {} points'.format(user['name'],user['points'])

