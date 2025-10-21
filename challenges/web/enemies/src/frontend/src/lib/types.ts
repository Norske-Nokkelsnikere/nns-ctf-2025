export type AccountCreationResponse = {
	user_id: number,
	token: string
};

export type UserData = {
	user_id: number;
	username: string;
	admin: boolean;
}

export type UserCreateNotification = {
	type: "user_create";
	id: number;
	data: UserData;
};
export type MessageNotification = {
	type: "message";
	id: number;
	data: {
		sender: {
			user_id: number;
		};
		recipient: {
			user_id: number;
		};
		content: string;
	};
};
export type Notification = UserCreateNotification | MessageNotification;
export type GetFeedResponse = {
	next_fetch_after_seconds: number;
	notifications: Notification[]
};

export type Vector2 = {
	x: number;
	y: number;
}