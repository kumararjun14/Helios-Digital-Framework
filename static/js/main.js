if (window.gsap && window.ScrollTrigger) {
  gsap.registerPlugin(ScrollTrigger);
  const menu = document.getElementById('menu'),
    links = document.getElementById('navLinks');
  if (menu) {
    menu.onclick = () => (links.classList.toggle('open'), menu.setAttribute('aria-expanded', links.classList.contains('open')))
  }
  window.addEventListener('scroll', () => document.getElementById('nav').style.background = scrollY > 40 ? 'rgba(7,18,13,.93)' : 'rgba(7,18,13,.76)');
  gsap.from('.hero-copy > *', {
    y: 60,
    opacity: 0,
    duration: 1,
    stagger: .12,
    ease: 'power3.out'
  });
  gsap.from('.lead-card', {
    y: 60,
    opacity: 0,
    duration: 1,
    delay: .25,
    ease: 'power3.out'
  });
  gsap.utils.toArray('.reveal').forEach(el => {
    gsap.from(el, {
      scrollTrigger: {
        trigger: el,
        start: 'top 82%'
      },
      y: 55,
      opacity: 0,
      duration: .9,
      ease: 'power3.out'
    })
  });
  gsap.utils.toArray('[data-count]').forEach(el => {
    let end = +el.dataset.count;
    gsap.to(el, {
      scrollTrigger: {
        trigger: el,
        start: 'top 88%'
      },
      innerText: end,
      duration: 1.4,
      snap: {
        innerText: 1
      },
      ease: 'power2.out'
    })
  });
  const glow = document.querySelector('.cursor-glow');
  window.addEventListener('mousemove', e => {
    if (glow) {
      glow.style.left = e.clientX + 'px';
      glow.style.top = e.clientY + 'px'
    }
  });

}
