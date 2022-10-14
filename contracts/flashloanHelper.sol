//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {IPoolAddressesProvider} from './IPoolAddressesProvider.sol';
import '../interfaces/IPool.sol';

/*probably going to do it so I call this and it encodes params that get put throught he flashloan
 and then send back to the executeOperation fallback function and then used as the payload for a
 .call() to the liquidator contract to call the liquidation */


//will also want a withdraw function so I can withdraw rewards - will need onlyOwner if i go that route
//or have it automatically send rewards to the owner (probably the better option)

contract flashLoanHelper {

    IPool public immutable pool;
    IPoolAddressProvider public immutable poolAddressesProvider;


    constructor(address _poolAddress, address _poolAddressesProviderAddress) {
        pool = IPool(_poolAddress);
        poolAddressesProvider = IPoolAddressProvider(_poolAddressesProviderAddress);
    }

    function getFlashLoan(address debt, uint256 debtToCover, bytes params) public {
        aavePool.flashLoanSimple(address(this), debt, debtToCover, params, 0);
        /*I need to figure out how to call this so that params can be passed through here and into the
         executeOperation fallback function and then passed into the L2 encoder. So I might need to do a .call() 
         and either make a separate contract or see if I can use .call on adddress(this) */
    }

    //IFlashLoanSimpleReceiver functions:
    function executeOperation( //called by aave when executing the flashloan
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) public returns (bool) {
        //I want params to be a call to the liquidator function - do I need to make that a separate contract?
        //or can i do call on address(this) - or do I even need to worry about params if I'm doing
        //to be doing it all in one smart contract - don't need to do a .call() if I can just call liqudate
        //as an internal function here - BUT i do need to figure out how to get these 
    }

    function ADDRESSES_PROVIDER() public view returns (IPoolAddressesProvider) {
        return poolAddressesProvider;
    }

    function POOL() public view returns (IPool) {
        return pool;
    }


}