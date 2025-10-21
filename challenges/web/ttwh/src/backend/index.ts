import express from "express";
import expressWs from "express-ws";
import { Game } from "./game.ts";

const APP = express();
const WS_APP = expressWs(APP);
const FLAG = process.env.FLAG || "oh noes, you ran your exploit against your local instance by mistake";
const PORT = parseInt(process.env.port || "8000");

APP.get("/", (_req, res) => {
    res.redirect("/ui");
});
APP.use("/ui", express.static("frontend/", {extensions: ["html"]}));

APP.listen(PORT, () => {
    console.info(`Listening on http://0.0.0.0:${PORT}`);
});

APP.ws("/game", (ws, request) => {
    new Game(ws);
})