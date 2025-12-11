function applyTheme(theme) {
    console.log('Applying theme:', theme);
    document.documentElement.setAttribute('data-theme', theme);
    
    // Обновляем иконку кнопки если она существует
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
        console.log('Button updated');
    }
    
    // Сохраняем в localStorage
    localStorage.setItem('theme', theme);
}

// Применяем тему сразу при загрузке скрипта
(function initTheme() {
    // Получаем сохраненную тему или используем светлую по умолчанию
    const savedTheme = localStorage.getItem('theme') || 'light';
    console.log('Saved theme:', savedTheme);
    
    // Применяем тему
    applyTheme(savedTheme);
    
    // Добавляем обработчик после загрузки DOM
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded, setting up theme toggle');
        const themeToggle = document.getElementById('theme-toggle');
        
        if (themeToggle) {
            console.log('Theme toggle button found');
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                console.log('Toggling theme from', currentTheme, 'to', newTheme);
                applyTheme(newTheme);
            });
        } else {
            console.log('Theme toggle button NOT found');
        }
    });
})();