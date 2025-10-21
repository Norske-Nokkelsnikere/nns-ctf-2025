import type { Game } from "./game"

export abstract class Block {
    id: string;
    constructor() {
        this.id = crypto.randomUUID();
    }
    abstract serialize(): object;
    abstract attach(game: Game): void;
    abstract dispose(game: Game): void;
}
export class PassBlock extends Block {
    serialize(): object {
        return {
            id: this.id,
            type: "pass"
        }
    }
    attach(game: Game): void {
        game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    dispose(game: Game): void {
        game.removeListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }

    private handleActiveBlock(game: Game): void {
        // Passing happens automagically
        console.log("pass");
    }
}
export class ResetBlock extends Block {
    attach(game: Game): void {
        game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    dispose(game: Game): void {
        game.removeListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    serialize(): object {
        return {
            id: this.id,
            type: "reset"
        }
    }
    private handleActiveBlock(game: Game): void {
        console.log("reset");
        game.loadLevel(game.levelId);
    }
}
export class NextLevelBlock extends Block {
    attach(game: Game): void {
        game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    dispose(game: Game): void {
        game.removeListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    serialize(): object {
        return {
            id: this.id,
            type: "next_level"
        }
    }
    private handleActiveBlock(game: Game): void {
        console.log("next_level");
        game.loadLevel(game.levelId+1);
    }
}
export class SlotBlock extends Block {
    private inner: Block;
    private activeBlockListener?: () => void;
    private messageListener?: (message: object) => void;
    constructor(inner: Block) {
        super();
        this.inner = inner;
    }
    attach(game: Game): void {
        // This recursion hack is probably not neccesary, but id rather not have angry infra maintainers so just being sure
        let isActive = false;
        this.activeBlockListener = () => {
            if (isActive) {
                throw "UH OH RECURSION";
            }
            isActive = true;
            this.handleActiveBlock(game);
            isActive = false;
        }
        this.messageListener = (message: object) => {
            if (message.type === "swap") {
                this.handleSwap(message, game);
            }
        }

        game.addListener(`activeBlock-${this.id}`, this.activeBlockListener);
        game.addListener("message", this.messageListener);
        this.inner.attach(game);
    }
    dispose(game: Game): void {
        if (this.activeBlockListener !== undefined) {
            game.removeListener(`activeBlock-${this.id}`, this.activeBlockListener);
        }
        if (this.messageListener !== undefined) {
            game.removeListener("message", this.messageListener);
        }
        this.inner.dispose(game);
    }
    serialize(): object {
        return {
            id: this.id,
            type: "slot",
            inner: this.inner.serialize()
        }
    }
    private handleActiveBlock(game: Game): void {
        game.executeBlock(this.inner);
    }
    private handleSwap(message: object, game: Game): void {
        if (message.from_slot !== this.id) {
            return;
        }

        for (let column of game.levelState) {
            for (let block of column) {
                if (block.id !== message.to_slot) {
                    continue;
                }
                let oldBlockState = block.inner;
                let oldSelfState = this.inner;
                block.inner = oldSelfState;
                this.inner = oldBlockState;

                console.log({block, t: this});
                game.syncLevel();
            }
        }
    }
}
export class FlagBlock extends Block {
    attach(game: Game): void {
        game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    dispose(game: Game): void {
        game.removeListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    private handleActiveBlock(game: Game): void {
        console.log("flag");
        game.send({"type": "flag", "data": process.env.FLAG ?? "there is no flag waiting on localhost"})
    }
    serialize(): object {
        return {
            id: this.id,
            type: "flag",
        }
    }

}
export class MoveCursorLeftBlock extends Block {
    constructor() {
        super();
    }
    attach(game: Game): void {
        game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    dispose(game: Game): void {
        game.removeListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    private handleActiveBlock(game: Game): void {
        console.log("move_cursor_left");
        if (game.cursorPosition === null) {
            throw ":(";
        }
        game.cursorPosition.x -= 1;
    }
    serialize(): object {
        return {
            id: this.id,
            type: "move_cursor_left",
        }
    }
}
export class MoveCursorRightBlock extends Block {
    attach(game: Game): void {
        game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    dispose(game: Game): void {
        game.removeListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    private handleActiveBlock(game: Game): void {
        console.log("move_cursor_right");
        if (game.cursorPosition === null) {
            throw ":(";
        }
        game.cursorPosition.x += 1;
    }
    serialize(): object {
        return {
            id: this.id,
            type: "move_cursor_right",
        }
    }
}
export class MoveRelativeBlock extends Block {
    listener?: () => void;
    x?: number;
    y?: number;
    attach(game: Game): void {
        game.addListener(`activeBlock-${this.id}`, this.handleActiveBlock);
        game.addListener("message", this.handleMessage);
    }
    dispose(game: Game): void {
        game.removeListener(`activeBlock-${this.id}`, this.handleActiveBlock)
    }
    private handleActiveBlock(game: Game): void {
        console.log("move_cursor_relative");
        if (game.cursorPosition === null) {
            throw ":(";
        }
        game.cursorPosition.x += this.x ?? 0;
        game.cursorPosition.y += this.y ?? 0;
    }
    serialize(): object {
        return {
            id: this.id,
            type: "move_relative",
            x: this.x,
            y: this.y
        }
    }
    private handleMessage(message) {
        if (message.type !== "move_relative_set") {
            return;
        }
        let {axis, value} = message;

        if (!["undefined", "number"].includes(typeof this[axis])) {
            return;
        }
        if (!(typeof value === "number")) {
            return;
        }
        value = Math.min(Math.max(value, -5), 5);
        this[axis] = value;
    }
}