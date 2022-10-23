from brownie import *
import os
from dotenv import load_dotenv
import time

load_dotenv()

#deposit ETH into AAVE and borrow the max possible amount of stablecoins
#when interest is applied, the account should be liquidatable.

account = accounts[0]

weth = Contract.from_explorer(os.getenv('WETH_ADDRESS'))
usdc = Contract.from_explorer(os.getenv('USDC_ADDRESS'))

poolAddressProvider = Contract.from_explorer(os.getenv('AAVE_POOL_ADDRESSES_PROVIDER'))

pool = Contract.from_explorer(poolAddressProvider.getPool()) \

aaveOracle = Contract.from_explorer(os.getenv('AAVE_ORACLE_ADDRESS'))

amount = 10*10**18 #10 ETH

weth.deposit({'from': account, 'value': amount})

weth.approve(pool.address, amount, {'from': account})

pool.supply(weth.address, amount, account.address, 0,{'from': account})

#pool.getUserAccountData(account.address)

wethPrice = aaveOracle.getAssetPrice(weth.address)*(10**-8)

#apparently usdc only has 6 decimals, not 18
#but i think the oracle is only returning weth price with 8 decimals
borrowAmount = int(amount * wethPrice .8*10**(usdc.decimals()-weth.decimals()))

pool.borrow(usdc.address,borrowAmount,1,0,account.address,{'from': account})

#revert 36 means you're trying to borrow too much


#no wait for HF to go below 1
HF = pool.getUserAccountData(account.address)[5]*10**-18
while HF > 1:
    HF = pool.getUserAccountData(account.address)[5]*10**-18
    print(f"HF: {HF}")
    time.sleep(15)


#does eth price even change since nobody's trading onchain? I guess not
#but there should still be interest accumulating so idk. I'll try to 
#figure it out tomottow