/* ---------------- INPUT WIZARD ---------------- */
const cards = document.querySelectorAll(".card");
let currentCard = 0;

function showCard(index) {
    cards.forEach(c => c.classList.remove("active"));
    cards[index].classList.add("active");
}

document.querySelectorAll(".next").forEach(btn => {
    btn.addEventListener("click", () => {
        if (currentCard < cards.length - 1) {
            currentCard++;
            showCard(currentCard);
        }
    });
});

document.querySelectorAll(".back").forEach(btn => {
    btn.addEventListener("click", () => {
        if (currentCard > 0) {
            currentCard--;
            showCard(currentCard);
        }
    });
});

/* ---------------- OPTION SELECTION ---------------- */
document.querySelectorAll(".options button").forEach(btn => {
    btn.addEventListener("click", () => {
        const name = btn.dataset.name;
        const value = btn.value;

        if (btn.parentElement.classList.contains("multi")) {
            btn.classList.toggle("selected");

            if (btn.classList.contains("selected")) {
                const hidden = document.createElement("input");
                hidden.type = "hidden";
                hidden.name = name;
                hidden.value = value;
                hidden.dataset.value = value;
                wizardForm.appendChild(hidden);
            } else {
                document
                    .querySelectorAll(`input[name="${name}"][data-value="${value}"]`)
                    .forEach(el => el.remove());
            }
        } else {
            document.querySelector(`input[name="${name}"]`).value = value;
            btn.parentElement
                .querySelectorAll("button")
                .forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");
        }
    });
});

/* ---------------- MOVIE FLOW ---------------- */
const movieFlow = document.getElementById("movieFlow");
const inputFlow = document.getElementById("inputFlow");
const movies = document.querySelectorAll(".movie-card");

if (movies.length > 0) {
    inputFlow.style.display = "none";
    movieFlow.style.display = "block";

    let movieIndex = 0;
    movies[movieIndex].classList.add("active");

    document.getElementById("nextBtn").addEventListener("click", () => {
        if (movieIndex < movies.length - 1) {
            movies[movieIndex].classList.remove("active");
            movieIndex++;
            movies[movieIndex].classList.add("active");
        }
    });

    document.getElementById("prevBtn").addEventListener("click", () => {
        if (movieIndex > 0) {
            movies[movieIndex].classList.remove("active");
            movieIndex--;
            movies[movieIndex].classList.add("active");
        }
    });
}
