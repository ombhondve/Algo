import React from 'react';

const skills = ['HTML', 'CSS', 'Bootstrap 5', 'React', 'REST APIs', 'Git', 'Responsive Design'];

export default function About() {
  return (
    <section id="about" className="bg-soft" aria-labelledby="about-title">
      <div className="container">
        <h2 id="about-title" className="mb-4 text-center">About Me</h2>
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <p className="fs-5">
              I'm a junior frontend developer who enjoys turning designs into clean, responsive interfaces.
              I work with HTML, CSS, Bootstrap 5 and React, and I care about performance, accessibility and
              maintainable code.
            </p>
            <h3 className="h5 mt-4">Skills</h3>
            <ul className="list-unstyled d-flex flex-wrap gap-2" aria-label="Skills list">
              {skills.map((s) => (
                <li key={s}><span className="badge bg-primary skill-badge">{s}</span></li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
