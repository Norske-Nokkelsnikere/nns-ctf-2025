import { customElement } from "lit/decorators.js";
import { LitElement, type HTMLTemplateResult, html } from "lit";
import { unsafeHTML } from "lit/directives/unsafe-html.js";
import { Task } from "@lit/task";
import type { MessageNotification } from "../../lib/types";

@customElement("enmy-message-page")
export class MessagePageElement extends LitElement {
    private getContentTask: Task<[], MessageNotification>;

    public constructor() {
        super();

        this.getContentTask = new Task(this, {
            task: async (_args, options) => {
                const responsePromise = new Promise<MessageNotification>(resolve => window.addEventListener("message", (event) => {
                    const message = event.data;
                    if (message.type === "notification") {
                        resolve(message.data);
                    }
                }, {signal: options.signal, once: true}));
                window.parent.postMessage({type: "ready", data: {notificationId: parseInt(location.hash.slice(1))}}, "*");
                return await responsePromise;
            },
            args: () => []
        });
    }

    protected render(): HTMLTemplateResult {
        return this.getContentTask.render({
            initial: () => html`<p>Loading content</p>`,
            pending: () => html`<p>Loading content</p>`,
            error: () => html`<p>Failed to get content</p>`,
            complete: (data) => html`${unsafeHTML(data.data.content)}`
        });
    }
	protected createRenderRoot(): HTMLElement | DocumentFragment {
	    return this;
	}
}
