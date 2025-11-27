const hamburger = document.querySelector(".hamburger");
const mobileMenu = document.querySelector(".mobile-menu");

// Toggle menu when hamburger is clicked
hamburger.addEventListener("click", () => {
    mobileMenu.classList.toggle("active");
});

// Close menu when clicking outside (not logo!)
document.addEventListener("click", (e) => {
    if (
        mobileMenu.classList.contains("active") &&
        !mobileMenu.contains(e.target) &&
        !hamburger.contains(e.target)
    ) {
        mobileMenu.classList.remove("active");
    }
});
