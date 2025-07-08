// Sistema de calificaciones con estrellas
document.addEventListener('DOMContentLoaded', function() {
    // Función para mostrar estrellas basado en el atributo data-rating
    function initializeStarDisplays() {
        const starContainers = document.querySelectorAll('.star-display');
        
        starContainers.forEach(container => {
            const rating = parseFloat(container.getAttribute('data-rating') || 0);
            const maxStars = 5;
            const fullStars = Math.floor(rating);
            const hasHalfStar = rating % 1 !== 0;
            
            let starsHTML = '';
            
            // Estrellas llenas
            for (let i = 0; i < fullStars; i++) {
                starsHTML += '<span class="star filled">★</span>';
            }
            
            // Estrella media (si aplica)
            if (hasHalfStar) {
                starsHTML += '<span class="star half-filled">★</span>';
            }
            
            // Estrellas vacías
            const emptyStars = maxStars - fullStars - (hasHalfStar ? 1 : 0);
            for (let i = 0; i < emptyStars; i++) {
                starsHTML += '<span class="star">★</span>';
            }
            
            // Agregar el número de calificación si se especifica
            if (container.hasAttribute('data-show-number')) {
                starsHTML += `<span class="rating-text">(${rating.toFixed(1)}/5)</span>`;
            }
            
            container.innerHTML = starsHTML;
        });
    }
    
    // Inicializar displays de estrellas
    initializeStarDisplays();
    
    // Manejar formularios de calificación interactivos
    function initializeRatingForms() {
        const ratingContainers = document.querySelectorAll('.rating-input');
        
        ratingContainers.forEach(container => {
            const inputs = container.querySelectorAll('input[type="radio"]');
            const labels = container.querySelectorAll('label');
            
            // Función para iluminar estrellas hasta un valor específico
            function highlightStars(value) {
                labels.forEach((label, index) => {
                    const input = inputs[index];
                    if (input && parseInt(input.value) <= value) {
                        label.style.color = '#ffc107';
                    } else {
                        label.style.color = '#ddd';
                    }
                });
            }
            
            // Función para resetear todas las estrellas
            function resetStars() {
                labels.forEach(label => {
                    label.style.color = '#ddd';
                });
            }
            
            // Función para mostrar el estado actual
            function showCurrentState() {
                const checkedInput = container.querySelector('input[type="radio"]:checked');
                if (checkedInput) {
                    highlightStars(parseInt(checkedInput.value));
                } else {
                    resetStars();
                }
            }
            
            // Eventos de hover
            labels.forEach((label, index) => {
                const correspondingInput = inputs[index];
                if (correspondingInput) {
                    const value = parseInt(correspondingInput.value);
                    
                    label.addEventListener('mouseenter', function() {
                        highlightStars(value);
                    });
                    
                    label.addEventListener('mouseleave', function() {
                        showCurrentState();
                    });
                    
                    label.addEventListener('click', function() {
                        correspondingInput.checked = true;
                        highlightStars(value);
                    });
                }
            });
            
            // Eventos de cambio en los inputs
            inputs.forEach(input => {
                input.addEventListener('change', function() {
                    if (this.checked) {
                        highlightStars(parseInt(this.value));
                    }
                });
            });
            
            // Mostrar estado inicial
            showCurrentState();
        });
    }
    
    // Inicializar formularios de rating
    initializeRatingForms();
    
    // Función pública para actualizar estrellas dinámicamente
    window.updateStarRating = function(containerId, rating) {
        const container = document.getElementById(containerId);
        if (container) {
            container.setAttribute('data-rating', rating);
            initializeStarDisplays();
        }
    };
    
    // Función para mostrar mensajes dinámicos según la calificación
    function addRatingMessages() {
        const ratingContainers = document.querySelectorAll('.rating-input');
        
        ratingContainers.forEach(container => {
            // Crear un elemento para mostrar el mensaje
            const messageElement = document.createElement('div');
            messageElement.className = 'rating-message';
            messageElement.style.cssText = `
                margin-top: 8px;
                font-size: 0.9em;
                font-weight: 500;
                min-height: 20px;
                transition: all 0.3s ease;
            `;
            
            // Insertar después del contenedor de estrellas
            container.parentNode.insertBefore(messageElement, container.nextSibling);
            
            const inputs = container.querySelectorAll('input[type="radio"]');
            const labels = container.querySelectorAll('label');
            
            const messages = {
                1: '😞 Muy malo - Lo sentimos mucho',
                2: '😐 Malo - Necesitamos mejorar',
                3: '🙂 Regular - Aceptable',
                4: '😊 Bueno - ¡Bien hecho!',
                5: '🌟 Excelente - ¡Perfecto!'
            };
            
            // Función para mostrar mensaje
            function showMessage(value) {
                const message = messages[value] || '';
                messageElement.textContent = message;
                messageElement.style.color = value <= 2 ? '#dc3545' : value <= 3 ? '#ffc107' : '#28a745';
                
                // Agregar clase visual al contenedor
                if (value) {
                    container.classList.add('selected');
                } else {
                    container.classList.remove('selected');
                }
            }
            
            // Eventos de hover para mostrar mensaje temporal
            labels.forEach((label, index) => {
                const correspondingInput = inputs[index];
                if (correspondingInput) {
                    const value = parseInt(correspondingInput.value);
                    
                    label.addEventListener('mouseenter', function() {
                        showMessage(value);
                    });
                    
                    label.addEventListener('mouseleave', function() {
                        const checkedInput = container.querySelector('input[type="radio"]:checked');
                        if (checkedInput) {
                            showMessage(parseInt(checkedInput.value));
                        } else {
                            showMessage(0);
                        }
                    });
                }
            });
            
            // Eventos de selección
            inputs.forEach(input => {
                input.addEventListener('change', function() {
                    if (this.checked) {
                        showMessage(parseInt(this.value));
                    }
                });
            });
        });
    }
    
    // Agregar después de inicializar formularios
    addRatingMessages();
});
