// Глобальные массивы
let prototypeEmployees = [];
let classEmployees = [];

// === МЕТОДЫ ДОБАВЛЕНИЯ ЧЕРЕЗ ФОРМУ ===

// Метод добавления для прототипных сотрудников
function addEmployeePrototypeFromForm() {
    const lastName = document.getElementById('lastName').value.trim();
    const firstName = document.getElementById('firstName').value.trim();
    const age = parseInt(document.getElementById('age').value);
    const experience = parseInt(document.getElementById('experience').value);
    const department = document.getElementById('department').value.trim();
    const salary = parseInt(document.getElementById('salary').value) || 0;
    
    if (!lastName || !firstName || isNaN(age) || isNaN(experience)) {
        alert('Заполните обязательные поля: Фамилия, Имя, Возраст, Стаж');
        return;
    }
    
    const employee = new EmployeePrototype(lastName, firstName, age, experience, department);
    if (salary > 0) employee.setSalary(salary);
    
    prototypeEmployees.push(employee);
    displayAllEmployees();
    updateStats();
    clearForm();
}

// Метод добавления для классовых сотрудников
function addEmployeeClassFromForm() {
    const lastName = document.getElementById('lastName').value.trim();
    const firstName = document.getElementById('firstName').value.trim();
    const age = parseInt(document.getElementById('age').value);
    const experience = parseInt(document.getElementById('experience').value);
    const department = document.getElementById('department').value.trim();
    const salary = parseInt(document.getElementById('salary').value) || 0;
    
    if (!lastName || !firstName || isNaN(age) || isNaN(experience)) {
        alert('Заполните обязательные поля: Фамилия, Имя, Возраст, Стаж');
        return;
    }
    
    const employee = new EmployeeClass(lastName, firstName, age, experience, department, salary);
    classEmployees.push(employee);
    displayAllEmployees();
    updateStats();
    clearForm();
}

// === МЕТОД ВЫВОДА ВСЕХ ОБЪЕКТОВ ===
function displayAllEmployees() {
    const protoDiv = document.getElementById('prototypeEmployees');
    const classDiv = document.getElementById('classEmployees');
    
    // Прототипные сотрудники
    protoDiv.innerHTML = '<h3>👥 Сотрудники (Прототипное наследование):</h3>';
    if (prototypeEmployees.length === 0) {
        protoDiv.innerHTML += '<p>Нет сотрудников</p>';
    } else {
        prototypeEmployees.forEach((emp, index) => {
            const expClass = emp._experience >= 3 ? 'young' : '';
            protoDiv.innerHTML += `
                <div class="employee-card ${expClass}">
                    <strong>${emp.getFullName()}</strong><br>
                    Возраст: ${emp.getAge()} лет, Стаж: ${emp._experience} лет<br>
                    Отдел: ${emp.getDepartment()}<br>
                    ${emp.getSalary() > 0 ? `Зарплата: ${emp.getSalary().toLocaleString()} руб.<br>` : ''}
                    <em>ID: ${index + 1}</em>
                </div>
            `;
        });
    }
    
    // Классовые сотрудники
    classDiv.innerHTML = '<h3>👥 Сотрудники (Классы ES6):</h3>';
    if (classEmployees.length === 0) {
        classDiv.innerHTML += '<p>Нет сотрудников</p>';
    } else {
        classEmployees.forEach((emp, index) => {
            const expClass = emp.hasRequiredExperience() ? 'young' : '';
            classDiv.innerHTML += `
                <div class="employee-card ${expClass}">
                    <strong>${emp.getFullName()}</strong><br>
                    Возраст: ${emp.age} лет, Стаж: ${emp.experience} лет<br>
                    Отдел: ${emp.department}<br>
                    Зарплата: ${emp.salary.toLocaleString()} руб.<br>
                    <em>ID: ${index + 1}</em>
                </div>
            `;
        });
    }
}

// === МЕТОД ВЫВОДА РЕЗУЛЬТАТА ===
function findYoungestEmployees() {
    const allEmployees = [...prototypeEmployees, ...classEmployees];
    
    // 1. Фильтруем сотрудников со стажем ≥ 3 лет
    const experiencedEmployees = allEmployees.filter(emp => {
        // Проверяем в зависимости от типа объекта
        if (emp.hasRequiredExperience) {
            return emp.hasRequiredExperience();
        } else {
            return emp._experience >= 3;
        }
    });
    
    if (experiencedEmployees.length === 0) {
        document.getElementById('combinedResult').innerHTML = 
            '<div class="employee-card">❌ Нет сотрудников со стажем от 3 лет</div>';
        return;
    }
    
    // 2. Находим минимальный возраст
    const minAge = Math.min(...experiencedEmployees.map(emp => {
        return emp.age || emp.getAge();
    }));
    
    // 3. Находим всех с минимальным возрастом
    const youngestEmployees = experiencedEmployees.filter(emp => {
        return (emp.age || emp.getAge()) === minAge;
    });
    
    // 4. Выводим результат В ЖЕЛТОЙ РАМКЕ (#combinedResult)
    const resultDiv = document.getElementById('combinedResult');
    resultDiv.innerHTML = `
        <h3>🎯 Самые молодые сотрудники со стажем ≥3 лет:</h3>
        <p><strong>Минимальный возраст среди опытных:</strong> ${minAge} лет</p>
        <p><strong>Найдено сотрудников:</strong> ${youngestEmployees.length}</p>
    `;
    
    if (youngestEmployees.length === 0) {
        resultDiv.innerHTML += '<div class="employee-card">Ничего не найдено</div>';
        return;
    }
    
    youngestEmployees.forEach((emp, index) => {
        const isClass = emp.constructor.name === 'EmployeeClass';
        const age = isClass ? emp.age : emp.getAge();
        const experience = isClass ? emp.experience : emp._experience;
        const department = isClass ? emp.department : emp.getDepartment();
        const salary = isClass ? emp.salary : emp.getSalary();
        
        resultDiv.innerHTML += `
            <div class="employee-card young">
                <h4>🏆 ${emp.getFullName()}</h4>
                <p><strong>Возраст:</strong> ${age} лет (самый молодой среди опытных)</p>
                <p><strong>Стаж:</strong> ${experience} лет (≥3 лет)</p>
                <p><strong>Отдел:</strong> ${department}</p>
                ${salary > 0 ? `<p><strong>Зарплата:</strong> ${salary.toLocaleString()} руб.</p>` : ''}
                <p><em>Тип объекта: ${emp.constructor.name}</em></p>
            </div>
        `;
    });
    
    updateStats();
}

// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
function clearForm() {
    document.getElementById('lastName').value = '';
    document.getElementById('firstName').value = '';
    document.getElementById('age').value = '';
    document.getElementById('experience').value = '';
    document.getElementById('department').value = '';
    document.getElementById('salary').value = '';
}

function updateStats() {
    const allEmployees = [...prototypeEmployees, ...classEmployees];
    document.getElementById('totalCount').textContent = allEmployees.length;
    
    const experienced = allEmployees.filter(emp => {
        if (emp.hasRequiredExperience) {
            return emp.hasRequiredExperience();
        } else {
            return emp._experience >= 3;
        }
    });
    
    if (experienced.length > 0) {
        const minAge = Math.min(...experienced.map(emp => emp.age || emp.getAge()));
        const youngestCount = experienced.filter(emp => (emp.age || emp.getAge()) === minAge).length;
        document.getElementById('youngestCount').textContent = youngestCount;
        document.getElementById('minAge').textContent = minAge;
    }
}

// Инициализация тестовыми данными
function initTestData() {
    // Тестовые данные для прототипов
    prototypeEmployees = [
        new EmployeePrototype('Иванов', 'Иван', 25, 4, 'IT отдел'),
        new EmployeePrototype('Петров', 'Петр', 28, 5, 'Бухгалтерия'),
        new EmployeePrototype('Сидорова', 'Анна', 22, 1, 'HR'),
        new EmployeePrototype('Кузнецов', 'Алексей', 25, 3, 'Продажи'),
        new EmployeePrototype('Волкова', 'Мария', 24, 3, 'Маркетинг')
    ];
    
    // Тестовые данные для классов
    classEmployees = [
        new EmployeeClass('Новиков', 'Дмитрий', 24, 2, 'IT отдел', 80000),
        new EmployeeClass('Федорова', 'Екатерина', 27, 6, 'Бухгалтерия', 85000),
        new EmployeeClass('Морозов', 'Сергей', 22, 3, 'Продажи', 50000),
        new EmployeeClass('Лебедев', 'Андрей', 35, 12, 'Руководство', 150000)
    ];
    
    // Установка зарплат для прототипных сотрудников
    prototypeEmployees[0].setSalary(80000);
    prototypeEmployees[1].setSalary(65000);
    prototypeEmployees[2].setSalary(45000);
    prototypeEmployees[3].setSalary(70000);
    prototypeEmployees[4].setSalary(60000);
    
    displayAllEmployees();
    updateStats();
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', initTestData);