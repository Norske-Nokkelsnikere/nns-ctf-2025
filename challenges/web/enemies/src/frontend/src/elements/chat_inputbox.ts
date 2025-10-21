import { css, html, LitElement, type CSSResultGroup, type HTMLTemplateResult } from "lit";
import { customElement, property } from "lit/decorators.js";
import { createRef, type Ref, ref } from "lit/directives/ref.js";
import Quill from "quill"
import { sendMessage } from "../lib/api";

@customElement("enmy-chat-input")
export class EnemyChatInputElement extends LitElement {
	@property({type: Number})
	public userId?: number;

	private editor: Quill | null;
	private editorElementRef: Ref<HTMLDivElement>;

	public constructor() {
		super();
		this.editor = null;
		this.editorElementRef = createRef();
	}

	public firstUpdated(): void {
		// Attach Quill
		const selector = this.editorElementRef.value;
		const options = {
  			placeholder: "You have to press space before typing your next character or your cursor will break. Don't question why, you have no choice but to use our products.",
  			theme: "snow"
		};
		if (selector !== undefined) {
			this.editor = new Quill(selector, options);
		}
	}

	protected render(): HTMLTemplateResult {
		return html`
			<link rel="stylesheet" href="https://cdn.quilljs.com/1.3.6/quill.snow.css">
			
			<button type="button" class="send" @click=${this.handleSendClicked}>send</button>
			<div ${ref(this.editorElementRef)} id="editor"></div>
			
		`;
	}
	private async handleSendClicked(): Promise<void> {
		const value = this.editor!.getSemanticHTML();
		await sendMessage(this.userId!, value);
		this.editor!.setText("");
	}

	static styles?: CSSResultGroup = [
		css`
			:host {
				position: relative;
				max-height: 100%;

				display: grid;
				grid-template-rows: auto 10.5em;
			}

			button.send {
				position: absolute;
				left: auto;
				right: 2em;
				bottom: 3em;
				z-index: 5;

				width: 5em;
				height: 5em;
				
				clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
				
				font-size: 1.2em;

				border: none;

				color: white;
				background: var(--accent);

				cursor: pointer;
			}

			#editor {
				

				background: var(--bg-color);
				color: white;

				border: none;
			}
			.ql-toolbar.ql-snow {
				background: #d40000;
				color: white;
				
				border: none;
			}
			.ql-picker-label {
				color: white;
			}
			.ql-snow .ql-stroke {
				
				
				stroke: white;

				border: none;
			}
			.ql-editor {
				overflow-y: scroll;
			}
		`
	];
}
