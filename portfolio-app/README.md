# Responsive Personal Portfolio with Contact Form

Single-page portfolio built with **React 18 + Bootstrap 5**. Sections: Hero, About (bio + skills), Projects gallery (3 cards), and a validated Contact form that POSTs to a mock REST API.

## Features
- Responsive from 320px up (Bootstrap grid, collapsing navbar)
- React Router (HashRouter) with smooth scroll to sections
- Reusable `ProjectCard` component, data-driven from `src/data/projects.js`
- Controlled contact form with client-side validation (required fields + email format)
- Success message / error alert based on API result
- ARIA labels, semantic HTML, SEO meta tags in `public/index.html`
- Jest unit tests for validation logic

## Setup
```bash
npm install
npm start            # http://localhost:3000
npm test             # run Jest in watch mode
npm run test:coverage
npm run build
```

## Deployment (GitHub Pages)
1. Create a GitHub repo and push this project.
2. Run `npm run deploy` (builds, publishes `build/` to the `gh-pages` branch).
3. In repo Settings > Pages, set source to the `gh-pages` branch.
`HashRouter` and `"homepage": "."` make routing work without extra server config.

## Mock API
- Endpoint: `POST https://jsonplaceholder.typicode.com/posts`
- Body: `{ "title": <name>, "email": <email>, "body": <message> }`
- Success: HTTP 201 with the echoed payload and an `id` -> thank-you message
- Failure (network error or non-2xx) -> error alert

## Structure
```
src/
  components/  Navbar, Hero, About, Projects, ProjectCard, ContactForm
  data/        projects.js
  services/    api.js
  utils/       validation.js, validation.test.js
```

## Customizing
Edit your bio in `About.js`, skills list there, and project entries/links in `src/data/projects.js`.

## Suggested commit history
`chore: init CRA` > `feat: layout and navbar` > `feat: about and hero` > `feat: project cards` > `feat: contact form + validation` > `test: validation unit tests` > `docs: README + deploy`
