import users
import threading
from time import sleep
import urllib.request
import cfg
import json

def add_points():
    while True:
        try:
            r = urllib.request.urlopen("http://tmi.twitch.tv/group/user/"+cfg.CHANNEL_NAME+"/chatters")
        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
            continue
        chattersJson = json.loads(r.read().decode("utf-8"))
        for key in chattersJson['chatters']:
            for name in chattersJson['chatters'][key]:
                user = users.get_user(name)
                user['points']+=cfg.PPM
                if key!='viewers':
                    user['mod'] = True
                else:
                    user['mod'] = False
                users.update_user(user)
        sleep(60)

def monitor_chat():
    threading.Thread(target=add_points).start()

