// Mostrar expertos por especialidad seleccionada en principal.html

document.addEventListener('DOMContentLoaded', function() {
    const servicioSelect = document.getElementById('servicio');
    const expertosContainer = document.createElement('div');
    expertosContainer.id = 'expertos-por-especialidad';
    expertosContainer.style.marginTop = '20px';
    if (servicioSelect && servicioSelect.parentNode) {
        servicioSelect.parentNode.appendChild(expertosContainer);
    }

    if (!servicioSelect) return;

    servicioSelect.addEventListener('change', function() {
        const servicioId = servicioSelect.value;
        expertosContainer.innerHTML = '';
        if (!servicioId) return;
        fetch(`/ajax/expertos_por_especialidad/?servicio_id=${encodeURIComponent(servicioId)}`)
            .then(res => res.json())
            .then(data => {
                if (data.expertos && data.expertos.length > 0) {
                    expertosContainer.innerHTML = '<h4>Expertos disponibles:</h4>';
                    data.expertos.forEach(exp => {
                        const div = document.createElement('div');
                        div.className = 'experto-card';
                        div.style.display = 'flex';
                        div.style.alignItems = 'center';
                        div.style.gap = '12px';
                        div.style.marginBottom = '10px';
                        div.innerHTML = `
                            <img src="${exp.foto || '/static/images/default_profile.png'}" alt="Foto de ${exp.nombre}" style="width:50px;height:50px;border-radius:50%;object-fit:cover;">
                            <div>
                                <strong>${exp.nombre}</strong><br>
                                <span style="font-size:0.95em;color:#555;">${exp.especialidades}</span><br>
                                <span style="font-size:0.9em;color:#888;">@${exp.username}</span>
                            </div>
                            <a href="/reserva/?servicio_id=${servicioId}&experto_id=${exp.id}" class="btn btn-sm btn-success" style="margin-left:auto;">Reservar</a>
                        `;
                        expertosContainer.appendChild(div);
                    });
                } else {
                    expertosContainer.innerHTML = '<div class="alert alert-warning">No hay expertos disponibles para este servicio.</div>';
                }
            });
    });
});
