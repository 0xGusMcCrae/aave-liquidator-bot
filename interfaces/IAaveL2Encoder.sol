//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface IAaveL2Encoder {
    function encodeLiquidationCall(
        address collateral, //address of collateral reserve
        address debt, //address of debt reserve
        address user, //account to be liquidated
        uint256 debtToCover, //set to uint(-1) to proceed with maximum allowable amount
        bool receiveAToken //false to receive the underlying collateral
    ) external view returns (bytes32, bytes32);
}