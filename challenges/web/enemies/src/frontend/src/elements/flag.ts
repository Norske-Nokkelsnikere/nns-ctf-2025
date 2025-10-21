import { customElement } from "lit/decorators.js";
import { LitElement, type HTMLTemplateResult, html } from "lit";
import { Task } from "@lit/task";

@customElement("enmy-flag")
export class FlagElement extends LitElement {
    private getFlagTask: Task<[], string>;
    public constructor() {
        super();
        this.getFlagTask = new Task(this, {
            task: async (_args, options) => {
                const responsePromise = new Promise<string>(resolve => window.addEventListener("message", (event) => {
                    const message = event.data;
                    if (message.type === "flag") {
                        resolve(message.data);
                    }
                }, {signal: options.signal, once: true}));
                window.parent.postMessage({type: "flag"});
                return await responsePromise;
            },
            args: () => []
        })
    }
    protected render(): HTMLTemplateResult {
        return this.getFlagTask.render({
            initial: () => html`<p>🚩 Flag is loading</p>`,
            pending: () => html`<p>🚩 Flag is loading</p>`,
            error: () => html`<p>🚩 Failed to get flag</p>`,
            complete: (flag) => {
                if (flag === null) {
                    return html`<p>🚩 No flag in localStorage</p>`
                }
                return html`<p>🚩 ${flag}</p>`
            }
        })
    }
}