console.log("Employee List JS Loaded v2.3");

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded and parsed");

  // Используем данные из глобальной переменной
  let contacts = window.employeesData || [];
  let currentPage = 1;
  const itemsPerPage = 3;
  let currentSort = { column: null, direction: "asc" };
  let filteredContacts = [];
  let selectedEmployees = [];

  // Получаем элементы DOM
  const employeeTableBody = document.querySelector("#employee-table tbody");
  const currentPageSpan = document.getElementById("current-page");
  const totalPagesSpan = document.getElementById("total-pages");
  const prevPageBtn = document.getElementById("prev-page");
  const nextPageBtn = document.getElementById("next-page");
  const filterBtn = document.getElementById("filter-btn");
  const filterInput = document.getElementById("filter-input");
  const employeeDetails = document.getElementById("employee-details");
  const addEmployeeBtn = document.getElementById("add-employee-btn");
  const addEmployeeDropdown = document.getElementById("add-employee-dropdown");
  const cancelFormBtn = document.getElementById("cancel-form-btn");
  const addEmployeeForm = document.getElementById("add-employee-form");
  const submitEmployeeBtn = document.getElementById("submit-employee-btn");
  const formResult = document.getElementById("form-result");
  const phoneInput = document.getElementById("phone");
  const phoneError = document.getElementById("phone_error");
  const awardBtn = document.getElementById("award-btn");
  const awardText = document.getElementById("award-text");
  const linkUrlInput = document.getElementById("link_url");
  const linkUrlError = document.getElementById("link_url_error");
  const fullNameInput = document.getElementById("full_name");
  const jobDescriptionInput = document.getElementById("job_description");
  const positionInput = document.getElementById("position");
  const emailInput = document.getElementById("email");

  console.log("Elements loaded:", {
    addEmployeeBtn: !!addEmployeeBtn,
    addEmployeeDropdown: !!addEmployeeDropdown,
    addEmployeeForm: !!addEmployeeForm
  });

  // Функция для загрузки данных
  function loadContacts() {
    try {
      filteredContacts = contacts.slice();
      renderTable();
      renderPagination();
      console.log("Contacts loaded successfully");
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

  function renderPagination() {
    const totalPages = Math.ceil(filteredContacts.length / itemsPerPage);
    totalPagesSpan.textContent = totalPages || 1;
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;
  }

  // Пагинация
  prevPageBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      renderTable();
      renderPagination();
    }
  });

  nextPageBtn.addEventListener("click", () => {
    const totalPages = Math.ceil(filteredContacts.length / itemsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      renderTable();
      renderPagination();
    }
  });

  // Фильтрация
  filterBtn.addEventListener("click", () => {
    const query = filterInput.value.toLowerCase().trim();
    
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
  });

  // Сортировка
  document.querySelectorAll("#employee-table th[data-column]").forEach((header) => {
    header.addEventListener("click", () => {
      const column = header.dataset.column;
      
      if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === "asc" ? "desc" : "asc";
      } else {
        currentSort.column = column;
        currentSort.direction = "asc";
      }
      sortContacts();
      renderTable();
      updateSortIndicators();
    });
  });

  function sortContacts() {
    const { column, direction } = currentSort;
    if (!column) return;

    filteredContacts.sort((a, b) => {
      let aVal = a[column] || '';
      let bVal = b[column] || '';

      if (typeof aVal === "string") {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return direction === "asc" ? -1 : 1;
      if (aVal > bVal) return direction === "asc" ? 1 : -1;
      return 0;
    });
  }

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

  // Детали сотрудника
  employeeTableBody.addEventListener("click", (event) => {
    const row = event.target.closest("tr");
    if (!row || event.target.classList.contains('select-checkbox')) return;

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
    }
  });

  addEmployeeBtn.addEventListener("click", (event) => {
    console.log("Add Employee button clicked");
    event.stopPropagation();
    
    const isVisible = addEmployeeDropdown.style.display === 'block';
    
    if (isVisible) {
      // Скрываем форму
      addEmployeeDropdown.style.display = 'none';
      addEmployeeBtn.textContent = 'Добавить сотрудника';
      addEmployeeBtn.classList.remove("active");
    } else {
      // Показываем форму
      addEmployeeDropdown.style.display = 'block';
      addEmployeeBtn.textContent = 'Скрыть форму';
      addEmployeeBtn.classList.add("active");
    }
  });

  // Обработчик кнопки "Отмена"
  cancelFormBtn.addEventListener("click", () => {
    addEmployeeDropdown.style.display = 'none';
    addEmployeeBtn.textContent = 'Добавить сотрудника';
    addEmployeeBtn.classList.remove("active");
    resetForm();
  });

  // Закрытие формы при клике вне ее
  document.addEventListener("click", (event) => {
    if (!addEmployeeDropdown.contains(event.target) && 
        event.target !== addEmployeeBtn && 
        !addEmployeeBtn.contains(event.target)) {
      addEmployeeDropdown.style.display = 'none';
      addEmployeeBtn.textContent = 'Добавить сотрудника';
      addEmployeeBtn.classList.remove("active");
    }
  });

  // Валидация формы
  linkUrlInput.addEventListener("input", validateLinkUrl);
  phoneInput.addEventListener("input", validatePhone);
  fullNameInput.addEventListener("input", validateForm);
  jobDescriptionInput.addEventListener("input", validateForm);
  positionInput.addEventListener("input", validateForm);
  emailInput.addEventListener("input", validateForm);

  function validateLinkUrl() {
    const url = linkUrlInput.value;
    const pattern = /^(http:\/\/|https:\/\/).+\.(php|html)$/i;
    if (pattern.test(url)) {
      linkUrlError.textContent = "";
      linkUrlError.classList.remove("active");
      linkUrlInput.style.borderColor = "";
    } else {
      linkUrlError.textContent = "Некорректный URL. Пример: http://site.ru/index.php";
      linkUrlError.classList.add("active");
      linkUrlInput.style.borderColor = "#c40000";
    }
    validateForm();
  }

  function validatePhone() {
    const phone = phoneInput.value;
    const patterns = [
      /^\+375\s?\(\d{2}\)\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,
      /^\+375\s?\d{2}\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,
      /^8\s?\(\d{3}\)\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,
      /^8\s?\d{3}\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/,
      /^80\d{9}$/,
      /^\+375\d{9}$/,
      /^\+375\s?\(\d{2}\)\s?\d{3}\s\d{2}\s\d{2}$/,
      /^\+375\s?\d{2}\s?\d{3}\s\d{2}\s\d{2}$/,
      /^8\s?\(\d{3}\)\s?\d{3}\s\d{2}\s\d{2}$/,
      /^8\s?\d{3}\s?\d{3}\s\d{2}\s\d{2}$/
    ];

    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    let patternMatch = false;
    patterns.forEach(pattern => {
      if (pattern.test(phone)) patternMatch = true;
    });

    const isValid = patternMatch && (cleanPhone.length === 13 || cleanPhone.length === 11 || cleanPhone.length === 12);

    if (isValid) {
      phoneError.textContent = "";
      phoneError.classList.remove("active");
      phoneInput.style.borderColor = "";
    } else {
      phoneError.textContent = "Некорректный номер телефона. Примеры: +375 (29) 111-22-33";
      phoneError.classList.add("active");
      phoneInput.style.borderColor = "#c40000";
    }
    validateForm();
  }

  function validateForm() {
    const isLinkUrlValid = !linkUrlError.classList.contains("active") && linkUrlInput.value.trim()!== "";
    const isPhoneValid = !phoneError.classList.contains("active") && phoneInput.value.trim() !== "";
    const isFullNameValid = fullNameInput.value.trim() !== "";
    const isJobDescValid = jobDescriptionInput.value.trim() !== "";
    const isPositionValid = positionInput.value.trim() !== "";
    const isEmailValid = emailInput.value.trim() !== "";

    if (isLinkUrlValid && isPhoneValid && isFullNameValid && isJobDescValid && isPositionValid && isEmailValid) {
      submitEmployeeBtn.disabled = false;
      submitEmployeeBtn.classList.remove("inactive-btn");
    } else {
      submitEmployeeBtn.disabled = true;
      submitEmployeeBtn.classList.add("inactive-btn");
    }
  }

  // Обработчик отправки формы
  addEmployeeForm.addEventListener("submit", function(event) {
    console.log("Form submitted");
  });

  // Сброс формы
  function resetForm() {
    addEmployeeForm.reset();
    linkUrlError.classList.remove("active");
    phoneError.classList.remove("active");
    submitEmployeeBtn.disabled = true;
    formResult.textContent = "";
    linkUrlInput.style.borderColor = "";
    phoneInput.style.borderColor = "";
  }

  // Выбор сотрудников
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
    }
  });

  // Премирование
  awardBtn.addEventListener("click", () => {
    if (selectedEmployees.length === 0) {
      awardText.textContent = "Нет выбранных сотрудников для премирования.";
      awardText.classList.add("active");
      return;
    }

    const selectedNames = contacts
      .filter((contact) => selectedEmployees.includes(contact.id))
      .map((contact) => contact.name.split(' ')[0]);

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
      <p>г. Минск, ${new Date().toLocaleDateString('ru-RU')}</p>
      <p>За добросовестное выполнение трудовых обязанностей</p>
      <p><strong>ПРЕМИРОВАТЬ СОТРУДНИКОВ:</strong><br>
      <span style="color: #ffd700; font-size: 1.3em;">${namesString}</span></p>
      <p><strong>Размер премии:</strong> 15% от должностного оклада</p>
    `;
    awardText.classList.add("active");

    setTimeout(() => {
      awardText.classList.remove("active");
    }, 10000);
  });

  // Инициализация
  loadContacts();
  updateSortIndicators();
  
  // Устанавливаем начальное состояние кнопки отправки
  submitEmployeeBtn.disabled = true;
  submitEmployeeBtn.classList.add("inactive-btn");
});