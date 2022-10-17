//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import '../interfaces/IAaveL2Encoder.sol';
import '../interfaces/IPool.sol';
import '../interfaces/IERC20.sol';
import '../interfaces/ISwapRouter.sol';

contract Liquidator {

    IAaveL2Encoder public immutable aaveL2Encoder;
    IPool public immutable pool;
    address public immutable wethAddress; //only weth is needed as a state variable because its the path intermediary in uniswap swap
    ISwapRouter public immutable uniswapRouter;

    constructor(
        address _poolAddress, 
        address _aaveL2EncoderAddress,
        address _uniswapRouter,
        address wethAddress,
        address wbtcAddress,
        address linkAddress,
        address usdtAddress,
        address usdcAddress,
        address daiAddress
        ) {
        pool = IAavePool(_poolAddress);
        aaveL2Encoder = IAaveL2Encoder(_aaveL2EncoderAddress);
        uniswapRouter = ISwapRouter(_uniswapRouter);
        //max approve all possible assets for aave pool spend
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
        //Max approve all possible assets for uniswapv3 router (to swap collateral bonus back to debt token for flashloan repayment)
        //wETH
        IERC20(wethAddress).approve(_uniswapRouter,2^256 - 1);
        //wBTC
        IERC20(wbtcAddress).approve(_uniswapRouter,2^256 - 1);
        //LINK
        IERC20(linkAddress).approve(_uniswapRouter,2^256 - 1);
        //USDT
        IERC20(usdtAddress).approve(_uniswapRouter,2^256 - 1);
        //USDC
        IERC20(usdcAddress).approve(_uniswapRouter,2^256 - 1);
        //DAI
        IERC20(daiAddress).approve(_uniswapRouter,2^256 - 1);
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
        //swap liquidated collateral back to debt token and send back to flashloanHelper to be repaid
        bytes swapPath;
        if(collateral == wethAddress || debt == wethAddress){
            swapPath = abi.encodePacked(collateral, 3000, debt); //3000 = 0.3% pool fee
        } else {
            swapPath = abi.encodePacked(collateral, 3000, wethAddress, 3000, debt);
        }
        uniswapRouter.exactInput(ISwapRouter.ExactInputParams({ 
            path: swapPath,                                        
            recipient: msg.sender,                                 
            deadline: block.timestamp + 30,                        
            amountIn: IERC20(collateral).balanceOf(address(this)), 
            amountOutMin: debtToCover * 1.0075 //debtToCover + 0.05% premium (subject to change) + buffer 
        }));
    }


}