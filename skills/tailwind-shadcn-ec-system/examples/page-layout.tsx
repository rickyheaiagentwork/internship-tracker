// app/page-layout.tsx — Consistent page layout for all pages
import { ScrollReveal, StaggerContainer, HoverLift } from './animations';
import type { ReactNode } from 'react';

interface PageLayoutProps {
  children: ReactNode;
  hero?: boolean;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '7xl';
}

const maxWidthMap = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '7xl': 'max-w-7xl',
};

export function PageLayout({ children, hero = false, maxWidth = '7xl' }: PageLayoutProps) {
  return (
    <main className={`min-h-screen ${hero ? 'relative overflow-hidden' : ''}`}>
      {/* Optional hero gradient */}
      {hero && (
        <div className="absolute inset-0 bg-gradient-to-b from-indigo-50/60 to-transparent pointer-events-none" />
      )}

      <div className={`relative ${maxWidthMap[maxWidth]} mx-auto px-4 sm:px-6 lg:px-8`}>
        {children}
      </div>
    </main>
  );
}

// Export utility hooks for Eternity to use freely
export { ScrollReveal, StaggerContainer, HoverLift };
