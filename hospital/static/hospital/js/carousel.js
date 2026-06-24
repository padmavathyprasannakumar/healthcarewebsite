(function(){
  const carousel = document.querySelector('[data-carousel]');
  if(!carousel) return;
  const slides = Array.from(carousel.querySelectorAll('.hero-slide'));
  const nextBtn = carousel.querySelector('[data-next]');
  const prevBtn = carousel.querySelector('[data-prev]');
  let index = 0;
  function show(i){
    slides[index].classList.remove('active');
    index = (i + slides.length) % slides.length;
    slides[index].classList.add('active');
  }
  if(nextBtn) nextBtn.addEventListener('click', () => show(index + 1));
  if(prevBtn) prevBtn.addEventListener('click', () => show(index - 1));
  if(slides.length > 1){ setInterval(() => show(index + 1), 5000); }
})();
