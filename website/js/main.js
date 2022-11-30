import { initConfig } from "./config.js";
import { initSite } from "./landing.js";
import { initPractice } from "./practice.js";

initSite();
initConfig();
initPractice();

let vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);
window.addEventListener('resize', () => {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  });