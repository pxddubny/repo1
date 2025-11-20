// static/js/slider.js
class Slider {
  constructor(sliderSelector) {
    this.currentSlide = 0;
    this.slides = document.querySelectorAll(`${sliderSelector} .slide`);
    this.counterElement = document.querySelector(`${sliderSelector} .slide-counter`);
    this.paginationContainer = document.querySelector(`${sliderSelector} .pagination`);
    this.totalSlides = this.slides.length;
    this.rotationInterval = 3000;
    this.rotationTimer = null;
    this.initSlider(sliderSelector);
    this.startRotation();
  }

  initSlider(sliderSelector) {
    this.showSlide(this.currentSlide);

    document
      .querySelector(`${sliderSelector} .prev-zone`)
      .addEventListener("click", () => this.prevSlide());
    document
      .querySelector(`${sliderSelector} .next-zone`)
      .addEventListener("click", () => this.nextSlide());

    this.createPagination();
    this.updateCounter();

    this.slides.forEach((slide) => {
      slide.addEventListener("click", () => {
        const url = slide.getAttribute("data-url");
        if (url) window.open(url, "_blank");
      });
    });
  }

  showSlide(index) {
    this.slides.forEach((slide, i) => {
      slide.style.display = i === index ? "block" : "none";
    });
    this.updateCounter();
    this.updatePagination();
  }

  nextSlide() {
    this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
    this.showSlide(this.currentSlide);
  }

  prevSlide() {
    this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
    this.showSlide(this.currentSlide);
  }

  createPagination() {
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
    this.counterElement.textContent = `${this.currentSlide + 1} / ${this.totalSlides}`;
  }

  startRotation() {
    this.stopRotation();
    this.rotationTimer = setInterval(() => this.nextSlide(), this.rotationInterval);
  }

  stopRotation() {
    if (this.rotationTimer) {
      clearInterval(this.rotationTimer);
      this.rotationTimer = null;
    }
  }

  updateInterval() {
    const intervalInput = document.getElementById("rotation-interval");
    const newInterval = parseInt(intervalInput.value);
    if (newInterval >= 1000) {
      this.rotationInterval = newInterval;
      this.startRotation();
    } else {
      alert("Интервал должен быть не менее 1000 мс.");
    }
  }
}

// Инициализация слайдера при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  window.slider = new Slider(".photo-slider");
});