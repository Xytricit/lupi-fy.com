const hamburger = document.querySelector(".hamburger");
const mobileMenu = document.querySelector(".mobile-menu");
const logo = document.querySelector(".logo");

hamburger.addEventListener("click", () => {
    mobileMenu.classList.toggle("active");
});

// clicking the logo closes menu (mobile only)
logo.addEventListener("click", () => {
    if (mobileMenu.classList.contains("active")) {
        mobileMenu.classList.remove("active");
    }
});
