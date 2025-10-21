import { css, html, LitElement } from "lit";
import { map } from "lit/directives/map.js";
import "./block.js"

class BoardElement extends LitElement {
    static styles = css`
        .lines {
            display: flex;
            gap: 2rem;
        }
        .line {
            display: grid;
            grid-template-columns: 2rem max-content;
        }
        .cursor {
            color: green;
        }
    `;
    constructor() {
        super();
        this.blocks = [];
        this.cursorPosition = {x: 0, y: 0};
    }
    static properties = {
        blocks: {},
        cursorPosition: {}
    };
    render() {
        console.log(this.blocks);
        return html`
            <div class="lines">
                ${map(this.blocks, ((line, x) => html`
                    <div class="line">
                        ${map(line, (block, y) => html`
                                <div class="cursor-slot">
                                    ${this.cursorPosition.x === x && this.cursorPosition.y === y ? html`<span class="cursor">-&gt;</span>` : null} 
                                </div>
                                <div class="instruction-slot">
                                    <ttwh-block .state=${block}></ttwh-block>
                                </div>
                            </div>
                        `)}
                    </div>
                `))}
            </div>
        `
    }
}
customElements.define("ttwh-board", BoardElement);