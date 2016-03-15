import json
import re

def extract_cards(filename):
    cards = {}
    with open(filename, encoding="utf8") as data_file:
        data = json.load(data_file)
    for card in data:
        name = card['name'].lower()
        if 'text' in card:
            card['text'] = re.sub('<.*?>','',card['text'])
        cards[name] = card
    return cards
    
