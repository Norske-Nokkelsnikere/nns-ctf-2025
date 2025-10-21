import "./board.js";
const ws = new WebSocket("/game");
window.ws = ws; // Hacky? yes. too bad :P

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log(message);
    const board = document.getElementById("board");
    if (message.type === "level") {
        let levelIndicator = document.getElementById("level-indicator");
        levelIndicator.innerText = `Level ${message.data.id}`;
        board.blocks = message.data.state;
    } else if (message.type === "cursor_position") {
        board.cursorPosition = message.data;
    }
}