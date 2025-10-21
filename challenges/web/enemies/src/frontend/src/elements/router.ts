import { LitElement, html, type HTMLTemplateResult } from "lit";
import { customElement, state } from "lit/decorators.js";
import { Router } from "@lit-labs/router";
import "./pages/auth";
import "./pages/chat";
import "./chat_sidebar";
import type { Notification } from "../lib/types";
import { provide } from "@lit/context";
import { notificationsContext } from "../lib/context";
import { Task } from "@lit/task";
import { getFeed } from "../lib/api";
import "urlpattern-polyfill";

@customElement("enmy-router")
export class EnemyRouterElement extends LitElement {
	private router: Router;

	@provide({context: notificationsContext})
	@state()
	private notifications: Notification[];
	@state()
	private signedIn: boolean;

	private updateFeedTask: Task<[], void>;

	public constructor() {
		super();
		this.notifications = [];
		this.signedIn = localStorage.getItem("enmy-token") !== null;

		this.router = new Router(this, [
			{path: "/", render: () => html`<enmy-chat-page></enmy-chat-page>`},
			{path: "/user/:id", render: ({id}) => html`<enmy-chat-page .userId=${parseInt(id!)}></enmy-chat-page>`},
		]);
		this.updateFeedTask = new Task(this, {
			task: () => this.updateFeed(),
			args: () => [],
			autoRun: this.signedIn
		});
	}

	protected render(): HTMLTemplateResult {
		if (!this.signedIn) {
			return html`
				<enmy-auth-page .onAuth=${() => {
					this.signedIn = true;
					this.updateFeedTask.run([])
				}}></enmy-auth-page>
			`;
		}
		return this.updateFeedTask.render({
			initial: () => this.renderAppFragment(),
			pending: () => this.renderAppFragment(),
			complete: () => html`<h1>Oh no :(</h1><p>Enemies doesn't like you today so it will not work. Please hestiate to contact support</p>`,
			error: (error) => html`<h1>Oh no :(</h1><p>Something broke and it is your fault: ${error}. Please hestitate to contact support</p>`,
		});
	}
	private renderAppFragment(): HTMLTemplateResult {
		return html`
			${this.router.outlet()}
		`;
	}

	private async updateFeed(): Promise<void> {
		let lastNotificationId: number | null = null;
		while (true) {
			const feed = await getFeed(lastNotificationId);
			this.notifications = this.notifications.concat(feed.notifications);

			const lastNotification = this.notifications[this.notifications.length - 1];
			if (lastNotification !== undefined) {
				lastNotificationId = lastNotification.id;
			}
			await new Promise((resolve) => setTimeout(resolve, feed.next_fetch_after_seconds * 1000));
		}
	}
}
