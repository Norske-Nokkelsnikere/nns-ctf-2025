// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

interface IChallenge {
    function solve(bytes32) external returns (bool);
    function owner() external view returns (address);
}

contract Implementation {
    address public challengeContract;
    address public owner;
    bool public isSolved;

    error HuffChallengeDeployFailed();
    
    event ChallengeDeployed(address indexed challengeAddress, address indexed owner);
    
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
        owner = IChallenge(challengeContract).owner();

        emit ChallengeDeployed(challengeContract, owner);
    }
    
    /**
     * @notice Get the deployed challenge contract address
     * @return The address of the deployed challenge contract
     */
    function getChallenge() external view returns (address) {
        return challengeContract;
    }
    
    /**
     * @notice Get the challenge contract interface
     * @return IChallenge interface to interact with the deployed contract
     */
    function challenge() external view returns (IChallenge) {
        return IChallenge(challengeContract);
    }
    
    /**
     * @notice Forward function call to the challenge contract
     * @dev This is the only way for users to call functions in the challenge contract
     * @param functionName The function to call as a string
     * @return success Whether the function execution call was successful
     */
    function callFunction(string memory functionName) external returns (bool success) {
        string memory functionSignature = string(abi.encodePacked(functionName, "()"));
        bytes4 selector = bytes4(keccak256(bytes(functionSignature)));
        bytes32 fullHash = keccak256(bytes(functionSignature));
        bytes memory callData = abi.encodePacked(selector, fullHash);

        (success, ) = address(challengeContract).call(callData);

        if (success) {
            isSolved = true;
        }

        return success;
    }
    
    /**
     * @notice Get the deployer of this implementation contract
     * @return address deployer address
     */
    function getOwner() external view returns (address) {
        return owner;
    }
}
