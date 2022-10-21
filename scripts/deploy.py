import os
from dotenv import load_dotenv
load_dotenv()
from brownie import *


#will be deploying liquidator and flashloanhelper from here
#and setting all contract aliases



aaveL2EncoderAddress = os.getenv('AAVE_L2_ENCODER')
uniswapRouterAddress = os.getenv('UNISWAP_ROUTER_ADDRESS')
wethAddress = os.getenv('WETH_ADDRESS')
wbtcAddress = os.getenv('WBTC_ADDRESS')
linkAddress = os.getenv('LINK_ADDRESS')
usdtAddress = os.getenv('USDT_ADDRESS')
usdcAddress = os.getenv('USDC_ADDRESS')
daiAddress = os.getenv('DAI_ADDRESS')

poolAddressProvider = Contract.from_explorer(os.getenv('AAVE_POOL_ADDRESSES_PROVIDER'))
poolAddressProvider.set_alias('PoolAddressProvider')

pool = Contract.from_explorer(poolAddressProvider.getPool()) 
pool.set_alias('Pool')

uiPoolDataProviderV3 = Contract.from_explorer(os.getenv('UI_POOL_DATA_PROVIDER_V3'))
uiPoolDataProviderV3.set_alias('UIPoolDataProviderV3')

aaveOracle = Contract.from_explorer(os.getenv('AAVE_ORACLE_ADDRESS'))
aaveOracle.set_alias('AaveOracle')

uniswapQuoter = Contract.from_explorer(os.getenv('UNISWAP_QUOTER_ADDRESS'))
uniswapQuoter.set_alias('UniswapQuoter')

weth = Contract.from_explorer(wethAddress)
weth.set_alias('Weth')

liquidatorContract = Liquidator.deploy(
    pool.address,
    aaveL2EncoderAddress,
    uniswapRouterAddress,
    wethAddress,
    wbtcAddress,
    linkAddress,
    usdtAddress,
    usdcAddress,
    daiAddress,
    {'from': accounts[0]}
)
liquidatorContract = Contract(liquidatorContract.address)
liquidatorContract.set_alias('Liquidator')

flashLoanHelperContract = FlashLoanHelper.deploy(
    pool.address,
    poolAddressProvider.address,
    liquidatorContract.address,
    wethAddress,
    wbtcAddress,
    linkAddress,
    usdtAddress,
    usdcAddress,
    daiAddress,
    {'from': accounts[0]}
)
flashLoanHelperContract = Contract(flashLoanHelperContract.address)
flashLoanHelperContract.set_alias('FlashLoanHelper')

def main():
    pass
main()