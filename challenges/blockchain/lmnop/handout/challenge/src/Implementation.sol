// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {IChallenge} from "./IChallenge.sol";

contract Implementation {
    address public challengeContract;

    error HuffChallengeDeployFailed();
    
    event ChallengeDeployed(address indexed challengeAddress);
    

    constructor(bytes memory bytecode) {        
        address deployedAddress;

        assembly {
            let bytecodeLength := mload(bytecode)
            let bytecodePtr := add(bytecode, 0x20)            
            deployedAddress := create(0, bytecodePtr, bytecodeLength)
        }

        if (deployedAddress == address(0)) {
            revert HuffChallengeDeployFailed();
        }

        challengeContract = deployedAddress;

        emit ChallengeDeployed(challengeContract);
    }

    function isSolved() external view returns (bool) {
        return address(challengeContract).balance == 0;
    }

    function getChallenge() external view returns (address) {
        return challengeContract;
    }

    function challenge() external view returns (IChallenge) {
        return IChallenge(challengeContract);
    }

    function owner() external view returns (address) {
        return IChallenge(challengeContract).owner();
    }
}