
import { css, html, LitElement } from "lit";

class BlockElement extends LitElement {
    static styles = css`
        .unknown {
            color: red;
        }
        .pass {
            color: lightgray;
        }
        .slot {
            padding: .5rem;
            border: 1px solid white;
        }
        .slot > * {
            cursor: grab;
        }
        .reset {
            color: red;
        }
        .next-level {
            color: green;
        }
        .move_relative {
            color: lightgray;
        }
        .move_cursor_left {
            color: lightgray;
        }
        .move_cursor_right {
            color: lightgray;
        }
        .flag {
            color: lightgray;
        }
    `;
    constructor() {
        super();
        this.state = undefined;
    }
    static properties = {
        state: {}
    }
    render() {
        if (this.state === undefined) {
            return html``;
        }
        if (this.state.type === "pass") {
            return html`<span class="pass">pass</span>`;
        }
        if (this.state.type === "slot") {
            return html`
                <div
                    class="slot"
                    @dragover=${(event) => {
                        if (event.dataTransfer.types.includes("ttwh/slot")) {
                            event.preventDefault();
                        }
                    }}
                    @drop=${(event) => {
                        let otherSlotId = event.dataTransfer.getData("ttwh/slot");
                        window.ws.send(JSON.stringify({"type": "swap", "from_slot": otherSlotId, "to_slot": this.state.id}));
                    }}
                >
                    <ttwh-block
                        .state=${this.state.inner}
                        draggable=${true}
                        @dragstart=${(event) => {
                            event.dataTransfer.setData("ttwh/slot", this.state.id);
                        }}
                    ></ttwh-block>
                </div>
            `;
        }
        if (this.state.type === "reset") {
            return html`<span class="reset">reset_level&lpar;&rpar;</span>`;
        }
        if (this.state.type === "next_level") {
            return html`<span class="next-level">next_level&lpar;&rpar;</span>`;
        }
        if (this.state.type === "move_relative") {
            return html`
                <span class="move_relative">move_relative&lpar;{x: ${this.createMoveRelativeAxis("x")}, y: ${this.createMoveRelativeAxis("y")}}&rpar;</span>
            `
        }
		if (this.state.type === "move_cursor_left") {
			return html`<span class="move_cursor_left">move_cursor_left()</span>`;
		}
		if (this.state.type === "move_cursor_right") {
			return html`<span class="move_cursor_left">move_cursor_right()</span>`;
		}
		if (this.state.type === "flag") {
			return html`<span class="flag">print(flag)</span>`;
		}
		
        return html`<span class="unknown">raise NotImplementedError&lpar;&quot;missing frontend ui for \\&quot;${this.state.type}\\&quot;&quot;&rpar;</span>`
    }
    createMoveRelativeAxis(axis) {
        return html`
            <input
                type="number"
                min="-5"
                max="5"
                value=${this.state[axis] ?? 0}
                @input=${(event) => {
                    window.ws.send(JSON.stringify({
                        "type": "move_relative_set",
                        axis,
                        value: parseInt(event.target.value)
                    }))
                }}
            >
        `;
    }
}
customElements.define("ttwh-block", BlockElement);
