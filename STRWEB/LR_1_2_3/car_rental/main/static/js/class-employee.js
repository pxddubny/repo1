// === КЛАССЫ ES6 ===

// Базовый класс ES6
class BaseEmployeeClass {
    constructor(lastName, firstName, age, experience) {
        this._lastName = lastName;
        this._firstName = firstName;
        this._age = age;
        this._experience = experience;
    }
    
    // 1. ГЕТТЕР - полное имя
    getFullName() {
        return `${this._lastName} ${this._firstName}`;
    }
    
    // 2. ГЕТТЕР - возраст
    get age() {
        return this._age;
    }
    
    // 3. СЕТТЕР - возраст
    set age(value) {
        if (value >= 18 && value <= 70) {
            this._age = value;
        }
    }
    
    // 4. Метод вывода информации
    displayInfo() {
        return `${this.getFullName()}, ${this._age} лет, стаж: ${this._experience} лет`;
    }
    
    // 5. Метод проверки стажа
    hasRequiredExperience() {
        return this._experience >= 3;
    }
    
    // Геттер для опыта (дополнительно)
    get experience() {
        return this._experience;
    }
    
    // Сеттер для опыта (дополнительно)
    set experience(value) {
        if (value >= 0) {
            this._experience = value;
        }
    }
}

// Класс-наследник ES6
class EmployeeClass extends BaseEmployeeClass {
    constructor(lastName, firstName, age, experience, department, salary) {
        super(lastName, firstName, age, experience);
        this._department = department || 'Не указан';
        this._salary = salary || 0;
    }
    
    // 1. ГЕТТЕР - отдел
    get department() {
        return this._department;
    }
    
    // 2. СЕТТЕР - отдел
    set department(value) {
        this._department = value;
    }
    
    // 3. ГЕТТЕР - зарплата
    get salary() {
        return this._salary;
    }
    
    // 4. СЕТТЕР - зарплата
    set salary(value) {
        if (value >= 0) {
            this._salary = value;
        }
    }
    
    // 5. Метод вывода информации (переопределение)
    displayInfo() {
        return `${super.displayInfo()}, отдел: ${this._department}, зарплата: ${this._salary.toLocaleString()} руб.`;
    }
}