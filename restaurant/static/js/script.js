// -------------------------
// 🌊 Smooth Scroll for Navigation
// -------------------------
document.querySelectorAll("nav a").forEach(link => {
    link.addEventListener("click", function (e) {
        if (this.hash !== "") {
            e.preventDefault();
            const target = document.querySelector(this.hash);
            if (target) {
                target.scrollIntoView({ behavior: "smooth" });
            }
        }
    });
});

// -------------------------
// ⬆ Back to Top Button
// -------------------------
const backToTop = document.createElement("button");
backToTop.innerText = "⬆ Top";
backToTop.id = "backToTop";
document.body.appendChild(backToTop);

backToTop.style.position = "fixed";
backToTop.style.bottom = "20px";
backToTop.style.right = "20px";
backToTop.style.padding = "10px 15px";
backToTop.style.background = "#0077b6";
backToTop.style.color = "white";
backToTop.style.border = "none";
backToTop.style.borderRadius = "8px";
backToTop.style.cursor = "pointer";
backToTop.style.display = "none";
backToTop.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";

window.addEventListener("scroll", () => {
    backToTop.style.display = window.scrollY > 300 ? "block" : "none";
});

backToTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});

// -------------------------
// 🐟 Specials Menu Filter
// -------------------------
function filterMenu(category) {
    document.querySelectorAll(".menu-card").forEach(card => {
        if (category === "all" || card.dataset.category === category) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// -------------------------
// 🛒 Add to Cart Functionality (AJAX)
// -------------------------
document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = getCookie("csrftoken");

    document.querySelectorAll(".add-to-cart-btn").forEach((button) => {
        button.addEventListener("click", function () {
            const itemId = this.dataset.itemId;

            fetch("/add-to-cart/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({ item_id: itemId }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.quantity) {
                        const countSpan = document.getElementById(`count-${itemId}`);
                        if (countSpan) countSpan.textContent = data.quantity;
                    }
                    alert(data.message || "Added to cart!");
                })
                .catch((error) => console.error("Error adding to cart:", error));
        });
    });
});

// CSRF helper function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
