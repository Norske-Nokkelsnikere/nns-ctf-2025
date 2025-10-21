import { customElement, property } from "lit/decorators.js";
import { LitElement, css, html, type CSSResultGroup, type HTMLTemplateResult } from "lit";
import { type Ref, ref, createRef } from "lit/directives/ref.js";
import { createAccount } from "../../lib/api";

@customElement("enmy-auth-page")
export class EmemyAuthPage extends LitElement {
	// Props
	@property({attribute: false})
	private onAuth?: () => void

	// Elements
	private usernameInputRef: Ref<HTMLInputElement>;
	private tokenInputRef: Ref<HTMLInputElement>;

	constructor() {
		super();
		this.usernameInputRef = createRef();
		this.tokenInputRef = createRef();
	}

	protected render(): HTMLTemplateResult {
		return html`
			<h1 class="header">ENEMIES</h1>
			<div class="page">
				<form @submit=${this.handleCreateUser}>
					<label for="username-input">Username</label>
					<input ${ref(this.usernameInputRef)} id="username-input" type="text" placeholder="username" required/>
					<button id="user-submit" type="submit">Sign up</button>
				</form>
				<form @submit=${this.handleLogin}>
					<label for="authtoken-input">Auth token</label>
					<input ${ref(this.tokenInputRef)} id="authtoken-input" type="text" placeholder="auth token" required/>
					<button id="auth-submit" type="submit">Sign in</button>
				</form>
			</div>
		`;
	}
	private async handleCreateUser(event: SubmitEvent): Promise<void> {
		// Cancel default browser nav
		event.preventDefault();

		const usernameInput = this.usernameInputRef.value!;
		const response = await createAccount(usernameInput.value);
		localStorage.setItem("enmy-token", response.token);
		localStorage.setItem("enmy-user-id", response.user_id.toString());
		if (this.onAuth) {
			this.onAuth();
		}
	}
	private async handleLogin(event: SubmitEvent): Promise<void> {
		// Cancel default browser nav
		event.preventDefault();

		const tokenInputElement = this.tokenInputRef.value!;
		const token = tokenInputElement.value;

		const rawDataFragment = token.split(".")[0];
		const dataFragment = JSON.parse(atob(rawDataFragment));

		localStorage.setItem("enmy-token", token);
		localStorage.setItem("enmy-user-id", dataFragment.user_id);
		if (this.onAuth) {
			this.onAuth();
		}
	}
	


	static styles?: CSSResultGroup = [
		css`
			:host {
				display: flex;
				flex-direction: column;
				align-items: center;
				justify-content: center;
				gap: 10em;

				width: 100%;
				height: 100%;
			}
			.header {
				color: var(--accent);
			}

			.page {
				display: flex;
				flex-direction: column;
				gap: 3rem;

				width: 80%;
			}

			form {
				display: flex;
				flex-direction: column;
				align-items: center;
				gap: .5rem
			}

			input {
				flex: 1;

				font-size: 1.2em;

				border: solid black 2px;

			}

			button {
				flex: 1;

				font-size: 1.2rem;

				padding: 1rem 2rem 1rem 2rem;

				border: 2px solid var(--accent);


				background: var(--accent);
				color: white;

				cursor: pointer;
			}
			button:hover {
				background: white;
				color: var(--accent);

			}
			button:focus {
				background: white;
				color: var(--accent);
	
			}

		`
	];

}
