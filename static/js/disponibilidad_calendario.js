// Script para mostrar calendario de disponibilidad por experto usando flatpickr
// Requiere que el template pase una variable window.disponibilidadPorExperto = { experto_id: ["YYYY-MM-DD", ...], ... }

document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.disponibilidadPorExperto !== 'object') return;
    Object.entries(window.disponibilidadPorExperto).forEach(([expertoId, diasNoDisponibles]) => {
        const input = document.getElementById('calendario-disponibilidad-' + expertoId);
        if (!input) return;
        flatpickr(input, {
            inline: true,
            disable: diasNoDisponibles,
            dateFormat: 'Y-m-d',
            locale: 'es',
            disableMobile: true,
        });
    });
});
