#delete the imports I don't need
import web3
import time 
from brownie import *
#from brownie import interface
import os
from dotenv import load_dotenv
import pandas
import eth_abi.packed

load_dotenv()

#log into account beforehand and feed into constructor
#deploy liquidator and flashLoanHelper and set appropriate aliases beforehand
class liquidator:
    def __init__(self, account):
        self.account = account
        self.liquidatorContract = Contract('Liquidator')
        self.flashLoanHelperContract = Contract('FlashLoanHelper')
        self.poolAddressProvider = Contract('PoolAddressProvider')
        self.pool = Contract('Pool')
        self.uiPoolDataProviderV3 = Contract('UIPoolDataProviderV3')
        self.aaveOracle = Contract('AaveOracle')
        self.uniswapQuoter = Contract('UniswapQuoter')
        self.weth = Contract('Weth')
        #token approvals
        

    def main(self):
        while(True): 
            liquidatableAccounts = self.getLiquidatableAccounts()
            for user in liquidatableAccounts:
                debtToken, collateralToken = self.getDebtAndCollateralTokens(user)
                #eurs liquidity is too low, skip if it's either debt or collateral
                eurs = Contract('eurs').address #this alias was set in deploy.py
                if debtToken[0] == eurs or collateralToken[0] == eurs:
                    continue
                debtToCover = self.calculateDebtToCover(debtToken, user)
                gasEstimate = self.estimateGas(collateralToken[0], debtToken[0], user, debtToCover, 0)
                expectedProfit = self.calculateProfitability(debtToken, collateralToken, gasEstimate)
                if expectedProfit > 0: #probably will be setting this higher than zero
                    self.liquidationCall(collateralToken[0], debtToken[0], user, debtToCover, 0)
                    #execute uniswap swap and print current eth balance
                    self.executeSwapTokensForEth(debtToken[0])
                    print(f"Current ETH balance: {self.account.balance()}")


    def getLiquidatableAccounts(self):
        df = pandas.read_csv('data/test.csv')
        #then df.users can be iterated through - it's a list of address strings
        #load csv, loop through accounts, return accounts with 
        #HF < 1
        liquidatableAccounts = []
        for user in df.users:
            HF = self.pool.getUserAccountData(user)[-1]/(10**18)
            if HF < 1:
                liquidatableAccounts.append(user)
        return liquidatableAccounts


    #params are the same as liquidate() in liquidator.sol (and therefore pool.liquidationCall)
    def liquidationCall(self, collateral, debt, user, debtToCover, receiveAToken):
        #this is passed in to getFlashloan so that executeOperation has access to it to .call the liquidator contract
        payload = self.liquidatorContract.liquidate.encode_input(collateral, debt, user, debtToCover, receiveAToken)
        #execute the flashloan and liquidation
        self.flashLoanHelper.getFlashLoan(debt, debtToCover, payload, {'from':self.account})

        #probably return a bool for success/failure and realised profit if possible
        #could do the account's balance of the debt token to check profit

    def calculateProfitability(self, debtToken, collateralToken, debtToCover, gasEstimate):
        #see aave docs for details
        collateralTokenPrice = self.aaveOracle.getAssetPrice(collateralToken[0])
        liquidationBonus = self.getLiquidationBonus(collateralToken)
        maxAmountOfCollateralToLiquidate = self.calculateMaxCollateralToLiquidate(self, debtToCover, debtToken, collateralToken)
        collateralBonus = maxAmountOfCollateralToLiquidate * (1 - liquidationBonus) * collateralTokenPrice  
        #include uniswap swap from collateral back to debt here
        if collateralToken[0] == self.weth.address or debtToken[0] == self.weth.address:
            path = eth_abi.packed.encode_abi_packed(
                ['address','uint24','address'],
                [collateralToken[0],3000,debtToken[0]]
            )
        else:    
            path = eth_abi.packed.encode_abi_packed(
                ['address','uint24','address','uint24','address'],
                [collateralToken[0],3000,self.weth.address,3000,debtToken[0]]
            )
        amountIn = debtToCover + collateralBonus # double check this
        uniswapAmountOut = self.uniswapQuoter.quoteExactInput.call(path, amountIn) #call so it doesn't use gas - the tx is designed to revert anyway
        expectedProfit = uniswapAmountOut - debtToCover*(1+(self.pool.FLASHLOAN_PREMIUM_TOTAL()/(10**4))) - gasEstimate #total debt token return minus flashloan payback minus gas to execute tx
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
    def getLiquidationBonus(self, collateralToken):
        #see aave docs pool.getReserve data for info on configuration bitmapping
        config = bin(self.pool.getConfiguration(collateralToken[0])[0])
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


    #use web3.py library to estimate transaction gas
    def estimateGas(self,collateral, debt, user, debtToCover, receiveAToken):
        web3_FLH = web3.eth.contract(address=self.flashLoanHelperContract.address, abi=self.flashLoanHelperContract.abi)
        payload = self.liquidatorContract.liquidate.encode_input(collateral, debt, user, debtToCover, receiveAToken)
        gasEstimate = web3_FLH.functions.getFlashLoan(debt, debtToCover, payload).estimateGas()
        return gasEstimate

    def executeSwapTokensForEth(self,tokenAddress):
        #swap tokens for WETH
        if tokenAddress != self.weth.address:
            tokenContract = interface.IERC20(tokenAddress)
            amountIn = tokenContract.balanceOf(self.account.address)
            if tokenContract.allowance(self.account.address,self.uniswapRouter.address) < amountIn:
                tokenContract.approve(self.uniswapRouter.address,2**256-1,{'from': self.account})
            self.uniswapRouter.exactInputSingle(
                (
                    tokenAddress,           #token in
                    self.weth.address,      #token out
                    3000,                   #fee
                    self.account.address,   #recipient
                    999999999999999,        #deadline
                    amountIn,               #amountIn
                    0,                      #amountOutMinimum - I'll probably want to change this so I don't get destroyed by frontrunners
                    0,                      #sqrtPriceLimitX96
                    {'from': self.account}
                )
            )
        #I'll need to execute the swap from the token to weth and then burn the weth 
        #for ETH using withdraw(wethAmountToBurnForETH) on the weth contract 
        if self.weth.allowance(self.account.address, self.weth.address) < self.weth.balanceOf(self.account.address):
            self.weth.approve(self.weth.address,2**256-1,{'from': self.account})       
        self.weth.withdraw(self.weth.balanceOf(self.account.address),{'from':self.account})
         


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
            
                
                    
                