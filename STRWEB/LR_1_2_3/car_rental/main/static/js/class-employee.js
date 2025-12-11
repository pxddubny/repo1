
class BaseEmployeeClass {
    constructor(lastName, firstName, age, experience) {
        this._lastName = lastName;
        this._firstName = firstName;
        this._age = age;
        this._experience = experience;
    }
    
    getFullName() {
        return `${this._lastName} ${this._firstName}`;
    }
    
    get age() {
        return this._age;
    }
    
    set age(value) {
        if (value >= 18 && value <= 70) {
            this._age = value;
        }
    }
    
    displayInfo() {
        return `${this.getFullName()}, ${this._age} лет, стаж: ${this._experience} лет`;
    }
    
    hasRequiredExperience() {
        return this._experience >= 3;
    }
    
    get experience() {
        return this._experience;
    }
    
    set experience(value) {
        if (value >= 0) {
            this._experience = value;
        }
    }
}

class EmployeeClass extends BaseEmployeeClass {
    constructor(lastName, firstName, age, experience, department, salary) {
        super(lastName, firstName, age, experience);
        this._department = department || 'Не указан';
        this._salary = salary || 0;
    }
    
    get department() {
        return this._department;
    }
    
    set department(value) {
        this._department = value;
    }
    
    get salary() {
        return this._salary;
    }

    set salary(value) {
        if (value >= 0) {
            this._salary = value;
        }
    }
    
    displayInfo() {
        return `${super.displayInfo()}, отдел: ${this._department}, зарплата: ${this._salary.toLocaleString()} руб.`;
    }
}