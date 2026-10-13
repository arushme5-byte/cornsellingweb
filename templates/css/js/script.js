```javascript
document.addEventListener("DOMContentLoaded", function () {
    // Mobile menu toggle
    const menuToggle = document.querySelector("#menu-toggle");
    const navMenu = document.querySelector("#nav-menu");

    if (menuToggle && navMenu) {
        menuToggle.addEventListener("click", function () {
            const isOpen = navMenu.classList.toggle("active");
            menuToggle.setAttribute("aria-expanded", String(isOpen));
        });
    }

    // Close mobile menu when a navigation link is clicked
    document.querySelectorAll("#nav-menu a").forEach(function (link) {
        link.addEventListener("click", function () {
            if (navMenu) {
                navMenu.classList.remove("active");
            }

            if (menuToggle) {
                menuToggle.setAttribute("aria-expanded", "false");
            }
        });
    });

    // Smooth scrolling for internal page links
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener("click", function (event) {
            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);

            if (target) {
                event.preventDefault();
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });

    // Prevent accidental double submission of forms
    document.querySelectorAll("form").forEach(function (form) {
        form.addEventListener("submit", function () {
            if (!form.checkValidity()) return;

            const submitButton = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (submitButton) {
                submitButton.disabled = true;

                if (submitButton.tagName === "BUTTON") {
                    submitButton.dataset.originalText =
                        submitButton.textContent;
                    submitButton.textContent = "Please wait...";
                }
            }
        });
    });

    // Automatically dismiss temporary alerts
    document.querySelectorAll("[data-auto-dismiss]").forEach(function (alert) {
        const delay = Number(alert.dataset.autoDismiss) || 5000;

        window.setTimeout(function () {
            alert.remove();
        }, delay);
    });

    // Update current year wherever this element is used
    document.querySelectorAll("[data-current-year]").forEach(function (element) {
        element.textContent = new Date().getFullYear();
    });

    // Copy UPI ID when the copy button is clicked
    document.querySelectorAll("[data-copy-text]").forEach(function (button) {
        button.addEventListener("click", async function () {
            const textToCopy = button.dataset.copyText;
            if (!textToCopy) return;

            try {
                await navigator.clipboard.writeText(textToCopy);

                const originalText = button.textContent;
                button.textContent = "Copied!";

                window.setTimeout(function () {
                    button.textContent = originalText;
                }, 2000);
            } catch (error) {
                window.prompt("Copy this text:", textToCopy);
            }
        });
    });
});
```
