# huffameg

- **Author:** hoover
- **Categories:** blockchain, huff

## Description

I don't understand, this just needs to return true! Hey Alexa, play "Tante Sofies sinte vise" until we've solved this challenge...


# Writeup

When examining `challenge.huff`, we stumble upon a function called `solve()`:

```huff
#define macro SOLVE() = takes (1) returns (1) {
    ONLY_OWNER()
    
    dup1
    [SOLVE_SIG]
    eq
    iszero               // oh wait
    success jumpi
    
    0x00 0x00 revert
    
    success:
        [SOLVE_SIG]
        swap1
        
        emitSolved()
        
        0x01
}
```

This function takes a value, duplicates it (so it can use it later), and compares it to a constant `SOLVE_SIG`. Here's the twist: if the values are **not** the same, the function returns "solved"!

`SOLVE_SIG` is defined further up and equals: `0x890d6908868e8ac13668278509dae455f142386153e7f121792f67b11b40f04b`

## The Challenge

The solution seems simple at first - we need to call `solve()` with a parameter that is **not** `SOLVE_SIG`. Easy peasy, right? Let's just do that and... oh wait. We also need to be the owner to call `solve()`. 

But don't worry! We have `implementation.sol` that gives us the function `callFunction()`. With that detour, the `solve()` function gets called by the owner and we get our flag, right? Right?!

```solidity
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
```

## The Plot Twist

Ahh no! The implementation of `callFunction()` is deceiving. First, it calculates a selector - the first four bytes of the keccak256 hash of the function signature (function name with "()" appended). This is how functions are identified and called in the EVM. So far, so good.

This selector is then combined with the **full hash** of the function signature to be sent to the target function. The selector calls the function, and the full hash becomes the... oh god... the **parameter**! 

So we can't choose our parameter freely. And the full hash of our function signature is, of course, equal to `SOLVE_SIG` - the ONE thing it's not allowed to be equal to!

## The Solution: Hash Collision Attack

We need to find a string that, when hashed, produces a different result from `SOLVE_SIG` while preserving the same selector (first four bytes). Essentially, we're looking for a keccak256 hash collision!

Since we only need a collision of the first four bytes, we can brute force it. The selector for `solve()` is `890d6908`. We just test random strings of increasing length until we get the same selector.

The corresponding Go script is [attached](./bruteforce.go) in this repository. (Shoutout to ChatGPT for translating it from python to go, python b slow)

After running our brute force script for five minutes, we get a collision! The string `d6l3eB()` produces the same selector as `solve()` but a different full hash. Yay!

## Exploitation

Now we send this collision string to the `callFunction()` at the implementation address:

```bash
cast send 0x6f1A46aacCD557F42d349b4999A1d63b10fdD37e "callFunction(string)" "d6l3eB" \
  --rpc-url https://c423299b-f15c-4b75-87f6-c2b92183f62b.chall.nnsc.tf/rpc \
  --private-key 0x441f31fe4bc26e0735af1e2b9bc18472cc10f5110c77e63463e8585e5150a141
```

We check the website for the emitted flag and collect our prize:

**Flag:** `NNS{huff_4_m3g_1_th0ugh_evm_funct10n_s1gn4tur3s_w3r3_s3cur3!!_0cb8449b4232}`
