zdocument.addEventListener("DOMContentLoaded", function () {
    // ---- Dark mode toggle ----
    const root = document.documentElement;
    const toggleBtn = document.getElementById("darkModeToggle");
    const savedTheme = localStorage.getItem("psms-theme") || "light";
    root.setAttribute("data-bs-theme", savedTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            const current = root.getAttribute("data-bs-theme");
            const next = current === "dark" ? "light" : "dark";
            root.setAttribute("data-bs-theme", next);
            localStorage.setItem("psms-theme", next);
        });
    }

    // ---- Mobile sidebar toggle ----
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("show");
        });
    }

    // ---- Bootstrap client-side validation hint ----
    const forms = document.querySelectorAll("form#statementForm");
    forms.forEach((form) => {
        form.addEventListener("submit", function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = "Saving...";
            }
        });
    });
});
