// static/js/slider.js
class Slider {
  constructor(sliderSelector) {
    // Начальные настройки слайдера
    this.config = {
      loop: true,           // возможность листать слайдер по кругу
      navs: true,           // вывод стрелочек
      pags: true,           // вывод пагинации
      auto: true,           // авто переключение
      delay: 1000,          // время в миллисекундах
      stopMouseHover: true  // остановка при наведении мыши
    };
    
    this.currentSlide = 0;
    this.slides = document.querySelectorAll(`${sliderSelector} .slide`);
    this.counterElement = document.querySelector(`${sliderSelector} .slide-counter`);
    this.paginationContainer = document.querySelector(`${sliderSelector} .pagination`);
    this.totalSlides = this.slides.length;
    this.rotationInterval = this.config.delay;
    this.rotationTimer = null;
    this.sliderElement = document.querySelector(sliderSelector);
    
    if (this.slides.length > 0) {
      this.initSlider(sliderSelector);
      if (this.config.auto) {
        this.startRotation();
      }
    }
  }

  initSlider(sliderSelector) {
    this.showSlide(this.currentSlide);

    // Обработчики кнопок навигации (если navs = true)
    if (this.config.navs) {
      const prevZone = document.querySelector(`${sliderSelector} .prev-zone`);
      const nextZone = document.querySelector(`${sliderSelector} .next-zone`);
      
      if (prevZone) {
        prevZone.addEventListener("click", () => this.prevSlide());
      }
      if (nextZone) {
        nextZone.addEventListener("click", () => this.nextSlide());
      }
    } else {
      // Скрываем стрелки если navs = false
      const prevZone = document.querySelector(`${sliderSelector} .prev-zone`);
      const nextZone = document.querySelector(`${sliderSelector} .next-zone`);
      if (prevZone) prevZone.style.display = 'none';
      if (nextZone) nextZone.style.display = 'none';
    }

    // Создаем пагинацию (если pags = true)
    if (this.config.pags) {
      this.createPagination();
    } else {
      if (this.paginationContainer) {
        this.paginationContainer.style.display = 'none';
      }
    }

    this.updateCounter();

    // Обработчик hover для остановки автопрокрутки (если auto = true и stopMouseHover = true)
    if (this.config.auto && this.config.stopMouseHover && this.sliderElement) {
      this.sliderElement.addEventListener('mouseenter', () => this.stopRotation());
      this.sliderElement.addEventListener('mouseleave', () => {
        if (this.config.auto) this.startRotation();
      });
    }

    // Клик по слайду для перехода по ссылке
    this.slides.forEach((slide) => {
      slide.addEventListener("click", () => {
        const url = slide.getAttribute("data-url");
        if (url && url !== '#') {
          window.location.href = url;
        }
      });
    });
  }

  showSlide(index) {
    // Скрыть все слайды
    this.slides.forEach((slide, i) => {
      slide.classList.remove('active');
      slide.style.display = 'none';
    });
    
    // Показать текущий слайд
    if (this.slides[index]) {
      this.slides[index].style.display = 'block';
      setTimeout(() => {
        this.slides[index].classList.add('active');
      }, 10);
    }
    
    this.updateCounter();
    this.updatePagination();
  }

  nextSlide() {
    if (this.config.loop) {
      // Режим loop - переходим по кругу
      this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
    } else {
      // Режим без loop - останавливаемся на последнем слайде
      if (this.currentSlide < this.totalSlides - 1) {
        this.currentSlide++;
      } else if (this.config.auto) {
        // Если достигли конца и включен auto, останавливаем автопрокрутку
        this.stopRotation();
        return;
      }
    }
    this.showSlide(this.currentSlide);
  }

  prevSlide() {
    if (this.config.loop) {
      // Режим loop - переходим по кругу
      this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
    } else {
      // Режим без loop - останавливаемся на первом слайде
      if (this.currentSlide > 0) {
        this.currentSlide--;
      }
    }
    this.showSlide(this.currentSlide);
  }

  createPagination() {
    if (!this.paginationContainer) return;
    
    this.paginationContainer.innerHTML = "";
    for (let i = 0; i < this.totalSlides; i++) {
      const dot = document.createElement("div");
      dot.classList.add("dot");
      if (i === this.currentSlide) dot.classList.add("active");
      dot.addEventListener("click", () => this.goToSlide(i));
      this.paginationContainer.appendChild(dot);
    }
  }

  updatePagination() {
    if (!this.paginationContainer || !this.config.pags) return;
    
    const dots = this.paginationContainer.querySelectorAll(".dot");
    dots.forEach((dot, index) => {
      dot.classList.toggle("active", index === this.currentSlide);
    });
  }

  goToSlide(index) {
    this.currentSlide = index;
    this.showSlide(this.currentSlide);
  }

  updateCounter() {
    if (this.counterElement) {
      this.counterElement.textContent = `${this.currentSlide + 1} / ${this.totalSlides}`;
    }
  }

  startRotation() {
    this.stopRotation();
    if (this.config.auto) {
      this.rotationTimer = setInterval(() => this.nextSlide(), this.rotationInterval);
    }
  }

  stopRotation() {
    if (this.rotationTimer) {
      clearInterval(this.rotationTimer);
      this.rotationTimer = null;
    }
  }

  updateInterval() {
    const intervalInput = document.getElementById("rotation-interval");
    if (!intervalInput) return;
    
    const newInterval = parseInt(intervalInput.value);
    if (newInterval >= 1000) {
      this.config.delay = newInterval;  // обновляем config.delay
      this.rotationInterval = newInterval;
      this.startRotation();
    } else {
      alert("Интервал должен быть не менее 1000 мс.");
    }
  }

  // Метод для обновления всех настроек (для админской формы)
  updateConfig(newConfig) {
    Object.assign(this.config, newConfig);
    
    // Обновляем интервал если изменился delay
    if (newConfig.delay !== undefined) {
      this.rotationInterval = newConfig.delay;
    }
    
    // Переинициализируем слайдер с новыми настройками
    this.reinitSlider();
    
    // Перезапускаем автопрокрутку если нужно
    if (this.config.auto) {
      this.startRotation();
    } else {
      this.stopRotation();
    }
  }

  // Переинициализация слайдера
  reinitSlider() {
  // Просто обновляем видимость элементов
    const prevZone = document.querySelector('.prev-zone');
    const nextZone = document.querySelector('.next-zone');
    
    if (prevZone && nextZone) {
      prevZone.style.display = this.config.navs ? 'flex' : 'none';
      nextZone.style.display = this.config.navs ? 'flex' : 'none';
    }
    
    if (this.paginationContainer) {
      this.paginationContainer.style.display = this.config.pags ? 'flex' : 'none';
    }
    
    // Обновляем отображение текущего слайда
    this.showSlide(this.currentSlide);
  }

  // Сброс к начальным настройкам
  resetConfig() {
    const initialConfig = {
      loop: true,
      navs: true,
      pags: true,
      auto: true,
      delay: 1000,
      stopMouseHover: true
    };
    
    this.updateConfig(initialConfig);
    
    // Сбрасываем значения в админской форме
    if (document.getElementById('admin-loop')) {
      document.getElementById('admin-loop').checked = true;
      document.getElementById('admin-navs').checked = true;
      document.getElementById('admin-pags').checked = true;
      document.getElementById('admin-auto').checked = true;
      document.getElementById('admin-delay').value = 1000;
      document.getElementById('admin-hover').checked = true;
    }
    
    // Сбрасываем значение в обычной форме
    document.getElementById('rotation-interval').value = 1000;
  }
}

// Функции для работы с формами
function updateSliderConfig() {
  const form = document.getElementById('slider-admin-form');
  if (!form) return;
  
  const config = {
    loop: form.elements['loop'].checked,
    navs: form.elements['navs'].checked,
    pags: form.elements['pags'].checked,
    auto: form.elements['auto'].checked,
    delay: parseInt(form.elements['delay'].value),
    stopMouseHover: form.elements['stopMouseHover'].checked
  };
  
  window.slider.updateConfig(config);
}

function resetSliderConfig() {
  if (window.slider) {
    window.slider.resetConfig();
  }
}

// Инициализация слайдера при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  window.slider = new Slider(".photo-slider");
});