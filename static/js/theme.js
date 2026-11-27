
document.addEventListener("DOMContentLoaded", function () {

    const html = document.documentElement;
    const themeToggle = document.getElementById("themeToggle");
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");

    // 1. Charger le thème enregistré

    const savedTheme = localStorage.getItem("bibliotheque-theme");
    const initialTheme = savedTheme || "dark";

    html.setAttribute("data-theme", initialTheme);

    // 2. Mettre à jour l'icône du thème

    function updateThemeIcon() {

        if (!themeToggle) return;

        const icon = themeToggle.querySelector("i");

        if (html.getAttribute("data-theme") === "dark") {

            icon.className = "bi bi-sun-fill";

            themeToggle.setAttribute(
                "aria-label",
                "Activer le mode clair"
            );

        } else {

            icon.className = "bi bi-moon-fill";

            themeToggle.setAttribute(
                "aria-label",
                "Activer le mode sombre"
            );
        }
    }

    updateThemeIcon();

    // 3. Changer le thème

    if (themeToggle) {

        themeToggle.addEventListener("click", function () {

            const currentTheme = html.getAttribute("data-theme");

            const newTheme =
                currentTheme === "dark" ? "light" : "dark";

            html.setAttribute("data-theme", newTheme);

            localStorage.setItem(
                "bibliotheque-theme",
                newTheme
            );

            updateThemeIcon();
        });
    }

    // 4. Ouvrir et fermer le menu mobile

    if (menuToggle && sidebar) {

        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });

        document.addEventListener("click", function (event) {

            const clickedInsideSidebar =
                sidebar.contains(event.target);

            const clickedMenuButton =
                menuToggle.contains(event.target);

            if (!clickedInsideSidebar && !clickedMenuButton) {
                sidebar.classList.remove("open");
            }
        });
    }

});
