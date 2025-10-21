import { buyCard, getCards, testCard } from "./api.js";
async function updateListing(params) {
    let containerElement = document.getElementById("cards-listing");
    let cards = await getCards();

    for (let card of cards) {
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

        let actionsContainer = document.createElement("div");
        cardElement.appendChild(actionsContainer);
        actionsContainer.classList.add("actions");

        let priceElement = document.createElement("span");
        actionsContainer.appendChild(priceElement);
        priceElement.classList.add("price");
        priceElement.innerText = `${card.price}$`;

        let testElement = document.createElement("button");
        actionsContainer.appendChild(testElement);
        testElement.classList.add("test");
        testElement.innerText = "Test";
        testElement.onclick = async () => {
            try {
                await testCard(card.id);
                location.href = "/ui/@me"
            } catch (error) {
                alert(error)
            }
        }

        let buyElement = document.createElement("button");
        actionsContainer.appendChild(buyElement);
        buyElement.classList.add("buy");
        buyElement.innerText = "Buy";
        buyElement.onclick = async () => {
            try {
                await buyCard(card.id);
            } catch (error) {
                alert(error)
            }
        }
    }
}

updateListing();