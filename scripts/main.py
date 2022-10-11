#delete the imports I don't need
import time 
import datetime
from brownie import *
import os
from dotenv import load_dotenv
import requests
import json
from eventListener import EventListener
import sys
#import liquidator class

#basic idea is to have the  event listener get me accounts on aave,
#add them to a dictionary or something, and then keep track of their
#health factor, when one is low enough, I can use flash loans to liquidate
#them

#might need to put this above import eventListener
if "C:\Users\Trevo\Documents\Solidity Stuff\aave-liquidation-bot" not in sys.path:
    sys.path.append(r"C:\Users\Trevo\Documents\Solidity Stuff\aave-liquidation-bot\scripts")

#basic idea behind getting an address
myListener = EventListener('0x794a61358D6845594F94dc1DB02A252b5b4814aD')
while(True):
    user = False
    while not user:
        time.sleep(5)
        try: 
            result = myListener.supplyfilter.get_new_entries()
        except:
            myListener.handleBadConnection
            result = myListener.supplyfilter.get_new_entries()
        if result != []:
            user = myListener.parseUser(result)

#really all we want to do is get a database of addresses - they're not going
#to be liquidated immediately after they get detected