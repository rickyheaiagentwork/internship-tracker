// app/hero-section.tsx
'use client';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export function HeroSection({ title, subtitle, ctaText = 'Get Started', ctaHref = '#contact' }: {
  title: string;
  subtitle: string;
  ctaText?: string;
  ctaHref?: string;
}) {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-indigo-50/30 to-white" />

      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
        {/* Animated title with letter split */}
        <motion.h1
          initial={{ opacity: 0, y: 80 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="text-[clamp(2.5rem, 7vw, 6rem)] font-bold tracking-tight leading-[1.05]"
        >
          {title}
        </motion.h1>

        {/* Subtitle with stagger */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-8 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed"
        >
          {subtitle}
        </motion.p>

        {/* CTA button with hover animation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="mt-12"
        >
          <a
            href={ctaHref}
            className="inline-flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg active:scale-[0.98]"
          >
            {ctaText}
            <ArrowRight className="w-5 h-5" />
          </a>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 12, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute bottom-12 left-1/2 -translate-x-1/2"
        >
          <div className="w-6 h-10 border-2 border-slate-300 rounded-full flex justify-center">
            <motion.div
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
              className="w-1 h-3 bg-slate-400 rounded-full mt-2"
            />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
