import json
import re

def extract_cards(filename):
    cards = {}
    json_data = open(filename).read()
    data = json.loads(json_data)
    for card in data:
        name = card['name'].lower()
        if 'text' in card:
            card['text'] = re.sub('<.*?>','',card['text'])
        cards[name] = card
    return cards
    
