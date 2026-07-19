// app/contact-page.tsx — Full contact page example using all components
'use client';
import { PageLayout, ScrollReveal, StaggerContainer, HoverLift } from './layout';
import { ContactForm } from './form';
import { MapPin, Mail, Phone } from 'lucide-react';

export default function ContactPage() {
  return (
    <PageLayout hero>
      {/* Hero */}
      <section className="py-[clamp(4rem,10vh,8rem)] text-center">
        <ScrollReveal>
          <h1 className="text-[clamp(2.5rem,6vw,5rem)] font-bold tracking-tight mb-6">
            Let's Talk
          </h1>
          <p className="text-lg text-slate-600 max-w-xl mx-auto leading-relaxed">
            We'd love to hear about your project. Drop us a message and we'll get back within 24 hours.
          </p>
        </ScrollReveal>
      </section>

      {/* Contact cards */}
      <section className="pb-[clamp(3rem,8vh,6rem)]">
        <StaggerContainer stagger={0.12}>
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
            {[{
              icon: Mail,
              label: 'Email',
              value: 'hello@example.com',
            }, {
              icon: Phone,
              label: 'Phone',
              value: '+1 (555) 123-4567',
            }, {
              icon: MapPin,
              label: 'Location',
              value: 'New York, NY',
            }].map((item) => (
              <HoverLift key={item.label} className="bg-white rounded-2xl p-8 shadow-sm border text-center">
                <item.icon className="w-8 h-8 mx-auto mb-4 text-indigo-600" />
                <p className="text-sm text-slate-500 mb-1">{item.label}</p>
                <p className="font-medium">{item.value}</p>
              </HoverLift>
            ))}
          </div>

          {/* Contact form */}
          <ScrollReveal delay={0.3}>
            <div className="max-w-xl mx-auto bg-white rounded-2xl p-8 shadow-sm border">
              <ContactForm />
            </div>
          </ScrollReveal>
        </StaggerContainer>
      </section>
    </PageLayout>
  );
}
