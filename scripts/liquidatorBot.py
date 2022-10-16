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

#do a check so that if it's EURS token i just ignore it - dont want to deal with
#potentially low liquidity/high slippage

#log into account beforehand, deploy liquidator contract, 
#and feed  both into constructor 
class liquidator:
    def __init__(self, account, liquidatorContractAddress):
        self.account = account
        self.liquidatorContract = Contract.from_abi() 
        self.flashLoanHelperContract = Contract.from_abi()
        self.poolAddressProvider = Contract.from_explorer(os.getenv('AAVE_POOL_ADDRESSES_PROVIDER'))
        self.pool = Contract.from_explorer(self.poolAddressProvider.getPool()) #switch this to a dontenv load
        self.uiPoolDataProviderV3 = Contract.from_explorer(os.getenv('UI_POOL_DATA_PROVIDER_V3'))
        self.aaveOracle = Contract.from_explorer(os.getenv('AAVE_ORACLE_ADDRESS'))

    def main(self):
        pass
        
        
        # #debtToken, collateralToken = self.getDebtAndCollateralTokens(user)
        
        # expectedProfit = self.calculateProfitability(debtToken, collateralToken)
        # if expectedProfit > 0: #probably will be setting this higher than zero
        #     self.liquidationCall()


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


    #params are the same as liquidate() in liquidator.sol (and therefore pool.liquidationCall)
    def liquidationCall(self, collateral, debt, user, debtToCover, receiveAToken):
        #this is passed in to getFlashloan so that executeOperation has access to it to .call the liquidator contract
        payload = self.liquidatorContract.liquidate.encode_input(collateral, debt, user, debtToCover, receiveAToken)
        #execute the flashloan and liquidation
        self.flashLoanHelper.getFlashLoan(debt, debtToCover, payload)

        #probably return a bool for success/failure and realised profit if possible

    def calculateProfitability(self, debtToken, collateralToken):
       
        #see aave docs for details
        debtTokenPrice = self.aaveOracle.getAssetPrice(debtToken[0])
        collateralTokenPrice = self.aaveOracle.getAssetPrice(collateralToken[0])
        
        
        
        expectedProfit = ''

        return expectedProfit
    
    def calculateDebtToCover(self, debtToken, user):
        #debtToCover = (userStableDebt + userVariableDebt) * LiquidationCloseFactor
        #determine liquidationCloseFactor
        HF = self.aavePool.getUserAccountData(user)[-1]/(10**18)
        if HF > 0.95 and HF < 1: #0.95 if the CLOSE_FACTOR_HF_THRESHOLD
            liquidationCloseFactor = 0.5
        if HF < 0.95:
            liquidationCloseFactor = 1.0
        debtToCover = (debtToken[4] + debtToken[5]) * liquidationCloseFactor
        return debtToCover


    #returns liquidation bonus as a decimal
    def getLiquidationBonus(self, debtToken):
        #see aave docs pool.getReserve data for info on configuration bitmapping
        config = bin(self.pool.getConfiguration(debtToken[0])[0])
        liquidationBonus = int(config[-48:32],2)/(10**4) - 1
        return liquidationBonus

    #definitely going to have to double check that my numbers all have the correct decimals
    #mainly - should liqBonus be decimal or the original representation from the configuration i.e. 10500 or 500 instead of 0.5
    def calculateMaxCollateralToLiquidate(self, debtToCover, debtToken, collateralToken):
        liquidationBonus = self.getLiquidationBonus(collateralToken[0])
        debtAssetPrice = self.aaveOracle.getAssetPrice(debtToken[0])
        collateralAssetPrice = self.aaveOracle.getAssetPrice(collateralToken[0])
        maxAmountOfCollateralToLiquidate = (debtAssetPrice * debtToCover * liquidationBonus) / collateralAssetPrice
        return maxAmountOfCollateralToLiquidate

    #get the collateral token and debt token with largest balances
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
            
                
                    
                