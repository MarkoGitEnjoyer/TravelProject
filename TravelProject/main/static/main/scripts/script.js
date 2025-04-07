const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
const authButtons = document.querySelector('.auth-buttons');


if (hamburger && navLinks && authButtons) {
    hamburger.addEventListener('click', () => {
        
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
        authButtons.classList.toggle('active');
    });
} else {
    console.error("Could not find hamburger menu elements!");
}