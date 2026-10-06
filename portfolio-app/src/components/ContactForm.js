import React, { useState } from 'react';
import { validateContact } from '../utils/validation';
import { sendMessage } from '../services/api';

const initial = { name: '', email: '', message: '' };

export default function ContactForm() {
  const [values, setValues] = useState(initial);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState('idle'); // idle | sending | success | error

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues((v) => ({ ...v, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const found = validateContact(values);
    setErrors(found);
    if (Object.keys(found).length) return;

    setStatus('sending');
    try {
      await sendMessage(values);
      setStatus('success');
      setValues(initial);
    } catch (err) {
      setStatus('error');
    }
  };

  const field = (id, label, props = {}) => (
    <div className="mb-3">
      <label htmlFor={id} className="form-label">{label}</label>
      {props.as === 'textarea' ? (
        <textarea id={id} name={id} rows="5" value={values[id]} onChange={handleChange}
          className={`form-control ${errors[id] ? 'is-invalid' : ''}`}
          aria-required="true" aria-invalid={!!errors[id]} aria-describedby={`${id}-error`} />
      ) : (
        <input id={id} name={id} type={props.type || 'text'} value={values[id]} onChange={handleChange}
          className={`form-control ${errors[id] ? 'is-invalid' : ''}`}
          aria-required="true" aria-invalid={!!errors[id]} aria-describedby={`${id}-error`} />
      )}
      <div id={`${id}-error`} className="invalid-feedback">{errors[id]}</div>
    </div>
  );

  return (
    <section id="contact" className="bg-soft" aria-labelledby="contact-title">
      <div className="container">
        <h2 id="contact-title" className="mb-4 text-center">Contact Me</h2>
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-6">
            {status === 'success' && (
              <div className="alert alert-success" role="status">Thank you! Your message has been sent.</div>
            )}
            {status === 'error' && (
              <div className="alert alert-danger" role="alert">Something went wrong. Please try again.</div>
            )}
            <form onSubmit={handleSubmit} noValidate aria-label="Contact form">
              {field('name', 'Name')}
              {field('email', 'Email', { type: 'email' })}
              {field('message', 'Message', { as: 'textarea' })}
              <button type="submit" className="btn btn-primary w-100" disabled={status === 'sending'}>
                {status === 'sending' ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
