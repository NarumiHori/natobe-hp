// Header scroll effect
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 10);
});

// Mobile nav toggle
function toggleNav() {
  const navList = document.getElementById('navList');
  navList.classList.toggle('active');
}

// Close mobile nav on link click
document.querySelectorAll('.nav-list a').forEach(link => {
  link.addEventListener('click', () => {
    document.getElementById('navList').classList.remove('active');
  });
});
