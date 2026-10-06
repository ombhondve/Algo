import React, { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import About from './components/About';
import Projects from './components/Projects';
import ContactForm from './components/ContactForm';

const sectionFor = (pathname) => (pathname === '/' ? 'home' : pathname.replace('/', ''));

function Home() {
  const { pathname } = useLocation();

  // Route changes smooth-scroll to the matching section.
  useEffect(() => {
    document.getElementById(sectionFor(pathname))?.scrollIntoView({ behavior: 'smooth' });
  }, [pathname]);

  return (
    <main>
      <Hero />
      <About />
      <Projects />
      <ContactForm />
    </main>
  );
}

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/*" element={<Home />} />
      </Routes>
      <footer className="bg-dark text-light text-center py-3">
        <small>&copy; {new Date().getFullYear()} Sanskar Ravindra Bhondve</small>
      </footer>
    </>
  );
}
