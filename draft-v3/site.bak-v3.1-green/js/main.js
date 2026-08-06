(() => {
  'use strict';

  const menuButton = document.querySelector('.menu-button');
  const menu = document.querySelector('.menu-overlay');
  let lastFocusedElement = null;

  if (menuButton && menu) {
    const menuLinks = Array.from(menu.querySelectorAll('a'));

    const closeMenu = (restoreFocus = true) => {
      menu.classList.remove('is-open');
      menu.setAttribute('aria-hidden', 'true');
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'メニューを開く');
      document.body.classList.remove('menu-open');
      if (restoreFocus && lastFocusedElement) lastFocusedElement.focus();
    };

    const openMenu = () => {
      lastFocusedElement = document.activeElement;
      menu.classList.add('is-open');
      menu.setAttribute('aria-hidden', 'false');
      menuButton.setAttribute('aria-expanded', 'true');
      menuButton.setAttribute('aria-label', 'メニューを閉じる');
      document.body.classList.add('menu-open');
      if (menuLinks[0]) menuLinks[0].focus();
    };

    menuButton.addEventListener('click', () => {
      if (menu.classList.contains('is-open')) closeMenu();
      else openMenu();
    });

    menuLinks.forEach((link) => link.addEventListener('click', () => closeMenu(false)));

    document.addEventListener('keydown', (event) => {
      if (!menu.classList.contains('is-open')) return;
      if (event.key === 'Escape') closeMenu();
      if (event.key === 'Tab') {
        const focusable = [menuButton, ...menuLinks];
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealElements = document.querySelectorAll('.reveal');
  if (reducedMotion || !('IntersectionObserver' in window)) {
    revealElements.forEach((element) => element.classList.add('is-visible'));
  } else {
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          currentObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealElements.forEach((element) => observer.observe(element));
  }
})();
