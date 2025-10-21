// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";
import {Implementation} from "src/Implementation.sol";
import {DevOpsTools} from "foundry-devops/DevOpsTools.sol";

contract GetAddresses is Script {
    function run() public {
        address implementationAddress = DevOpsTools.get_most_recent_deployment("Implementation", block.chainid);
        
        if (implementationAddress == address(0)) {
            console.log("error: no implementation contract found");
            return;
        }
        
        Implementation implementation = Implementation(implementationAddress);
        address challengeAddress = implementation.getChallenge();
        address ownerAddress = implementation.getOwner();
        
        string memory json = string(abi.encodePacked(
            '{\n',
            '  "implementation_address": "', vm.toString(implementationAddress), '",\n',
            '  "challenge_address": "', vm.toString(challengeAddress), '",\n',
            '  "owner_address": "', vm.toString(ownerAddress), '"\n',
            '}'
        ));
        
        vm.writeFile("./contracts.json", json);
        
        console.log("contract addresses written to contracts.json");
        console.log("implementation:", implementationAddress);
        console.log("challenge:", challengeAddress);
        console.log("owner:", ownerAddress);
    }
}
