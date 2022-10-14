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
        self.account = account
        self.liquidatorContract = Contract.from_abi() #have abi ready to go in file
        self.poolAddressProvider = Contract.from_explorer(os.getenv('AAVE_POOL_ADDRESSES_PROVIDER'))
        self.pool = Contract.from_explorer(self.poolAddressProvider.getPool()) #switch this to a dontenv load
        self.uiPoolDataProviderV3 = Contract.from_explorer(os.getenv('UI_POOL_DATA_PROVIDER_V3'))
        self.l2encoder = Contract.from_explorer(os.getenv('AAVE_L2_ENCODER'))#probably don't need this - it will only be used in the liquidator contract
        #but might need if I'm deploying liquidator from this file

    def main():
        print()

    def checkHealthFactors(self):
        df = pandas.read_csv('../data/users.csv')
        #then df.users can be iterated through - it's a list of address strings
        #load csv, loop through accounts, return accounts with 
        #HF < 1
        liquidatableAccounts = []
        for user in df.users:
            HF = self.aavePool.getUserAccountData(user)[-1]/(10**18)
            if HF < 1:
                liquidatableAccounts.append(user)
        return liquidatableAccounts



    #probably will split into more than 1 function - maybe handleGetReserves()?
    # and tbh probably will put most of this in main() with the only thing remaining
    #in the liquidationCall function is the single line call to the liquidator contract
    def liquidationCall(self, user):
        
        debtToken, collateralToken = self.getDebtAndCollateralTokens(user)
        
        expectedProfit = self.calculateProfitability() #probably will be passing in collateral and debt tokens here
        if expectedProfit > 0: #probably will be setting this higher than zero
            self.liquidatorContract.liquidate(collateralToken[0],debtToken[0],user,-1,False, {'from': self.account.address}) 
        
        #probably return a bool for success/failure and realised profit if possible

    def calculateProfitability(self):
        #going to need to calculate profitability
        #see aave docs for details
        expectedProfit = ''

        return expectedProfit
    

    #aave allows you to flashloan more than 1 asset at a time
    #but liquidation call only allows 1 at a time
    #either keep how it is now or just add a loop to go through liquidations for
    #more than 1 asset - but probably not viable gas-wise
    #probably better to just keep it as-is and do single-asset liquidations
    def getDebtAndCollateralTokens(self, user):
        #first we want to get reserves data for the user
        userReserves = self.uiPoolDataProviderV3.getUserReservesData(self.poolAddressProvider.address,user)[0]
        #drop items that aren't debt or collateral
        debtTokens = []
        collateralTokens = []
        for item in userReserves:
            if item[1] != 0:
                collateralTokens.append(item)
            if item[4] != 0 or item[5] != 0:
                debtTokens.append(item)
        #will need to account if there is more than 1 debt token or more than 1 collateral token
        #but also need to figure out how aave handles that - which should i be liquidating?
        #probably the larger collateral token and larger debt token are a good place to start
        debtToken = None
        collateralToken = None
        #honestly might want to turn the below into pickDebtAndCollatTokens()
        #starting to look like spaghetti!
        #find debt token with largest balance
        for item in debtTokens:
            if debtToken is None:
                debtToken = item
                #variable/stable debt doesnt matter, just figure out which has a balance
                if debtToken[4] != 0:
                    debtTokenAmount  = debtToken[4]
                elif debtToken[5] != 0:
                    debtTokenAmount = debtToken[5]
            else:
                #variable/stable debt doesnt matter, just figure out which has a balance
                if item[4] != 0:
                    itemAmount  = item[4]
                elif item[5] != 0:
                    itemAmount = item[5]
                #check if current item has larger balance than debt token
                #if so, current item is debt token
                if itemAmount > debtTokenAmount:
                    debtToken = item
                    debtTokenAmount = itemAmount
        #repeat for collateral tokens
        for item in collateralTokens:
            if collateralToken is None:
                collateralToken = item
                collateralTokenAmount = collateralToken[2] 
            else:
                itemAmount = item[2]
                #check if current item has larger balance than collateral token
                #if so, current item is collateral token
                if itemAmount > collateralTokenAmount:
                    collateralToken = item
                    collateralTokenAmount = itemAmount
        return debtToken, collateralToken
            
                
                    
                