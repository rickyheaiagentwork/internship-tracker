// animations.js — Complete setup with Lenis + GSAP ScrollTrigger
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);

// === Lenis: Smooth scroll ===
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  orientation: 'vertical',
  smoothWheel: true,
});

function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

// === GSAP + Lenis sync ===
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});
gsap.ticker.lagSmoothing(0);

// === Common animation patterns ===

// 1. Fade-in reveal on scroll
gsap.utils.toArray('.reveal-on-scroll').forEach((el) => {
  gsap.from(el, {
    scrollTrigger: {
      trigger: el,
      start: 'top 85%',
      end: 'top 60%',
      toggleActions: 'play none none reverse',
    },
    y: 40,
    opacity: 0,
    duration: 1,
    ease: 'power3.out',
  });
});

// 2. Parallax background
gsap.utils.toArray('.parallax-bg').forEach((el) => {
  gsap.to(el, {
    scrollTrigger: {
      trigger: el.parentElement,
      start: 'top bottom',
      end: 'bottom top',
      scrub: true,
    },
    y: -200,
    ease: 'none',
  });
});

// 3. Text character stagger reveal
gsap.utils.toArray('.stagger-text').forEach((el) => {
  const chars = el.textContent.split('');
  el.innerHTML = chars.map(c => `<span>${c === ' ' ? '\u00A0' : c}</span>`).join('');
  
  gsap.from(el.querySelectorAll('span'), {
    scrollTrigger: {
      trigger: el,
      start: 'top 75%',
      toggleActions: 'play none none reverse',
    },
    y: 80,
    opacity: 0,
    stagger: 0.04,
    duration: 0.6,
    ease: 'power3.out',
  });
});

export { lenis, ScrollTrigger };
