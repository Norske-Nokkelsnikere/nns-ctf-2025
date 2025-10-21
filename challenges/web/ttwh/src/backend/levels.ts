import { Block, FlagBlock, MoveCursorRightBlock, MoveRelativeBlock, NextLevelBlock, PassBlock, ResetBlock, SlotBlock } from "./blocks.ts";

export function createLevel0(): Block[][] {
    return [
        [
            new PassBlock(),
            new PassBlock(),
            new SlotBlock(new ResetBlock()),
        ],
        [
            new SlotBlock(new MoveCursorRightBlock()),
            new PassBlock(),
            new NextLevelBlock(),
        ]
    ]
}
export function createLevel1(): Block[][] {
    return [
        [
            new PassBlock(),
            new MoveRelativeBlock(),
            new ResetBlock()
        ],
        [
            new NextLevelBlock(),
        ]
    ]
}
export function createLevel2(): Block[][] {
    return [
        [
            new PassBlock(),
            new MoveRelativeBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new ResetBlock(),
            new ResetBlock(),
            new ResetBlock()
        ],
        [
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new ResetBlock(),
            new NextLevelBlock(),
            new ResetBlock()
        ],
        [
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new PassBlock(),
            new ResetBlock(),
            new ResetBlock(),
            new ResetBlock()
        ],
    ]
}
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
