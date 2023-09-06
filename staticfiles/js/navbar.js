document.addEventListener("DOMContentLoaded", function () {
    const toggleNavbar = (toggleId, navId, bodyId, headerId) => {
        const toggle = document.getElementById(toggleId);
        const nav = document.getElementById(navId);
        const bodypd = document.getElementById(bodyId);
        const headerpd = document.getElementById(headerId);

        // Check if all elements exist
        if (toggle && nav && bodypd && headerpd) {
            toggle.addEventListener('click', () => {
                // Toggle navbar visibility
                nav.classList.toggle('show');
                // Toggle icon
                toggle.classList.toggle('bi-bi');
                // Toggle padding for body and header
                bodypd.classList.toggle('body-pd');
                headerpd.classList.toggle('body-pd');
            });
        }
    };

    toggleNavbar('header-toggle', 'nav-bar', 'body-pd', 'header');

    // Activate links
    const navLinks = document.querySelectorAll('.nav_link');

    function activateLink() {
        // Remove the "active" class from all links
        navLinks.forEach(link => link.classList.remove('active'));
        // Add the "active" class to the clicked link
        this.classList.add('active');
    }

    navLinks.forEach(link => link.addEventListener('click', activateLink));
});
