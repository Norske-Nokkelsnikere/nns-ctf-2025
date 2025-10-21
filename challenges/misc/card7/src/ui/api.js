export async function getCards() {
    let response = await fetch("/cards");
    return await response.json();
}
export async function getAccountToken() {
    let existingToken = localStorage.getItem("api.token");
    if (existingToken !== null) {
        return existingToken;
    }
    let response = await fetch("/accounts/@me", {method: "POST"});
    let data = await response.json();
    localStorage.setItem("api.token", data.token);
    return await getAccountToken();
    
}
export async function getAccount() {
    let token = await getAccountToken();
    let response = await fetch("/accounts/@me", {
        headers: {
            token
        }
    });
    return await response.json()
}
export async function testCard(cardId) {
    let token = await getAccountToken();
    let response = await fetch(`/cards/${cardId}/test`, {
        method: "POST",
        headers: {
            token
        },
    });
    if (!response.ok) {
        throw await response.text();
    }
}
export async function buyCard(cardId) {
    let token = await getAccountToken();
    let response = await fetch(`/cards/${cardId}/buy`, {
        method: "POST",
        headers: {
            token
        },
    });
    if (!response.ok) {
        throw await response.text();
    }
}