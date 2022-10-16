//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {IPoolAddressesProvider} from './IPoolAddressesProvider.sol';
import '../interfaces/IPool.sol';
import '../interfaces/IERC20';

/*probably going to do it so I call this and it encodes params that get put throught he flashloan
 and then send back to the executeOperation fallback function and then used as the payload for a
 .call() to the liquidator contract to call the liquidation */


//will also want a withdraw function so I can withdraw rewards - will need onlyOwner if i go that route
//or have it automatically send rewards to the owner (probably the better option)

//will either want to feed liquidator address in as a constructor param or as a getflashloan param
//because I need to be able to access it within the executeOperation function to call it

contract flashLoanHelper {

    IPool public immutable pool;
    IPoolAddressProvider public immutable poolAddressesProvider;
    address public immutable liquidator;


    constructor(address _poolAddress, address _poolAddressesProviderAddress, address _liquidator) {
        pool = IPool(_poolAddress);
        poolAddressesProvider = IPoolAddressProvider(_poolAddressesProviderAddress);
        liquidator = _liquidator;
        //max approve all possible assets for aave pool spend (to repay flashloan)
        //wETH
        IERC20(0x82aF49447D8a07e3bd95BD0d56f35241523fBab1).approve(_poolAddress,2^256 - 1);
        //wBTC
        IERC20(0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f).approve(_poolAddress,2^256 - 1);
        //LINK
        IERC20(0xf97f4df75117a78c1A5a0DBb814Af92458539FB4).approve(_poolAddress,2^256 - 1);
        //USDT
        IERC20(0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9).approve(_poolAddress,2^256 - 1);
        //USDC
        IERC20(0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8).approve(_poolAddress,2^256 - 1);
        //DAI
        IERC20(0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1).approve(_poolAddress,2^256 - 1);
    }

    function getFlashLoan(address debt, uint256 debtToCover, bytes params) public {
        aavePool.flashLoanSimple(address(this), debt, debtToCover, params, 0);
    }



    //IFlashLoanSimpleReceiver functions:
    function executeOperation( //called by aave when executing the flashloan
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) public returns (bool) {
        //transfer loan to liquidator
        IERC20(asset).transfer(liquidator,amount);
        //call the liquidate function with pre-encoded payload that was fed into getFlashLoan()
        liquidator.call(params);
        //trade collateral received from liquidation back to borrowed debt asset on uniswap

        //repay flashloan
        //since debt assets are pre-approved, the pool calls safeTransferFrom to take them back
        //so need to make sure I have amount+premium of asset on hand at end of function but I 
        //don't actually transfer them back to the pool
        

    }

    function ADDRESSES_PROVIDER() public view returns (IPoolAddressesProvider) {
        return poolAddressesProvider;
    }

    function POOL() public view returns (IPool) {
        return pool;
    }


}