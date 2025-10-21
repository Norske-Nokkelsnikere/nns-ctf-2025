import { customElement, property } from "lit/decorators.js";
import { LitElement, type HTMLTemplateResult, html, type CSSResultGroup, css } from "lit";
import "./user_icon";

@customElement("enmy-user-profile")
export class UserProfileElement extends LitElement {
    
	@property({type: String})
	public href: string;
    @property({type: String})
    public username: string;
    @property({type: Number})
    public userId?: number;

	public constructor() {
        super();
		this.href = "";
        this.username = "";
    }

    protected render(): HTMLTemplateResult {
        return html`
			
			<a href=${this.href} class="bar">
				<div class="hover-fx"></div>
				<span class="avatar"><enmy-user-icon .userId=${this.userId}></enmy-user-icon></span>
            	<span class="username">${this.username}</span>
				
			</a>
            
        `;
    }
    static styles?: CSSResultGroup = css`

		.bar {
			position: relative;
			display: flex;
            gap: 2rem;
			
			padding: 1em;
            
            background: #424242;
			clip-path: inset(0 0);
		}
		.hover-fx {
			transition: left .2s ease-in-out;

			position: absolute;
			top: 0;
			left: 100%;


			width: 100%;
			height: 100%;

			background: var(--accent);

			clip-path: polygon(20% 0%, 100% 0%, 100% 100%, 0% 100%);
		}

		.bar:hover > .hover-fx {
			transition: .2s ease-in-out;
			left: 70%;
		}
		.bar:focus > .hover-fx {
			transition: left .2s ease-in-out;
			left: 70%;
		}

		span {
			position: relative;
			z-index: 3;

			align-content: center;

			color: white;
			font-size: 1.5em;
			font-weight: 450;
			text-overflow: ellipsis;
		}
		a {
			text-decoration: none;
			color: inherit;
		}

    `;
}