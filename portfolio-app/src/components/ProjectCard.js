import React from 'react';
import PropTypes from 'prop-types';

export default function ProjectCard({ title, image, link }) {
  return (
    <div className="card h-100 project-card">
      <img src={image} className="card-img-top" alt={`${title} preview`} loading="lazy" />
      <div className="card-body d-flex flex-column">
        <h3 className="card-title h5">{title}</h3>
        <a href={link} className="btn btn-primary mt-auto" target="_blank" rel="noopener noreferrer"
           aria-label={`View ${title} project`}>
          View Project
        </a>
      </div>
    </div>
  );
}

ProjectCard.propTypes = {
  title: PropTypes.string.isRequired,
  image: PropTypes.string.isRequired,
  link: PropTypes.string.isRequired,
};
