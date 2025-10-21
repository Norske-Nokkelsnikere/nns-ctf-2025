import { getAccount, getCards } from "./api.js";

async function updateWithData() {
    let account = await getAccount();
    let cards = await getCards();

    let containerElement = document.getElementById("cards-listing");
    for (let cardId of account.cards) {
        let card = cards.filter(card => card.id === cardId)[0];
        let cardElement = document.createElement("div");
        containerElement.appendChild(cardElement);
        cardElement.classList.add("card");

        let titleElement = document.createElement("span");
        cardElement.appendChild(titleElement);
        titleElement.classList.add("title");
        titleElement.innerText = card.id;

        let descriptionElement = document.createElement("span");
        cardElement.appendChild(descriptionElement);
        descriptionElement.classList.add("description");
        descriptionElement.innerText = card.description;
    }
    let infoElement = document.getElementById("info");
    let balanceElement = document.createElement("p");
    infoElement.appendChild(balanceElement);
    balanceElement.innerText = `Balance: ${account.balance}$`;
}
updateWithData();