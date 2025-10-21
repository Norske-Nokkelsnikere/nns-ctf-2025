import { css, html, LitElement, type CSSResultGroup, type HTMLTemplateResult } from "lit";
import { customElement, state } from "lit/decorators.js";
import type { Notification, UserData } from "../lib/types";
import { notificationsContext } from "../lib/context";
import { consume } from "@lit/context";
import "./user_profile";
import { map } from "lit/directives/map.js";


@customElement("enmy-chat-sidebar")
export class EnemyChatSidebarElement extends LitElement {
	// State
	@consume({context: notificationsContext, subscribe: true})
	@state()
	private notifications: Notification[];

	// Attrs
	private users: UserData[];

	public constructor() {
		super();
		this.notifications = [];
		this.users = [];
	}

	private parseNotifications() {
		this.users = [];
		for (const notification of this.notifications) {
			if (notification.type === "user_create") {
				this.users.push(notification.data);
			}
		}
	}
	
	private renderUserFragment(user: UserData): HTMLTemplateResult {
		return html`
			<enmy-user-profile href=${`/user/${user.user_id}`} .username=${user.username} .userId=${user.user_id}></enmy-user-profile>
		`;
	}
	

	protected render(): HTMLTemplateResult {
		this.parseNotifications();

		return html`
			<div class="users">
				${map(this.users, user => this.renderUserFragment(user))}
			</div>
		`;
	}

	static styles?: CSSResultGroup = [
		css`
			:host {
				display: flex;
				flex-direction: column;

				overflow-y: scroll;
				height: 100%;

				background: var(--bg-light);

			}
			.users {
				display: flex;
				flex-direction: column;
				gap: .5rem;

				padding: .5rem;
			}
		`
	];
}
