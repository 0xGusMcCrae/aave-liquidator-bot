//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {IPoolAddressesProvider} from '../interfaces/IPoolAddressesProvider.sol';
import '../interfaces/IPool.sol';
import '../interfaces/IERC20.sol';


contract FlashLoanHelper {

    IPool public immutable pool;
    IPoolAddressesProvider public immutable poolAddressesProvider;
    address public immutable liquidator;


    constructor(
        address _poolAddress, 
        address _poolAddressesProviderAddress, 
        address _liquidator, 
        address wethAddress,
        address wbtcAddress,
        address linkAddress,
        address usdtAddress,
        address usdcAddress,
        address daiAddress
        ) {
        pool = IPool(_poolAddress);
        poolAddressesProvider = IPoolAddressesProvider(_poolAddressesProviderAddress);
        liquidator = _liquidator;
        //max approve all possible assets for aave pool spend (to repay flashloan)
        //wETH
        IERC20(wethAddress).approve(_poolAddress,2^256 - 1);
        //wBTC
        IERC20(wbtcAddress).approve(_poolAddress,2^256 - 1);
        //LINK
        IERC20(linkAddress).approve(_poolAddress,2^256 - 1);
        //USDT
        IERC20(usdtAddress).approve(_poolAddress,2^256 - 1);
        //USDC
        IERC20(usdcAddress).approve(_poolAddress,2^256 - 1);
        //DAI
        IERC20(daiAddress).approve(_poolAddress,2^256 - 1);
        
    }

    // params is the encoded payload that will be used to call the liquidator contract in executeOperation
    function getFlashLoan(address debt, uint256 debtToCover, bytes calldata params) public {
        pool.flashLoanSimple(address(this), debt, debtToCover, params, 0);
        //send the profit back to bot address
        IERC20(debt).transfer(msg.sender,IERC20(debt).balanceOf(address(this)));
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

        // liquidator will liquidate positions, swap collateral + bonus back to debt token and send back here to be repaid
        
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