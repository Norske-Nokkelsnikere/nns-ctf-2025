// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";
import {Implementation} from "src/Implementation.sol";

contract DeployChallenge is Script {
    function run() public {
        vm.startBroadcast();
        bytes memory bytecode = get_bytecode("challenge");

        Implementation implementation = new Implementation(bytecode);

        // fund challenge contract with 1000 ether
        address challengeAddr = address(implementation.challenge());
        payable(challengeAddr).transfer(1000 ether);


        bool isSolved = implementation.isSolved();
        console.log("challenge state is:", isSolved);

        vm.stopBroadcast();        
    }

    function get_bytecode(string memory filename) public returns (bytes memory) {
        string[] memory cmds = new string[](3);
        cmds[0] = "huffc";
        cmds[1] = string(abi.encodePacked("src/", filename, ".huff"));
        cmds[2] = "--bytecode";

        bytes memory bytecode = vm.ffi(cmds);
        return bytecode;
    }
}