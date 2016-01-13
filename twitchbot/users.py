from pymongo import MongoClient
import cfg

client = MongoClient()
db = client[cfg.CHANNEL_NAME]
users = db.users

_attributes = ['name','count','points', 'mod']

def create_user(name, points=0, count=0, mod=False):
   return {
            'name': name.lower(),
            'points': points,
            'count': count,
            'mod': mod
          }

def get_user(name):
    if not user_exists(name):
        add_user(name)
    return users.find_one({'name': name.lower()})

def add_user(name):
    return users.insert_one(create_user(name))

def remove_user(name):
    return users.delete_many({'name': name.lower()})

def user_exists(name):
    return list(db.users.find({'name': name.lower()}).limit(1))!=[]

def update_user(user):
    users.update_one(
        {'name': user['name'].lower()}, {'$set': user}, upsert=True 
    )

def set_attribute(name, key, value):
    users.update_one(
        {'name': name.lower()}, 
        {'$set': { key: value} }
    )
    
