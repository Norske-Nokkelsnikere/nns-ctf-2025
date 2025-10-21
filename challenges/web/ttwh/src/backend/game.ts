import { EventEmitter } from "node:events";
import { Block, NextLevelBlock } from "./blocks.ts";
import {createLevel0, createLevel1, createLevel2, createLevel3} from "./levels.ts"
import type { Vector2 } from "./types.ts";

const LEVEL_FACTORIES = {
    0: createLevel0,
    1: createLevel1,
    2: createLevel2,
    3: createLevel3
}


export class Game extends EventEmitter {
    private connection;
    public levelId: number;
    public levelState: Block[][];
    public cursorPosition: Vector2;
    constructor(connection) {
        super();

        this.cursorPosition = {x: 0, y: 0};
        this.connection = connection;
        this.connection.addEventListener("message", (event) => {
            this.onMessage(JSON.parse(event.data));
        });
        this.levelId = 0;
        this.levelState = [];
        this.start();
    }
    private start() {
        this.loadLevel(0);
        setInterval(() => this.step(), 1000);
    }
    public send(data: object): void {
        this.connection.send(JSON.stringify(data));
    }
    public loadLevel(levelId: number): void {
        for (let row of this.levelState) {
            for (let block of row) {
                block.dispose(this);
            }
        }
        console.log("loading level", levelId);
        this.cursorPosition = {x: 0, y: 0};
        this.levelId = levelId;
        this.levelState = LEVEL_FACTORIES[levelId]();
        for (let row of this.levelState) {
            for (let block of row) {
                block.attach(this);
            }
        }
        this.syncLevel();
        this.send({"type": "cursor_position", "data": this.cursorPosition});
    }
    public syncLevel(): void {
        let rows = this.levelState.map(row => row.map(element => element.serialize()))
        this.send({"type": "level", "data": {state: rows, id: this.levelId}});
    }
    private step(): void {
        let activeBlock = (this.levelState[this.cursorPosition.x] ?? [])[this.cursorPosition.y];
        if (activeBlock !== undefined) {
            let previousLevelId = this.levelId;
            let previousCursorPosition = structuredClone(this.cursorPosition);
            this.executeBlock(activeBlock);
            if (this.levelId === previousLevelId && this.cursorPosition.x === previousCursorPosition.x && this.cursorPosition.y === previousCursorPosition.y) {
                this.cursorPosition.y++;
            }
        } else {
            this.cursorPosition = {x: 0, y: 0};
        }
        this.send({"type": "cursor_position", "data": this.cursorPosition});

    }
    public executeBlock(block: Block): void {
        this.emit(`activeBlock-${block.id}`, this);
    }
    private onMessage(message: object): void {
        this.emit("message", message);
    }
}
