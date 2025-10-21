// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";
import {Challenge} from "../src/Challenge.sol";

contract DeployChallenge is Script {
    function run() external {
        vm.startBroadcast();

        string memory flag = vm.envString("FLAG");
        address payable target = payable(msg.sender);
        
        Challenge challenge = new Challenge(bytes(flag), target);

        vm.stopBroadcast();

        string memory json = string(abi.encodePacked(
            '{\n',
            '  "challenge_address": "', vm.toString(address(challenge)), '"\n',
            '}'
        ));
        
        vm.writeFile("./contracts.json", json);
        
        console.log("contract addresses written to contracts.json");
        console.log("challenge:", address(challenge));
    }

}
