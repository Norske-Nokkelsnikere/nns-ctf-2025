import { type AccountCreationResponse, type GetFeedResponse } from "./types";

function getApiBase(): String {
	return "/api/";
}

export async function createAccount(username: string): Promise<AccountCreationResponse> {
	const response = await fetch(`${getApiBase()}users/@me`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			username
		})
	});
	return await response.json();
}
export async function getFeed(lastNotificationId: number | null): Promise<GetFeedResponse> {
	const queryParams = new URLSearchParams({
		token: localStorage.getItem("enmy-token") ?? "",
	});
	if (lastNotificationId) {
		queryParams.append("last_seen_notification", lastNotificationId.toString());
	};

	const response = await fetch(`${getApiBase()}feed?${queryParams}`);
	return await response.json();
}

export async function sendMessage(userId: number, content: string): Promise<void> {
	const queryParams = new URLSearchParams({
		token: localStorage.getItem("enmy-token") ?? "",
	});
	await fetch(`${getApiBase()}users/${userId}/messages?${queryParams}`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			content
		})
	});
}
