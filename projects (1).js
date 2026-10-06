const img = (name) => `${process.env.PUBLIC_URL}/images/${name}`;

const projects = [
  { id: 1, title: 'Task Manager', image: img('project1.svg'), link: 'https://github.com/' },
  { id: 2, title: 'Weather App', image: img('project2.svg'), link: 'https://github.com/' },
  { id: 3, title: 'Landing Page', image: img('project3.svg'), link: 'https://github.com/' },
];

export default projects;
