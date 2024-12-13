document.addEventListener("DOMContentLoaded", () => {
    const navLinks = document.querySelectorAll(".nav ul li a");
    navLinks.forEach((link) => {
        link.addEventListener("mouseover", () => {
            link.style.animation = "hover-bounce 0.5s ease";
        });
        link.addEventListener("animationend", () => {
            link.style.animation = "";
        });
    });

    // Плавное появление элементов при прокрутке
    const elements = document.querySelectorAll(".hero, .cta-button");
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.animation = "fade-in 1s ease";
            }
        });
    });
    elements.forEach((el) => observer.observe(el));
});

// Bounce эффект при наведении
@keyframes hover-bounce {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-8px);
    }
}
