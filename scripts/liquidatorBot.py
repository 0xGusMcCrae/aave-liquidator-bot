#delete the imports I don't need
import web3
import time 
import datetime
from brownie import *
import os
from dotenv import load_dotenv
import requests
import json
import pandas

load_dotenv()


#log into account beforehand, deploy liquidator contract, 
#and feed  both into constructor 
class liquidator:
    def __init__(self, account, liquidatorContractAddress):
        self.liquidatorContract = Contract.from_abi() #have abi ready to go in file
        self.aavePool = Contract.from_explorer(os.getenv('AAVE_ARB_MAIN_POOL')) 
        self.l2encoder = Contract.from_explorer(os.getenv('AAVE_L2_ENCODER'))
    
    def checkHealthFactors(self):
        df = pandas.read_csv('../data/users.csv')
        #then df.users can be iterated through - it's a list of address strings
        #load csv, loop through accounts, return accounts with 
        #HF < 1

