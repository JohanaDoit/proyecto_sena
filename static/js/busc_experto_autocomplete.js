// JS para autocompletar sugerencias de expertos en la barra de búsqueda

document.addEventListener('DOMContentLoaded', function() {
    const input = document.querySelector('input[name="q"]');
    if (!input) return;

    // Crear contenedor de sugerencias
    let suggestionBox = document.createElement('div');
    suggestionBox.className = 'autocomplete-suggestions';
    suggestionBox.style.position = 'absolute';
    suggestionBox.style.zIndex = 1000;
    suggestionBox.style.background = '#fff';
    suggestionBox.style.border = '1px solid #ccc';
    suggestionBox.style.width = input.offsetWidth + 'px';
    suggestionBox.style.display = 'none';
    input.parentNode.appendChild(suggestionBox);

    let lastValue = '';
    let timeout = null;

    input.addEventListener('input', function() {
        const value = input.value.trim();
        if (value.length < 2) {
            suggestionBox.style.display = 'none';
            suggestionBox.innerHTML = '';
            return;
        }
        if (value === lastValue) return;
        lastValue = value;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            fetch(`/ajax/busc_experto_sugerencias/?q=${encodeURIComponent(value)}`)
                .then(res => res.json())
                .then(data => {
                    suggestionBox.innerHTML = '';
                    if (data.sugerencias && data.sugerencias.length > 0) {
                        data.sugerencias.forEach(item => {
                            let div = document.createElement('div');
                            div.className = 'autocomplete-suggestion';
                            div.textContent = item.texto;
                            div.style.padding = '6px 12px';
                            div.style.cursor = 'pointer';
                            div.addEventListener('mousedown', function(e) {
                                input.value = item.texto;
                                suggestionBox.style.display = 'none';
                                input.form && input.form.submit();
                            });
                            suggestionBox.appendChild(div);
                        });
                        suggestionBox.style.display = 'block';
                    } else {
                        suggestionBox.style.display = 'none';
                    }
                });
        }, 200);
    });

    // Ocultar sugerencias al perder foco
    input.addEventListener('blur', function() {
        setTimeout(() => suggestionBox.style.display = 'none', 150);
    });
    input.addEventListener('focus', function() {
        if (suggestionBox.innerHTML) suggestionBox.style.display = 'block';
    });
});
