//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface IAavePool {
    //feed in results of L2Encoder's encodeLiquidationCall()
    function liquidationCall(bytes32 args1, bytes32 args2) external;
}