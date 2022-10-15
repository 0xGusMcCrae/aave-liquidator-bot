//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import '../interfaces/IAaveL2Encoder.sol';
import '../interfaces/IPool.sol';
import '../interfaces/IERC20';

contract Liquidator {

    IAaveL2Encoder public immutable aaveL2Encoder;
    IPool public immutable pool;

    constructor(address _poolAddress, address _aaveL2EncoderAddress) {
        pool = IAavePool(_poolAddress);
        aaveL2Encoder = IAaveL2Encoder(_aaveL2EncoderAddress);
        //max approve all possible assets for aave pool spend
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

    
    function liquidate(
        address collateral, //address of collateral token
        address debt, //address of debt token
        address user, //account to be liquidated
        uint256 debtToCover, //set to uint(-1) to proceed with max, other wise the amount of debt to liquidate. Might need to calculate this since I gotta call the flashloan
        bool receiveAToken //True to receive aTokens, false to receive the underlying collateral
    ) public {
        (bytes32 args1, bytes32 args2) = aaveL2Encoder.encodeLiquidationCall(collateral, debt, user, debtToCover, receiveAToken);
        pool.liquidationCall(args1, args2); 
        //send liquidated collateral rewards back to caller of liqudiate function (flashloanHelper)
        // is it collateral or debt that I get back??? I'm flashloaning the debt token but I think i get collateral back
        IERC20(collateral).transfer(
            msg.sender,
            IERC20(collateral).balanceOf(address(this))
        );
    }


}