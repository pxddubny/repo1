console.log("Employee List JS Loaded v2.0");

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded and parsed");

  // Используем данные из глобальной переменной
  let contacts = window.employeesData || [];
  let currentPage = 1;
  const itemsPerPage = 3;
  let currentSort = { column: null, direction: "asc" };
  let filteredContacts = [];
  let selectedEmployees = [];

  const employeeTableBody = document.querySelector("#employee-table tbody");
  const currentPageSpan = document.getElementById("current-page");
  const totalPagesSpan = document.getElementById("total-pages");
  const prevPageBtn = document.getElementById("prev-page");
  const nextPageBtn = document.getElementById("next-page");
  const filterBtn = document.getElementById("filter-btn");
  const filterInput = document.getElementById("filter-input");
  const employeeDetails = document.getElementById("employee-details");
  const addEmployeeBtn = document.getElementById("add-employee-btn");
  const addEmployeeModal = document.getElementById("add-employee-modal");
  const modalClose = document.getElementById("modal-close");
  const addEmployeeForm = document.getElementById("add-employee-form");
  const submitEmployeeBtn = document.getElementById("submit-employee-btn");
  const formResult = document.getElementById("form-result");
  const phoneInput = document.getElementById("phone");
  const phoneError = document.getElementById("phone_error");
  const awardBtn = document.getElementById("award-btn");
  const awardText = document.getElementById("award-text");
  const linkUrlInput = document.getElementById("link_url");
  const linkUrlError = document.getElementById("link_url_error");

  // Получение остальных полей формы
  const fullNameInput = document.getElementById("full_name");
  const jobDescriptionInput = document.getElementById("job_description");
  const positionInput = document.getElementById("position");
  const emailInput = document.getElementById("email");

  console.log("Initial contacts:", contacts);

  // Функция для загрузки данных
  function loadContacts() {
    try {
      filteredContacts = contacts.slice();
      renderTable();
      renderPagination();
      console.log("Contacts loaded successfully from window data");
    } catch (error) {
      console.error("Ошибка при загрузке данных:", error);
      employeeTableBody.innerHTML = `<tr><td colspan="8">Не удалось загрузить данные.</td></tr>`;
    }
  }

  function renderTable() {
    employeeTableBody.innerHTML = "";
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const paginatedContacts = filteredContacts.slice(start, end);

    if (paginatedContacts.length === 0) {
      employeeTableBody.innerHTML = `<tr><td colspan="8">Нет сотрудников для отображения.</td></tr>`;
      return;
    }

    paginatedContacts.forEach((contact) => {
      const row = document.createElement("tr");
      row.dataset.id = contact.id;

      const isChecked = selectedEmployees.includes(contact.id);

      row.innerHTML = `
        <td>${contact.name || ''}</td>
        <td>${contact.photo_path ? `<img src="${contact.photo_path}" alt="Фото" style="max-width: 100px;">` : 'Нет фото'}</td>
        <td>${contact.description || ''}</td>
        <td>${contact.position || ''}</td>
        <td>${contact.phone || ''}</td>
        <td>${contact.email || ''}</td>
        <td>${contact.link || ''}</td>
        <td><input type="checkbox" class="select-checkbox" value="${contact.id}" ${
          isChecked ? "checked" : ""
        }></td>
      `;
      employeeTableBody.appendChild(row);
    });

    currentPageSpan.textContent = currentPage;
  }

  // Функция для рендеринга пагинации
  function renderPagination() {
    const totalPages = Math.ceil(filteredContacts.length / itemsPerPage);
    totalPagesSpan.textContent = totalPages || 1;

    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;
  }

  // Обработчики пагинации
  prevPageBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      renderTable();
      renderPagination();
      console.log(`Перейдено на страницу ${currentPage}`);
    }
  });

  nextPageBtn.addEventListener("click", () => {
    const totalPages = Math.ceil(filteredContacts.length / itemsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      renderTable();
      renderPagination();
      console.log(`Перейдено на страницу ${currentPage}`);
    }
  });

  // Обработчик фильтрации
  // Обработчик фильтрации с прелоадером
  filterBtn.addEventListener("click", () => {
    const query = filterInput.value.toLowerCase().trim();
    
    showLoader();
    
    setTimeout(() => {
      if (query === "") {
        filteredContacts = contacts.slice();
      } else {
        filteredContacts = contacts.filter(
          (contact) =>
            (contact.name && contact.name.toLowerCase().includes(query)) ||
            (contact.description && contact.description.toLowerCase().includes(query)) ||
            (contact.position && contact.position.toLowerCase().includes(query)) ||
            (contact.phone && contact.phone.toLowerCase().includes(query)) ||
            (contact.email && contact.email.toLowerCase().includes(query))
        );
      }
      currentPage = 1;
      renderTable();
      renderPagination();
      console.log(`Фильтрация по запросу: "${query}"`);
      
      hideLoader();
    }, 500);
  });

  // Обработчик сортировки с прелоадером
  document.querySelectorAll("#employee-table th[data-column]").forEach((header) => {
    header.addEventListener("click", () => {
      const column = header.dataset.column;
      
      showLoader();
      
      setTimeout(() => {
        if (currentSort.column === column) {
          currentSort.direction = currentSort.direction === "asc" ? "desc" : "asc";
        } else {
          currentSort.column = column;
          currentSort.direction = "asc";
        }
        sortContacts();
        renderTable();
        updateSortIndicators();
        console.log(`Сортировка по столбцу: "${column}", направление: "${currentSort.direction}"`);
        
        hideLoader();
      }, 300);
    });
  });

  // Функция сортировки
  function sortContacts() {
    const { column, direction } = currentSort;
    if (!column) return;

    filteredContacts.sort((a, b) => {
      let aVal = a[column] || '';
      let bVal = b[column] || '';

      // Для строк
      if (typeof aVal === "string") {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return direction === "asc" ? -1 : 1;
      if (aVal > bVal) return direction === "asc" ? 1 : -1;
      return 0;
    });
  }

  // Функция обновления индикаторов сортировки
  function updateSortIndicators() {
    document.querySelectorAll("#employee-table th[data-column]").forEach((header) => {
      const indicator = header.querySelector(".sort-indicator");
      const column = header.dataset.column;
      if (column === currentSort.column) {
        indicator.textContent = currentSort.direction === "asc" ? " ▲" : " ▼";
      } else {
        indicator.textContent = "";
      }
    });
  }

  // Обработчик клика на строку таблицы для отображения деталей
  employeeTableBody.addEventListener("click", (event) => {
    const row = event.target.closest("tr");
    if (!row) return;

    const contactId = row.dataset.id;
    const contact = contacts.find((c) => c.id == contactId);
    if (contact) {
      employeeDetails.innerHTML = `
        <h3>Детали сотрудника</h3>
        <p><strong>ФИО:</strong> ${contact.name}</p>
        <p><strong>Должность:</strong> ${contact.position}</p>
        <p><strong>Описание работ:</strong> ${contact.description}</p>
        <p><strong>Телефон:</strong> ${contact.phone}</p>
        <p><strong>Почта:</strong> ${contact.email}</p>
        ${contact.photo_path ? `<img src="${contact.photo_path}" alt="Фото" width="100">` : ''}
      `;
      employeeDetails.classList.add("active");
      console.log(`Отображение деталей для сотрудника: ${contact.name}`);
    }
  });

  // Обработчик для кнопки добавления сотрудника
  addEmployeeBtn.addEventListener("click", () => {
    console.log("Add Employee button clicked");
    console.log("Modal before:", getComputedStyle(addEmployeeModal).display);
    addEmployeeModal.classList.add("active");
    console.log("Modal after:", getComputedStyle(addEmployeeModal).display);
    console.log("Modal classes:", addEmployeeModal.classList);
  });

  // Обработчик для закрытия модального окна
  modalClose.addEventListener("click", () => {
    console.log("Modal close button clicked");
    addEmployeeModal.classList.remove("active");
    resetForm();
  });

  // Закрытие модального окна при клике вне его
  window.addEventListener("click", (event) => {
    if (event.target === addEmployeeModal) {
      console.log("Clicked outside modal");
      addEmployeeModal.classList.remove("active");
      resetForm();
    }
  });

  // Валидация ссылки (link_url)
  linkUrlInput.addEventListener("input", () => {
    const url = linkUrlInput.value;
    // Разрешаем пустую строку или URL начинающийся с http/https
    const pattern = /^(|http:\/\/|https:\/\/.+)$/i;
    if (pattern.test(url)) {
      linkUrlError.classList.remove("active");
      linkUrlInput.style.borderColor = "";
      linkUrlInput.style.backgroundColor = "";
      console.log("Link URL valid");
      linkUrlError.textContent = "";
    } else {
      linkUrlError.textContent = "Некорректный URL. Пример: http://site.ru/index.php";
      linkUrlError.classList.add("active");
      linkUrlInput.style.borderColor = "#c40000";
      linkUrlInput.style.backgroundColor = "#ff4fce";
      console.log("Link URL invalid");
    }
    validateForm();
  });

  // Валидация телефона
  // Валидация телефона
  // Валидация телефона - ОБНОВЛЕННАЯ ВЕРСИЯ с отладкой
  phoneInput.addEventListener("input", () => {
    const phone = phoneInput.value;
    console.log("=== PHONE VALIDATION START ===");
    console.log("Input value:", phone);
    
    // Убираем все пробелы, дефисы и скобки для проверки длины
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    console.log("Clean phone (no spaces):", cleanPhone);
    console.log("Clean phone length:", cleanPhone.length);
    
    // Проверяем различные форматы
    const patterns = [
      /^\+375\s?\(\d{2}\)\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,      // +375 (29) 111-22-33 или +375 (29) 111 22 33
      /^\+375\s?\d{2}\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,          // +375 29 111-22-33 или +375 29 111 22 33
      /^8\s?\(\d{3}\)\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,          // 8 (029) 111-22-33 или 8 (029) 111 22 33
      /^8\s?\d{3}\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,              // 8 029 111-22-33 или 8 029 111 22 33
      /^80\d{9}$/,                                                // 80291112233 (11 цифр)
      /^\+375\d{9}$/,                                             // +375291112233 (12 цифр + знак + = 13 символов)
      /^\+375\s?\(\d{2}\)\s?\d{3}\s\d{2}\s\d{2}$/,                // +375 (29) 111 22 33 (специально для вашего формата)
      /^\+375\s?\d{2}\s?\d{3}\s\d{2}\s\d{2}$/,                    // +375 29 111 22 33
      /^8\s?\(\d{3}\)\s?\d{3}\s\d{2}\s\d{2}$/,                    // 8 (029) 111 22 33
      /^8\s?\d{3}\s?\d{3}\s\d{2}\s\d{2}$/                         // 8 029 111 22 33
    ];

    console.log("Testing patterns:");
    let patternMatch = false;
    patterns.forEach((pattern, index) => {
      const matches = pattern.test(phone);
      console.log(`Pattern ${index}: ${pattern.source} => ${matches}`);
      if (matches) patternMatch = true;
    });

    // ИСПРАВЛЕННАЯ ПРОВЕРКА ДЛИНЫ:
    // +375291112233 = 13 символов (+ + 12 цифр)
    // 80291112233 = 11 цифр
    const isValid = patternMatch && (cleanPhone.length === 13 || cleanPhone.length === 11 || cleanPhone.length === 12);
    
    // ИЛИ более простое решение - проверять только паттерны:
    // const isValid = patternMatch; // Убрать проверку длины вообще

    console.log("Pattern match:", patternMatch);
    console.log("Clean phone length:", cleanPhone.length);
    console.log("Final isValid result:", isValid);

    if (isValid) {
      console.log("Phone number is VALID");
      phoneError.textContent = "";
      phoneError.classList.remove("active");
      phoneInput.style.borderColor = "";
      phoneInput.style.backgroundColor = "";
    } else {
      console.log("Phone number is INVALID");
      phoneError.textContent = "Некорректный номер телефона. Примеры: +375 (29) 111-22-33, +375 (29) 111 22 33, 8 (029) 1112233";
      phoneError.classList.add("active");
      phoneInput.style.borderColor = "#c40000";
      phoneInput.style.backgroundColor = "#ff4fce";
    }
    
    console.log("=== PHONE VALIDATION END ===");
    validateForm();
  });
  // Устанавливаем начальное состояние кнопки (неактивная)
  submitEmployeeBtn.disabled = true;
  submitEmployeeBtn.classList.add("inactive-btn");

  // Функция проверки формы
  function validateForm() {
    const isLinkUrlValid = !linkUrlError.classList.contains("active");
    const isPhoneValid = !phoneError.classList.contains("active") && phoneInput.value.trim() !== "";
    const isFullNameValid = fullNameInput.value.trim() !== "";
    const isJobDescValid = jobDescriptionInput.value.trim() !== "";
    const isPositionValid = positionInput.value.trim() !== "";
    const isEmailValid = emailInput.value.trim() !== "";

    // Активируем кнопку, если все поля валидны
    if (isLinkUrlValid && isPhoneValid && isFullNameValid && isJobDescValid && isPositionValid && isEmailValid) {
      submitEmployeeBtn.disabled = false;
      submitEmployeeBtn.classList.remove("inactive-btn");
    } else {
      submitEmployeeBtn.disabled = true;
      submitEmployeeBtn.classList.add("inactive-btn");
    }
  }

  // Добавляем обработчики валидации для всех полей
  linkUrlInput.addEventListener("input", validateForm);
  phoneInput.addEventListener("input", validateForm);
  fullNameInput.addEventListener("input", validateForm);
  jobDescriptionInput.addEventListener("input", validateForm);
  positionInput.addEventListener("input", validateForm);
  emailInput.addEventListener("input", validateForm);

  // Обработчик отправки формы
  addEmployeeForm.addEventListener("submit", function(event) {
    console.log("Form submitted via Django");
  });

  // Функция сброса формы
  function resetForm() {
    addEmployeeForm.reset();
    linkUrlError.classList.remove("active");
    phoneError.classList.remove("active");
    submitEmployeeBtn.disabled = true;
    formResult.textContent = "";
    linkUrlInput.style.borderColor = "";
    linkUrlInput.style.backgroundColor = "";
    phoneInput.style.borderColor = "";
    phoneInput.style.backgroundColor = "";
    console.log("Form reset");
  }

  // Обработчик для чекбоксов
  employeeTableBody.addEventListener("change", (event) => {
    const checkbox = event.target;
    if (checkbox.classList.contains("select-checkbox")) {
      const employeeId = parseInt(checkbox.value);
      if (checkbox.checked) {
        if (!selectedEmployees.includes(employeeId)) {
          selectedEmployees.push(employeeId);
        }
      } else {
        selectedEmployees = selectedEmployees.filter((id) => id !== employeeId);
      }
      console.log("Selected employees:", selectedEmployees);
    }
  });

  // Обработчик премирования
  // Обработчик премирования
  awardBtn.addEventListener("click", () => {
    if (selectedEmployees.length === 0) {
      awardText.textContent = "Нет выбранных сотрудников для премирования.";
      awardText.classList.add("active");
      console.log("No employees selected for awarding");
      return;
    }

    // Показываем прелоадер
    showLoader();

    // Имитируем задержку для демонстрации прелоадера
    setTimeout(() => {
      const selectedNames = contacts
        .filter((contact) => selectedEmployees.includes(contact.id))
        .map((contact) => {
          // Берем только первое слово из ФИО (фамилию)
          const firstName = contact.name.split(' ')[0];
          return firstName;
        });

      // Создаем красивый текст премирования
      let namesString;
      if (selectedNames.length === 1) {
        namesString = selectedNames[0];
      } else if (selectedNames.length === 2) {
        namesString = selectedNames.join(' и ');
      } else {
        namesString = selectedNames.slice(0, -1).join(', ') + ' и ' + selectedNames.slice(-1);
      }

      awardText.innerHTML = `
        <h3>🎉 Приказ о премировании</h3>
        <p><strong>ООО "ТМЫВ ДЕНЕГ"</strong></p>
        <p>г. Минск, ${new Date().toLocaleDateString('ru-RU', { 
          day: 'numeric', 
          month: 'long', 
          year: 'numeric' 
        })}</p>
        
        <p>За добросовестное выполнение трудовых обязанностей, высокие профессиональные достижения и вклад в развитие компании</p>
        
        <p style="text-align: center; font-size: 1.2em; margin: 15px 0;">
          <strong>ПРЕМИРОВАТЬ СОТРУДНИКОВ:</strong><br>
          <span style="color: #ffd700; font-size: 1.3em;">${namesString}</span>
        </p>
        
        <p><strong>Размер премии:</strong> 15% от должностного оклада</p>
        <p><strong>Срок выплаты:</strong> до ${new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString('ru-RU')}</p>
        <p><strong>Основание:</strong> приказ генерального директора №${Math.floor(Math.random() * 1000) + 1}</p>
        
        <p style="text-align: right; margin-top: 20px;">
          <strong>Генеральный директор</strong><br>
          ___________ И.И. Иванов
        </p>
      `;
      awardText.classList.add("active");
      console.log(`Awarded employees: ${namesString}`);

      // Скрываем прелоадер
      hideLoader();

      // Скрыть сообщение через 10 секунд
      setTimeout(() => {
        awardText.classList.remove("active");
        console.log("Award message hidden");
      }, 10000);
    }, 1500);
  });
  // Инициализация загрузки данных
  loadContacts();
  // Функция для показа прелоадера
  function showLoader() {
    const loader = document.getElementById('simpleLoader');
    if (loader) {
      loader.style.display = 'flex';
    }
  }

  // Функция для скрытия прелоадера
  function hideLoader() {
    const loader = document.getElementById('simpleLoader');
    if (loader) {
      loader.style.display = 'none';
    }
  }

  // Обработчик премирования с прелоадером
  awardBtn.addEventListener("click", () => {
    if (selectedEmployees.length === 0) {
      awardText.textContent = "Нет выбранных сотрудников для премирования.";
      awardText.classList.add("active");
      console.log("No employees selected for awarding");
      return;
    }

    // Показываем прелоадер
    showLoader();

    // Имитируем задержку для демонстрации прелоадера
    setTimeout(() => {
      const selectedNames = contacts
        .filter((contact) => selectedEmployees.includes(contact.id))
        .map((contact) => {
          // Берем только первое слово из ФИО (фамилию)
          const firstName = contact.name.split(' ')[0];
          return firstName;
        });

      const namesString = selectedNames.join(", ");
      awardText.innerHTML = `
        <h3>Приказ о премировании</h3>
        <p>За добросовестное выполнение трудовых обязанностей и высокие профессиональные достижения</p>
        <p><strong>ПРЕМИРОВАТЬ СОТРУДНИКОВ:</strong> ${namesString}</p>
        <p>Размер премии: 15% от должностного оклада</p>
        <p>Основание: приказ генерального директора №${Math.floor(Math.random() * 1000) + 1} от ${new Date().toLocaleDateString('ru-RU')}</p>
      `;
      awardText.classList.add("active");
      console.log(`Awarded employees: ${namesString}`);

      // Скрываем прелоадер
      hideLoader();

      // Скрыть сообщение через 8 секунд
      setTimeout(() => {
        awardText.classList.remove("active");
        console.log("Award message hidden");
      }, 8000);
    }, 1500); // Задержка 1.5 секунды для демонстрации прелоадера
  });
});
