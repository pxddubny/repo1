console.log("Car List Pagination JS Loaded");

document.addEventListener('DOMContentLoaded', function() {
    // Обработчик для селектора количества элементов
    const itemsPerPageSelect = document.getElementById('items-per-page-select');
    
    // Функция загрузки из cookie
    function loadItemsPerPageFromCookie() {
        if (!itemsPerPageSelect) return;
        
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'car_items_per_page') {
                itemsPerPageSelect.value = value;
                console.log('Loaded items per page from cookie:', value);
                break;
            }
        }
    }
    
    if (itemsPerPageSelect) {
        itemsPerPageSelect.addEventListener('change', function() {
            const selectedValue = this.value;
            console.log('Items per page changed to:', selectedValue);
            
            // Показываем прелоадер
            showLoader();
            
            // Сохраняем в cookie
            document.cookie = `car_items_per_page=${selectedValue}; path=/; max-age=2592000`;
            
            // Обновляем URL
            const url = new URL(window.location.href);
            url.searchParams.set('items_per_page', selectedValue);
            url.searchParams.set('page', 1);
            
            // Задержка для демонстрации прелоадера
            setTimeout(() => {
                window.location.href = url.toString();
            }, 500);
        });
        
        loadItemsPerPageFromCookie();
    }
    
    // Обработчики для кнопок пагинации
    document.querySelectorAll('.pagination-btn:not([disabled])').forEach(button => {
        button.addEventListener('click', function() {
            const page = this.dataset.page;
            if (!page) return;
            
            console.log('Navigating to page:', page);
            showLoader();
            
            const url = new URL(window.location.href);
            url.searchParams.set('page', page);
            
            setTimeout(() => {
                window.location.href = url.toString();
            }, 500);
        });
    });
    
    // Обработчик для формы поиска
    const searchForm = document.getElementById('car-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            console.log('Search form submitted');
            showLoader();
            
            const itemsPerPage = document.getElementById('items-per-page-select')?.value || 3;
            
            let hiddenItemsField = this.querySelector('input[name="items_per_page"]');
            if (!hiddenItemsField) {
                hiddenItemsField = document.createElement('input');
                hiddenItemsField.type = 'hidden';
                hiddenItemsField.name = 'items_per_page';
                this.appendChild(hiddenItemsField);
            }
            hiddenItemsField.value = itemsPerPage;
            
            let pageField = this.querySelector('input[name="page"]');
            if (!pageField) {
                pageField = document.createElement('input');
                pageField.type = 'hidden';
                pageField.name = 'page';
                this.appendChild(pageField);
            }
            pageField.value = 1;
        });
    }
    
    // Функция для показа прелоадера
    function showLoader() {
        let loader = document.getElementById('simpleLoader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'simpleLoader';
            loader.className = 'simple-loader';
            loader.innerHTML = `
                <div class="infinity-clear">
                    <div class="circle circle-left"></div>
                    <div class="circle circle-right"></div>
                </div>
            `;
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
        
        setTimeout(() => {
            if (loader.style.display === 'flex') {
                loader.style.display = 'none';
            }
        }, 5000);
    }
});