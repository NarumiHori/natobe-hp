/* NATOBE corporate site — 2026-07 renewal */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Header shadow on scroll ---- */
  var header = document.getElementById('header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---- Mobile nav ---- */
  var toggle = document.querySelector('.hamburger');
  var navList = document.getElementById('navList');
  if (toggle && navList) {
    var setNav = function (open) {
      navList.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    };
    toggle.addEventListener('click', function () {
      setNav(!navList.classList.contains('is-open'));
    });
    navList.addEventListener('click', function (e) {
      if (e.target.closest('a')) setNav(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navList.classList.contains('is-open')) setNav(false);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 768 && navList.classList.contains('is-open')) setNav(false);
    });
  }

  /* ---- Scroll reveal ---- */
  var targets = document.querySelectorAll('.reveal');
  if (targets.length) {
    if (reduceMotion || !('IntersectionObserver' in window)) {
      Array.prototype.forEach.call(targets, function (el) { el.classList.add('is-in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      Array.prototype.forEach.call(targets, function (el, i) {
        el.style.transitionDelay = Math.min(i % 4, 3) * 70 + 'ms';
        io.observe(el);
      });
    }
  }

  /* ---- Count-up for hero stats ---- */
  var nums = document.querySelectorAll('[data-count]');
  if (nums.length && !reduceMotion && 'IntersectionObserver' in window) {
    var countIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        countIO.unobserve(el);
        var target = parseFloat(el.getAttribute('data-count'));
        if (isNaN(target)) return;
        var decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
        var start = null;
        var dur = 1100;
        var tick = function (now) {
          if (start === null) start = now;
          var p = Math.min((now - start) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = (target * eased).toFixed(decimals)
            .replace(/\B(?=(\d{3})+(?!\d))/g, ',');
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.4 });
    Array.prototype.forEach.call(nums, function (el) { countIO.observe(el); });
  }

  /* ---- Sticky mobile CTA (appears once the hero is scrolled past) ---- */
  var sticky = document.querySelector('.sticky-cta');
  if (sticky) {
    document.body.classList.add('has-sticky-cta');
    var anchor = document.querySelector('.hero, .page-hero');
    if (anchor && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        sticky.classList.toggle('is-visible', !entries[0].isIntersecting);
      }, { threshold: 0 }).observe(anchor);
    } else {
      sticky.classList.add('is-visible');
    }
  }

  /* ---- Current year in footer ---- */
  var years = document.querySelectorAll('[data-year]');
  if (years.length) {
    var y = String(new Date().getFullYear());
    Array.prototype.forEach.call(years, function (el) { el.textContent = y; });
  }
})();
