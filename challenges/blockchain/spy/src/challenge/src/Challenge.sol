// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

contract Challenge {
    constructor(bytes memory data, address payable target) {
        selfdestruct(target);
    }
}
