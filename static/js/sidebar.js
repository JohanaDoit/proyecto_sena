// static/js/sidebar.js

document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const body = document.body; // Referencia al body para añadir/quitar clase

    // Función para manejar el despliegue/plegado del sidebar
    function toggleSidebar() {
        sidebar.classList.toggle('active');
        content.classList.toggle('shifted');
        body.classList.toggle('sidebar-active'); // Añade/quita clase al body
    }

    // Event listener para el botón de toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Opcional: Cerrar el sidebar al hacer clic fuera de él (para móviles)
    // Puedes añadir una capa de superposición para esto
    /*
    content.addEventListener('click', function() {
        if (sidebar.classList.contains('active') && window.innerWidth <= 768) {
            toggleSidebar();
        }
    });
    */
});

// static/js/sidebar.js
console.log("sidebar.js cargado correctamente!"); // Añade esta línea al principio

document.addEventListener('DOMContentLoaded', function() {
    // ... resto de tu código
});