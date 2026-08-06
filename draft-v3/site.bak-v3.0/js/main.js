(() => {
  'use strict';

  const menuButton = document.querySelector('.menu-button');
  const menu = document.querySelector('.menu-overlay');
  const siteHeader = document.querySelector('.site-header');
  const hero = document.querySelector('.hero, .page-hero');
  let lastFocusedElement = null;

  if (siteHeader && hero) {
    let frameRequested = false;

    const updateHeader = () => {
      const threshold = hero.offsetTop + (hero.offsetHeight * 0.8);
      siteHeader.classList.toggle('is-over-hero', window.scrollY <= threshold);
      frameRequested = false;
    };

    const requestHeaderUpdate = () => {
      if (frameRequested) return;
      frameRequested = true;
      window.requestAnimationFrame(updateHeader);
    };

    updateHeader();
    window.requestAnimationFrame(() => siteHeader.classList.add('is-state-ready'));
    window.addEventListener('scroll', requestHeaderUpdate, { passive: true });
    window.addEventListener('resize', requestHeaderUpdate, { passive: true });
  }

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
