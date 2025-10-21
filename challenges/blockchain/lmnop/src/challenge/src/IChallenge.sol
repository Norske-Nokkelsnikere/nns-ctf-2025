// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

interface IChallenge {
    function withdraw(bytes32, uint8, bytes32, bytes32) external payable;
    function owner() external view returns (address);
} 