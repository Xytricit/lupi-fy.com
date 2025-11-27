const hamburger = document.querySelector(".hamburger");
const mobileMenu = document.querySelector(".mobile-menu");

hamburger.addEventListener("click", () => {
    mobileMenu.classList.toggle("active");
});

document.addEventListener("click", (e) => {
    if (
        mobileMenu.classList.contains("active") &&
        !mobileMenu.contains(e.target) &&
        !hamburger.contains(e.target)
    ) {
        mobileMenu.classList.remove("active");
    }
});
