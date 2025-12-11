// Константы для дней и месяцев
const WEEK_DAYS = ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'];
const MONTH_NAMES = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];

// Основная функция проверки возраста
function verifyUserAge() {
    console.log('Функция verifyUserAge вызвана'); // Для отладки
    
    const birthDateInput = document.getElementById('userBirthDate');
    const resultContainer = document.getElementById('verificationResult');
    
    if (!birthDateInput) {
        alert('Ошибка: поле даты не найдено!');
        return;
    }
    
    if (!birthDateInput.value) {
        alert('Пожалуйста, выберите дату рождения');
        return;
    }
    
    const userBirthDate = new Date(birthDateInput.value);
    const currentDate = new Date();
    
    // Вычисление возраста
    let years = currentDate.getFullYear() - userBirthDate.getFullYear();
    const monthDiff = currentDate.getMonth() - userBirthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && currentDate.getDate() < userBirthDate.getDate())) {
        years--;
    }
    
    console.log('Возраст:', years); // Для отладки
    
    // День недели
    const birthWeekDay = WEEK_DAYS[userBirthDate.getDay()];
    const formattedBirthDate = `${userBirthDate.getDate()} ${MONTH_NAMES[userBirthDate.getMonth()]} ${userBirthDate.getFullYear()} года`;
    
    // Проверка совершеннолетия
    const isUserAdult = years >= 18;
    !isUserAdult ? alert("для использования сайта необходимо разрешение родителей"): null;

    const ageSuffix = getAgeSuffix(years);
    resultContainer.innerHTML = `
        <div class="age-number">${years} ${ageSuffix}</div>
        <p>Дата рождения: ${formattedBirthDate}</p>
        <p>День недели: <span class="weekday">${birthWeekDay}</span></p>
        <p><strong>${isUserAdult ? '✓ Доступ разрешён' : '✗ Доступ ограничен'}</strong></p>
    `;
    
    resultContainer.className = isUserAdult ? 'result-box age-approved' : 'result-box age-restricted';
    resultContainer.style.display = 'block';
    
    // Показ предупреждения для несовершеннолетних
    if (!isUserAdult) {
        document.getElementById('parentAlert').style.display = 'block';
    }
}

// Функция для правильного склонения "год/года/лет"
function getAgeSuffix(age) {
    const lastDigit = age % 10;
    const lastTwoDigits = age % 100;
    
    if (lastDigit === 1 && lastTwoDigits !== 11) return 'год';
    if (lastDigit >= 2 && lastDigit <= 4 && (lastTwoDigits < 10 || lastTwoDigits >= 20)) return 'года';
    return 'лет';
}

// Скрытие модального окна
function hideAlert() {
    document.getElementById('parentAlert').style.display = 'none';
}

// Блокировка выбора будущих дат при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const birthDateInput = document.getElementById('userBirthDate');
    if (birthDateInput) {
        birthDateInput.max = new Date().toISOString().split('T')[0];
    }
    
    // Обработка нажатия Enter
    if (birthDateInput) {
        birthDateInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                verifyUserAge();
            }
        });
    }
    
    // Закрытие модального окна при клике вне его
    document.addEventListener('click', function(event) {
        const alertModal = document.getElementById('parentAlert');
        if (alertModal && alertModal.style.display === 'block' && !alertModal.contains(event.target)) {
            hideAlert();
        }
    });
});