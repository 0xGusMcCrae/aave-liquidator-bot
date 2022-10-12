//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

//import '@openzeppelin/contracts/access/Ownable.sol';
import '../interfaces/IAaveL2Encoder.sol';
import '../interfaces/IAavePool.sol';

//will also want a withdraw function so I can withdraw rewards
//or have it automatically send rewards to the owner (probably the better option)

//not sure if will need address providers in here or if they can just be in
//the python script

contract Liquidator/* is Ownable */{

    address public immutable aavePoolAddress;
    address public immutable aaveL2EncoderAddress;
    IAaveL2Encoder private immutable aaveL2Encoder;
    IAavePool private immutable aavePool;

    constructor(address _aavePoolAddress, address _aaveL2EncoderAddress) {
        aavePoolAddress = _aavePoolAddress;
        aaveL2EncoderAddress = _aaveL2EncoderAddress;

        aavePool = IAavePool(aavePoolAddress);
        aaveL2Encoder = IAaveL2Encoder(aaveL2EncoderAddress);
    }

    
    function liquidate(
        address collateral, //address of collateral token
        address debt, //address of debt token
        address user, //account to be liquidated
        uint256 debtToCover, //set to uint(-1) to proceed with max, other wise the amount of debt to liquidate
        bool receiveAToken //True to receive aTokens, false to receive the underlying collateral
    ) external {
        //call flashfloan
        /*need to make sure debtToCover is being handled correctly if I'm passing -1 in from the python bot,
         might just leave blank and hardcode uint(-1) if it gives me issues*/
        (bytes32 args1, bytes32 args2) = aaveL2Encoder.encodeLiquidationCall(collateral, debt, user, debtToCover, receiveAToken);
        aavePool.liquidationCall(args1, args2); 
    }



}