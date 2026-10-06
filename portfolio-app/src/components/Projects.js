import React from 'react';
import ProjectCard from './ProjectCard';
import projects from '../data/projects';

export default function Projects() {
  return (
    <section id="projects" aria-labelledby="projects-title">
      <div className="container">
        <h2 id="projects-title" className="mb-4 text-center">Projects</h2>
        <div className="row g-4">
          {projects.map((p) => (
            <div className="col-12 col-md-6 col-lg-4" key={p.id}>
              <ProjectCard title={p.title} image={p.image} link={p.link} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
