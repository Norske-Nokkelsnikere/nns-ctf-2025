import { createContext } from "@lit/context";
import type { Notification } from "./types";

export const notificationsContext = createContext<Notification[]>(Symbol("notifications"));