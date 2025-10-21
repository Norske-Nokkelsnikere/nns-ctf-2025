import { css, html, LitElement, type CSSResultGroup, type HTMLTemplateResult } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import type { Notification, MessageNotification } from "../../lib/types";
import { consume } from "@lit/context";
import { notificationsContext } from "../../lib/context";
import "../chat_inputbox";
import { repeat } from "lit/directives/repeat.js";

@customElement("enmy-chat-page")
export class EnemyChatElement extends LitElement {
	
	@property({type: Number})
	public userId?: number;

	@consume({context: notificationsContext, subscribe: true})
	@state()
	private notifications: Notification[];

	// Attrs
	private abortController: AbortController;

	public constructor() {
		super();

		this.notifications = [];
		this.abortController = new AbortController();
	}

	protected render(): HTMLTemplateResult {
		const localUserId = parseInt(localStorage.getItem("enmy-user-id")!);
		return html`
			<enmy-chat-sidebar></enmy-chat-sidebar>
			
			</div>
			<div class="chat">
				<div class="chat-history">
					${repeat(this.notifications, notification => notification.id, notification => {
						if (notification.type !== "message") {
							return;
						}
						const isMessageToUser = notification.data.sender.user_id === localUserId && notification.data.recipient.user_id === this.userId;
						const isMessageFromUser = notification.data.sender.user_id === this.userId && notification.data.recipient.user_id === localUserId;
						if (!(isMessageToUser || isMessageFromUser)) {
							return;
						}
						if (notification.type === "message") {
							return this.renderMessageFragment(notification);
						}
					})}
				</div>
				${this.userId === undefined ? null : html`<enmy-chat-input .userId=${this.userId}></enmy-chat-input>`}
			</div>
		`;
	}
	private renderMessageFragment(notification: MessageNotification): HTMLTemplateResult {
		return html`
			<div class="message" data-notification=${JSON.stringify(notification)}>
				<div class="icon-container">
					<enmy-user-icon .userId=${notification.data.sender.user_id}></enmy-user-icon>
				</div>
				<iframe
					class="message-content"
					src=${`/message.html#${notification.id}`}
				></iframe>
			</div>
		`
	}

	public connectedCallback(): void {
		super.connectedCallback();

		if (this.abortController.signal.aborted) {
			this.abortController = new AbortController();
		}
		window.addEventListener("message", (event) => this.handleMessageEvent(event), {signal: this.abortController.signal});
	}
	public disconnectedCallback(): void {
		super.disconnectedCallback();
		this.abortController.abort();
	}

	private handleMessageEvent(event: MessageEvent): void {
		console.log({event});
		if (event.source === null) {
			return;
		}
		const data = event.data;
		if (data.type === "ready") {
			const notification = this.notifications.find(searchNotification => searchNotification.id === data.data.notificationId);
			event.source.postMessage({
				type: "notification",
				data: notification
			});
		}
		if (data.type === "flag") {
			event.source.postMessage(
				{
					type: "flag",
					data: localStorage.getItem("flag")
				},
				{
					targetOrigin: "*"
				}
			);
		}
	}

	static styles?: CSSResultGroup = [
		css`
			:host {
				height: 100%;

				display: grid;
				grid-template-rows: auto;
				grid-template-columns: 20em auto;
				
			}
			.chat {
				height: 100%;
				display: grid;
				grid-template-rows: auto auto;


			}
			.chat-history {
				height: 80vh;
				
				display: grid;
				gap: 1rem;
				grid-auto-rows: max-content;

				padding: 2em;

				overflow-y: scroll;
			}

			.message-content {
				border: none;
				background: grey;
				padding: .5rem;
			}
			.message {
				display: flex;
				gap: 1rem;
			}
			.icon-container {

				display: flex;
				flex-direction: column;
			}
		`
	];
}
