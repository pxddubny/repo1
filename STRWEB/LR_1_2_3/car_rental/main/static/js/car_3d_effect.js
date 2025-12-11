console.log("Car 3D Effect JS Loaded v2.0");

class Car3DEffect {
    constructor() {
        this.cards = [];
        this.isMobile = window.innerWidth <= 768;
        this.init();
    }
    
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupCards());
        } else {
            this.setupCards();
        }
        
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth <= 768;
            if (this.isMobile) {
                this.disable3DEffects();
            }
        });
    }
    
    setupCards() {
        const carCards = document.querySelectorAll('.car-card');
        
        carCards.forEach((card, index) => {
            // Проверяем, не обернута ли уже карточка
            if (card.parentNode.classList.contains('car-card-wrapper')) {
                console.log('Card already wrapped, skipping', index);
                return;
            }
            
            // Сохраняем оригинальный HTML и обработчики событий
            const originalContent = card.cloneNode(true);
            
            // Создаем обертку
            const wrapper = document.createElement('div');
            wrapper.className = 'car-card-wrapper';
            wrapper.style.position = 'relative';
            
            // Обертываем карточку
            card.parentNode.insertBefore(wrapper, card);
            
            // Вместо перемещения карточки, создаем новую структуру
            wrapper.innerHTML = `
                <div class="car-card-3d">
                    <div class="car-content">
                        ${card.innerHTML}
                    </div>
                </div>
            `;
            
            // Удаляем оригинальную карточку
            card.remove();
            
            // Получаем ссылку на новую карточку
            const newCard = wrapper.querySelector('.car-card-3d');
            
            // Восстанавливаем обработчики событий на ссылках
            this.restoreLinkHandlers(wrapper, originalContent);
            
            // Добавляем 3D эффект, если не мобильное устройство
            if (!this.isMobile) {
                this.addCardListeners(wrapper, newCard);
                this.cards.push({ wrapper, card: newCard });
            }
        });
        
        console.log(`Initialized ${carCards.length} car cards with 3D effect`);
    }
    
    restoreLinkHandlers(wrapper, originalCard) {
        // Находим все ссылки в оригинальной карточке
        const originalLinks = originalCard.querySelectorAll('a');
        const newLinks = wrapper.querySelectorAll('a');
        
        // Копируем обработчики событий и атрибуты
        originalLinks.forEach((originalLink, index) => {
            if (newLinks[index]) {
                // Копируем все атрибуты
                Array.from(originalLink.attributes).forEach(attr => {
                    newLinks[index].setAttribute(attr.name, attr.value);
                });
                
                // Копируем обработчики событий
                const events = this.getEventListeners(originalLink);
                events.forEach(event => {
                    newLinks[index].addEventListener(event.type, event.listener);
                });
                
                // Убедимся, что ссылка кликабельна
                newLinks[index].style.pointerEvents = 'auto';
                newLinks[index].style.position = 'relative';
                newLinks[index].style.zIndex = '10';
            }
        });
    }
    
    getEventListeners(element) {
        return [];
    }
    
    addCardListeners(wrapper, card) {
        let animationFrameId = null;
        let isAnimating = false;
        
        // Исключаем область ссылки из обработки 3D эффекта
        const links = wrapper.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('mouseenter', () => {
                wrapper.classList.add('no-effect');
            });
            
            link.addEventListener('mouseleave', () => {
                wrapper.classList.remove('no-effect');
            });
        });
        
        wrapper.addEventListener('mousemove', (event) => {
            if (this.isMobile || isAnimating || wrapper.classList.contains('no-effect')) return;
            
            // Проверяем, находится ли курсор над ссылкой
            const linkUnderCursor = event.target.closest('a');
            if (linkUnderCursor) return;
            
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            
            animationFrameId = requestAnimationFrame(() => {
                const rect = wrapper.getBoundingClientRect();
                const width = rect.width;
                const height = rect.height;
                
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                
                const middleX = width / 2;
                const middleY = height / 2;
                
                const maxRotation = 10; // Уменьшили для более тонкого эффекта
                const rotateX = ((y - middleY) / middleY) * maxRotation;
                const rotateY = -((x - middleX) / middleX) * maxRotation;
                
                const bgX = 50 + ((x - middleX) / middleX) * 5;
                const bgY = 50 + ((y - middleY) / middleY) * 5;
                
                card.style.setProperty('--rotateX', `${rotateX}deg`);
                card.style.setProperty('--rotateY', `${rotateY}deg`);
                card.style.setProperty('--posx', `${bgX}%`);
                card.style.setProperty('--posy', `${bgY}%`);
                
                card.style.boxShadow = `
                    0 15px 40px rgba(0, 123, 255, 0.2),
                    0 0 0 1px rgba(255, 255, 255, 0.05) inset
                `;
            });
        });
        
        wrapper.addEventListener('mouseleave', () => {
            if (this.isMobile) return;
            
            isAnimating = true;
            
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            
            card.style.animation = 'reset-card-3d 0.4s ease';
            
            card.addEventListener('animationend', () => {
                card.style.animation = 'unset';
                card.style.setProperty('--rotateX', '0deg');
                card.style.setProperty('--rotateY', '0deg');
                card.style.setProperty('--posx', '50%');
                card.style.setProperty('--posy', '50%');
                card.style.boxShadow = `
                    0 10px 30px rgba(0, 0, 0, 0.2),
                    0 0 0 1px rgba(255, 255, 255, 0.03) inset
                `;
                isAnimating = false;
            }, { once: true });
        });
        
        // Клик по карточке (кроме ссылок)
        wrapper.addEventListener('click', (event) => {
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return; // Не применяем эффект при клике на ссылку
            }
            
            card.style.transform += ' translateZ(10px)';
            setTimeout(() => {
                card.style.transform = card.style.transform.replace(' translateZ(10px)', '');
            }, 200);
        });
    }
    
    disable3DEffects() {
        this.cards.forEach(({ card }) => {
            card.style.transform = 'none';
            card.style.setProperty('--rotateX', '0deg');
            card.style.setProperty('--rotateY', '0deg');
            card.style.setProperty('--posx', '50%');
            card.style.setProperty('--posy', '50%');
        });
    }
}

function initSimple3DEffect() {
    console.log("Initializing simple 3D effect");
    
    const carCards = document.querySelectorAll('.car-card');
    
    carCards.forEach((card, index) => {
        // Создаем обертку
        const wrapper = document.createElement('div');
        wrapper.className = 'car-card-wrapper';
        
        // Сохраняем позиционирование
        const cardStyle = window.getComputedStyle(card);
        wrapper.style.width = cardStyle.width;
        wrapper.style.height = cardStyle.height;
        wrapper.style.margin = cardStyle.margin;
        
        // Обертываем карточку, не меняя её содержимое
        card.parentNode.insertBefore(wrapper, card);
        wrapper.appendChild(card);
        
        // Просто добавляем класс для 3D, не перезаписывая HTML
        card.classList.add('car-card-3d');
        
        // Создаем контент-обертку, если её нет
        if (!card.querySelector('.car-content')) {
            const content = document.createElement('div');
            content.className = 'car-content';
            
            // Перемещаем всех детей карточки в content
            while (card.firstChild) {
                content.appendChild(card.firstChild);
            }
            
            card.appendChild(content);
        }
        
        // Добавляем 3D эффект
        add3DListeners(wrapper, card);
    });
    
    console.log(`Added 3D effect to ${carCards.length} cards`);
}

function add3DListeners(wrapper, card) {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) return;
    
    let animationFrameId = null;
    
    wrapper.addEventListener('mousemove', (event) => {
        // Не применяем эффект при наведении на ссылки
        if (event.target.tagName === 'A' || event.target.closest('a')) {
            return;
        }
        
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        
        animationFrameId = requestAnimationFrame(() => {
            const rect = wrapper.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateY = ((x - centerX) / centerX) * 5; // Уменьшили угол
            const rotateX = -((y - centerY) / centerY) * 5;
            
            card.style.transform = `
                perspective(1000px)
                rotateX(${rotateX}deg)
                rotateY(${rotateY}deg)
                translateZ(10px)
            `;
            
            // Легкое свечение
            card.style.boxShadow = '0 20px 40px rgba(0, 123, 255, 0.15)';
        });
    });
    
    wrapper.addEventListener('mouseleave', () => {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        
        card.style.transition = 'transform 0.5s ease, box-shadow 0.5s ease';
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
        card.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        
        setTimeout(() => {
            card.style.transition = '';
        }, 500);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        initSimple3DEffect();
    }, 100);
});