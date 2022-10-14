//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import '../interfaces/IAaveL2Encoder.sol';
import '../interfaces/IPool.sol';





contract Liquidator {

    IAaveL2Encoder public immutable aaveL2Encoder;
    IPool public immutable pool;

    constructor(address _poolAddress, address _aaveL2EncoderAddress) {
        pool = IAavePool(_poolAddress);
        aaveL2Encoder = IAaveL2Encoder(_aaveL2EncoderAddress);
    }

    
    function liquidate(
        address collateral, //address of collateral token
        address debt, //address of debt token
        address user, //account to be liquidated
        uint256 debtToCover, //set to uint(-1) to proceed with max, other wise the amount of debt to liquidate. Might need to calculate this since I gotta call the flashloan
        bool receiveAToken //True to receive aTokens, false to receive the underlying collateral
    ) public {
        (bytes32 args1, bytes32 args2) = aaveL2Encoder.encodeLiquidationCall(collateral, debt, user, debtToCover, receiveAToken);
        pool.liquidationCall(args1, args2); 
        //gonna need something here that sends the rewards back to the flashloan helper so it can repay the flashloan
    }


}