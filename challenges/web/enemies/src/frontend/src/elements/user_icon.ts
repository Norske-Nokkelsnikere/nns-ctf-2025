import { css, html, LitElement, svg, type CSSResultGroup, type HTMLTemplateResult, type SVGTemplateResult } from "lit";
import { customElement, property } from "lit/decorators.js";
import seedRandom, { type PRNG } from "seedrandom";
import type { Vector2 } from "../lib/types";

@customElement("enmy-user-icon")
export class EnemyUserIconElement extends LitElement {

	@property({type: Number})
	userId?: number;

	public constructor() {
		super();
	}

	connectedCallback(): void {
		super.connectedCallback();
		console.log("icon loaded")
	}

	private generatePoint(numberGenerator: PRNG): Vector2 {
		let point: Vector2 = {x: 0, y: 0};
		point.x = Math.round(numberGenerator() * 4);
		point.y = Math.round(numberGenerator() * 4);
		return point;
	}

	private generateLines(amount: number, numberGenerator: PRNG): SVGTemplateResult {
		let pointString: string = "";

		for (let i = 0; i < amount; i ++) {
			const point = this.generatePoint(numberGenerator);
			pointString += `${point.x * 8},${point.y * 8} `
		}

		return svg`<polyline points=${pointString} />`;
	}

	protected render(): HTMLTemplateResult {
		if (this.userId === undefined) {
			return html`<svg width=32 height=32></svg>`;
		}
		const numberGenerator = seedRandom(this.userId.toString());
		return html`
			<svg width=32 height=32>${this.generateLines(10, numberGenerator)}</svg>
		`;
	}

	static styles?: CSSResultGroup = [
		css`
			svg {
				background: var(--bg-color);

				padding: 4px;

				border-radius: 50%;

			}

			polyline {
				fill: none;

				stroke: red;
				stroke-width: 2px;


			}
		`
	];

}