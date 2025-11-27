const hamburger = document.querySelector(".hamburger");
const mobileMenu = document.querySelector(".mobile-menu");

hamburger.addEventListener("click", () => {
    mobileMenu.classList.toggle("active");
});
document.querySelector(".mobile-menu .logo").addEventListener("click", () => {
    mobileMenu.classList.remove("active");
});
