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

#could do this where it runs deploy and then instantiates a liquidator and
#runs liquidator.main()