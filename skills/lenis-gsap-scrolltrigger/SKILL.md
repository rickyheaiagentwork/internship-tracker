---
name: "lenis-gsap-scrolltrigger"
description: "Scroll animations skill — Lenis + GSAP patterns. Pull engine, own patterns. 7 reusable React components for professional scroll effects."
---

# Lenis + GSAP ScrollTrigger Skill (for ETERNITY)

## Philosophy: Pull the engine, own the patterns
- **Pull:** Lenis (~6kb smooth scroll), GSAP core (~13kb animation engine)
- **Own:** All animation presets as reusable React components — our code, no config headaches

## Installation
```bash
npm install lenis gsap
```

## Setup: src/lib/scroll.ts (our glue code)
```typescript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);

const lenis = new Lenis({ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });

function raf(time: number) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);

lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => { lenis.raf(time * 1000); });
gsap.ticker.lagSmoothing(0);

export { lenis, gsap, ScrollTrigger };
```

## Reusable Animation Components (src/components/ScrollAnimations.tsx)

### 1. Reveal — fade-up on scroll
```tsx
export function Reveal({ children, className = '', delay = 0 }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    gsap.fromTo(ref.current, { opacity: 0, y: 40 },
      { opacity: 1, y: 0, duration: 0.7, delay, ease: 'power3.out',
        scrollTrigger: { trigger: ref.current, start: 'top 85%', toggleActions: 'play none none reverse' } });
  }, []);
  return <div ref={ref} className={className}>{children}</div>;
}
```

### 2. Stagger — staggered children reveal
```tsx
export function Stagger({ children, className = '', stagger = 0.1 }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    for (let i = 0; i < ref.current.children.length; i++) {
      gsap.fromTo(ref.current.children[i], { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.5, delay: i * stagger, ease: 'power3.out',
          scrollTrigger: { trigger: ref.current, start: 'top 80%', toggleActions: 'play none none reverse' } });
    }
  }, []);
  return <div ref={ref} className={className}>{children}</div>;
}
```

### 3. Parallax — slower-than-scroll movement
```tsx
export function Parallax({ children, factor = 0.3, className = '' }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    gsap.to(ref.current, { y: () => -(ref.current.offsetHeight * factor), ease: 'none',
      scrollTrigger: { trigger: ref.current.parentElement!, start: 'top bottom', end: 'bottom top', scrub: true } });
  }, [factor]);
  return <div ref={ref} className={className}>{children}</div>;
}
```

### 4. SplitText — letter-by-letter hero title reveal
```tsx
export function SplitText({ text, className = '', speed = 0.04 }) {
  const words = text.split(' ');
  return (
    <h1 className={className}>
      {words.map((word, wi) => (
        <span key={wi} className="inline-block mr-2">
          {word.split('').map((char, ci) => (
            <span key={`${wi}-${ci}`}>{char === ' ' ? '\u00A0' : char}</span>
          ))}
        </span>
      ))}
    </h1>
  );
}
```

### 5. ScaleReveal — grow into view
```tsx
export function ScaleReveal({ children, className = '', scale = 0.9 }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    gsap.fromTo(ref.current, { opacity: 0, scale },
      { opacity: 1, scale: 1, duration: 0.8, ease: 'power3.out',
        scrollTrigger: { trigger: ref.current, start: 'top 85%', toggleActions: 'play none none reverse' } });
  }, []);
  return <div ref={ref} className={className}>{children}</div>;
}
```

### 6. HorizontalGallery — pin-and-scroll gallery
```tsx
export function HorizontalGallery({ items }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    gsap.to(ref.current.children, { xPercent: -100 * (ref.current.children.length - 1), ease: 'none',
      scrollTrigger: { trigger: ref.current.parentElement!, pin: true, scrub: 1 } });
  }, [items]);
  return <div ref={ref} className="flex gap-6">{items.map((item, i) => <div key={i} className="shrink-0 w-[85vw] sm:w-[30rem]">{item}</div>)}</div>;
}
```

### 7. Sequence — multi-element scroll timeline
```tsx
export function Sequence({ children }) {
  const tlRef = useRef(null);
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    tlRef.current = gsap.timeline({ scrollTrigger: { trigger: ref.current, start: 'top 60%', end: 'bottom 40%', scrub: true } });
  }, []);
  // Eternity adds to timeline via tlRef.current.to(el, props)
  return <div ref={ref}>{children}</div>;
}
```

## Usage
```tsx
<Reveal><h2>Section Title</h2></Reveal>
<Stagger stagger={0.12}>{cards.map(card => <Card key={card.title} {...card} />)}</Stagger>
<Parallax factor={0.4}><img src="/bg.jpg" className="h-[120vh]" /></Parallax>
<SplitText text="We build things that matter." className="text-6xl font-bold" />
```

## Key Principles
1. All animations respect `prefers-reduced-motion` — GSAP handles this automatically
2. Clean up on unmount: `useEffect(() => () => ScrollTrigger.getAll().forEach(st => st.kill()), [])`
3. Call `ScrollTrigger.refresh()` after dynamic content loads
4. Pick 2-3 patterns and apply consistently across the site
5. Don't animate everything — strategic motion beats constant motion

## Skip for
- Static pages with no scroll content
- Mobile-first apps where performance > polish
- Dashboards/tools where visual flair < function
