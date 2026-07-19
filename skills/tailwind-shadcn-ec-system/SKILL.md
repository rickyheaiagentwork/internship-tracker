---
name: "tailwind-shadcn-ec-system"
description: "Tailwind CSS + shadcn/ui professional website stack for ETERNITY — free, Vercel-ready"
---

# Tailwind + shadcn/ui + Eternity Creative System (EC)

## When to use
Eternity is building any regular website (not just portfolios): landing pages, SaaS sites, agency sites, tool/product pages, multi-page marketing sites. This covers the styling/component/animation/form layers for professional results.

## Installation (all free/open-source)
```bash
# Tailwind CSS + shadcn/ui — the core stack
npm create @shadcn@latest     # interactive setup: pick Tailwind v4 or v3, dark mode, etc.

# Framer Motion (React animations)
npm install framer-motion

# React Hook Form + Zod (form validation)
npm install react-hook-form zod @hookform/resolvers

# Lucide Icons
npm install lucide-react

# Lenis (smooth scroll — if needed on the page)
npm install lenis

# GSAP + ScrollTrigger (scroll animations)
npm install gsap
```

## Setup File 1: styles/globals.css or app/globals.css
```css
/* Base Tailwind config via shadcn setup */
@import "tailwindcss";

/* Custom design tokens — change these to rebrand entire site */
@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: 'Inter', ui-sans-serif, system-ui;
  --font-mono: 'JetBrains Mono', monospace;
  --radius-sm: clamp(0.25rem, 0.4vw, 0.5rem);
  --radius-md: clamp(0.5rem, 0.8vw, 1rem);
  --radius-lg: clamp(1rem, 1.5vw, 1.5rem);

  /* Eternity color palette — change accent to rebrand */
  --color-accent-400: #6366f1;   /* indigo primary accent */
  --color-accent-500: #818cf8;
  --color-neutral-100: #f8fafc;
  --color-neutral-900: #0f172a;
}

/* Smooth scroll base */
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto; }
.lenis.lenis-smooth * { scroll-behavior: auto; }
```

## Setup File 2: app/animations.ts (Framer Motion components)
```tsx
'use client';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';

// === Reusable animated containers for Eternity to drop into any page ===

// Fade-in on scroll (use wherever elements should appear)
export function ScrollReveal({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6, delay, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

// Staggered children (for lists, grids)
export function StaggerContainer({ children, stagger = 0.08 }: { children: React.ReactNode; stagger?: number }) {
  const container = useRef(null);
  return (
    <motion.div ref={container} initial="hidden" whileInView="visible" viewport={{ once: true }}>
      {React.Children.map(children, (child, i) => (
        <motion.div
          variants={{
            hidden: { opacity: 0, y: 30 },
            visible: { opacity: 1, y: 0, transition: { delay: i * stagger, duration: 0.5 } },
          }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
}

// Parallax section wrapper
export function ParallaxSection({ children }: { children: React.ReactNode }) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [-80, 80]);
  return (
    <div ref={ref}>
      <motion.div style={{ y }}>{children}</motion.div>
    </div>
  );
}

// Hover lift effect for cards
export function HoverLift({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div
      whileHover={{ y: -8, transition: { duration: 0.2 } }}
      whileTap={{ scale: 0.98 }}
      className={`transition-shadow hover:shadow-lg ${className}`}
    >
      {children}
    </motion.div>
  );
}

// Text split animation (for hero headings)
export function SplitText({ text, className = "" }: { text: string; className?: string }) {
  const words = text.split(' ');
  return (
    <h1 className={className}>
      {words.map((word, i) => (
        <span key={i} className="inline-block mr-2">
          {word.split('').map((char, j) => (
            <motion.span
              key={`${i}-${j}`}
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: (i * 0.1) + (j * 0.03), duration: 0.4 }}
            >
              {char}
            </motion.span>
          ))}
        </span>
      ))}
    </h1>
  );
}
```

## Setup File 3: app/form.tsx (React Hook Form + Zod)
```tsx
'use client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Reusable validated form for any website contact/inquiry form
const formSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
});

type FormInput = z.infer<typeof formSchema>;

export function ContactForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormInput>({
    resolver: zodResolver(formSchema),
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log('Submitted:', data))} className="space-y-6">
      <div>
        <label className="block text-sm font-medium mb-2">Name</label>
        <input {...register('name')} className="w-full px-4 py-3 rounded-lg border bg-transparent" />
        {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2">Email</label>
        <input {...register('email')} type="email" className="w-full px-4 py-3 rounded-lg border bg-transparent" />
        {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2">Message</label>
        <textarea {...register('message')} rows={5} className="w-full px-4 py-3 rounded-lg border bg-transparent" />
        {errors.message && <p className="text-red-500 text-sm mt-1">{errors.message.message}</p>}
      </div>
      <button type="submit" className="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
        Send Message
      </button>
    </form>
  );
}
```

## Usage Patterns Eternity Follows

### Layout structure (every page)
```tsx
// Consistent layout pattern across all pages
export function PageLayout({ children, hero }: { children: React.ReactNode; hero?: boolean }) {
  return (
    <main className={`min-h-screen ${hero ? 'relative overflow-hidden' : ''}`}>
      {/* Hero gradient background */}
      {hero && (
        <div className="absolute inset-0 bg-gradient-to-b from-indigo-50 to-white pointer-events-none" />
      )}

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Fluid spacing — 8px base grid, clamped for responsive */}
        <section className="py-[clamp(3rem, 8vh, 8rem)]">
          {children}
        </section>
      </div>
    </main>
  );
}

// Usage:
<PageLayout hero>
  <ScrollReveal>
    <SplitText text="We build things that matter." />
  </ScrollReveal>

  <StaggerContainer stagger={0.1}>
    <HoverLift className="bg-white rounded-2xl p-8 shadow-sm border">
      {/* Card content */}
    </HoverLift>
  </StaggerContainer>
</PageLayout>
```

### Typography scale (use consistently)
| Level | Size (Tailwind) | Use Case |
|-------|----------------|----------|
| Hero heading | `text-[clamp(2.5rem, 6vw, 6rem)]` | Page hero titles — massive contrast |
| Section heading | `text-[clamp(1.8rem, 4vw, 3.5rem)]` | Section dividers, feature headers |
| Body large | `text-lg leading-relaxed` | Paragraph text, 1.6-1.7 line height |
| Body regular | `text-base leading-normal` | Normal paragraphs |
| Caption/small | `text-sm text-muted-foreground` | Labels, disclaimers |

### Design principles for Eternity
1. **One accent color max** — indigo/purple/violet/amber works best on white/black backgrounds. Never more than one primary hue.
2. **Double the whitespace** — if padding feels right at 4rem, make it 6-8rem. Empty space = perceived quality.
3. **Fluid sizing everywhere** — use `clamp()` for font sizes, padding, margins. Never fixed px on anything > sm breakpoint.
4. **Dark mode support** — shadcn sets up CSS variables for dark/light automatically. Use `dark:` variants.
5. **Consistent border radius** — pick ONE value (or small set) and use it everywhere. No mix-matching rounded corners.
6. **Micro-interactions on every interactive element** — buttons scale down on click, cards lift on hover, inputs have focus ring.

### Vercel deployment notes
- All deps are standard npm packages — zero special setup needed
- Tailwind config goes in `tailwind.config.ts` (auto-generated by shadcn)
- Use `@shadcn/ui` for component library — it copies components into your project (not a dependency lock-in)
- Deploy to Vercel: `vercel deploy --prod` or push to connected Git repo
- Image optimization: use Next.js `next/image` for all web images (auto WebP/AVIF conversion on Vercel)

## What to skip (don't add these)
- Bootstrap, Bulma, Semantic UI — outdated patterns, template feel
- Material-UI, Ant Design — too opinionated, looks like "enterprise software" not custom sites
- Full component libraries you don't need — copy only what you use from shadcn/ui
