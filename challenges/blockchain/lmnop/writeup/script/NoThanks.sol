// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

interface ISimpleBank {
    function withdraw(bytes32, uint8, bytes32, bytes32) external payable;
} 

contract NoThanks {
    address immutable bank;
    address immutable owner;

    error NoNo();
    error NoThankYou();

    constructor(address _bank, address _owner) {
        bank = _bank;
        owner = _owner;
    }

    function makeCall(bytes32 _hash, uint8 _v, bytes32 _r, bytes32 _s) external {
        ISimpleBank(bank).withdraw(_hash, _v, _r, _s);
    }

    function withdrawCoins() external {
        if (msg.sender != owner) revert NoNo();
        payable(msg.sender).transfer(address(this).balance);
    }
    
    receive() external payable {
        if (msg.value < 10 ether) revert NoThankYou();
    }

    fallback() external payable {
        if (msg.value < 10 ether) revert NoThankYou();
    }
}