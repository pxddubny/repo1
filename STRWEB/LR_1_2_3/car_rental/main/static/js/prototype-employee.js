// === ПРОТОТИПНОЕ НАСЛЕДОВАНИЕ ===
function BaseEmployeePrototype(lastName, firstName, age, experience) {
    this._lastName = lastName;
    this._firstName = firstName;
    this._age = age;
    this._experience = experience;
}

BaseEmployeePrototype.prototype = {
    getFullName: function() {
        return `${this._lastName} ${this._firstName}`;
    },
    
    getAge: function() {
        return this._age;
    },
    
    setAge: function(newAge) {
        if (newAge >= 18 && newAge <= 70) {
            this._age = newAge;
            return true;
        }
        return false;
    },
    
    displayInfo: function() {
        return `${this.getFullName()}, ${this._age} лет, стаж: ${this._experience} лет`;
    },
    
    hasRequiredExperience: function() {
        return this._experience >= 3;
    }
};

// Класс-наследник
function EmployeePrototype(lastName, firstName, age, experience, department) {
    BaseEmployeePrototype.call(this, lastName, firstName, age, experience);
    this._department = department || 'Не указан';
}

// Наследование
EmployeePrototype.prototype = Object.create(BaseEmployeePrototype.prototype);
EmployeePrototype.prototype.constructor = EmployeePrototype;

EmployeePrototype.prototype.getDepartment = function() {
    return this._department;
};

EmployeePrototype.prototype.setDepartment = function(dept) {
    this._department = dept;
    return true;
};

EmployeePrototype.prototype.getSalary = function() {
    return this._salary || 0;
};

EmployeePrototype.prototype.setSalary = function(salary) {
    if (salary >= 0) {
        this._salary = salary;
        return true;
    }
    return false;
};

EmployeePrototype.prototype.displayInfo = function() {
    const baseInfo = BaseEmployeePrototype.prototype.displayInfo.call(this);
    return `${baseInfo}, отдел: ${this._department}`;
};