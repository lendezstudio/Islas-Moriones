/* Islas Moriones Beach Resort: brochure interactions.
   Progressive enhancement: every section is readable and every link works without this file. */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduceMotion = function () { return reduceMotionQuery.matches; };
  var $ = function (sel, ctx) { return (ctx || doc).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); };

  root.classList.add('js-anim');

  function safe(fn) { try { fn(); } catch (err) { if (window.console) console.error(err); } }

  // Horizontal swipe on touch screens: onDir(+1) next, onDir(-1) previous.
  function onSwipe(el, onDir, onActive) {
    var sx = null, sy = 0;
    el.addEventListener('touchstart', function (e) {
      if (e.touches.length !== 1) { sx = null; return; }
      sx = e.touches[0].clientX; sy = e.touches[0].clientY;
      if (onActive) onActive(true);
    }, { passive: true });
    el.addEventListener('touchend', function (e) {
      if (sx === null) return;
      var t = e.changedTouches[0];
      var dx = t.clientX - sx, dy = t.clientY - sy;
      sx = null;
      if (onActive) onActive(false);
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) onDir(dx < 0 ? 1 : -1);
    }, { passive: true });
    el.addEventListener('touchcancel', function () { sx = null; if (onActive) onActive(false); }, { passive: true });
  }

  /* ---------- Header, current section, contents menu ---------- */
  function initHeader() {
    var header = $('.site-header');
    var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 24); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    var links = $$('.primary-nav a').filter(function (a) { return a.getAttribute('href').charAt(0) === '#'; });
    if (links.length && 'IntersectionObserver' in window) {
      var map = {};
      links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          links.forEach(function (a) { a.classList.remove('is-current'); a.removeAttribute('aria-current'); });
          var link = map[e.target.id];
          if (link) { link.classList.add('is-current'); link.setAttribute('aria-current', 'true'); }
        });
      }, { rootMargin: '-45% 0px -50% 0px' });
      $$('main > section[id]').forEach(function (s) { io.observe(s); });
    }

    var toggle = $('.menu-toggle');
    var menu = $('#mobile-menu');
    var label = $('.menu-toggle__label', toggle);
    var outside = [$('main'), $('.site-footer'), $('.mobile-cta')];
    var closeTimer;
    function setOpen(open) {
      clearTimeout(closeTimer);
      toggle.setAttribute('aria-expanded', String(open));
      label.textContent = open ? 'Close' : 'Menu';
      doc.body.classList.toggle('menu-open', open);
      outside.forEach(function (el) { if (el) el.inert = open; });
      if (open) {
        menu.hidden = false;
        requestAnimationFrame(function () { requestAnimationFrame(function () { menu.classList.add('is-open'); }); });
        var first = $('a', menu);
        if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 60);
      } else {
        menu.classList.remove('is-open');
        closeTimer = setTimeout(function () { menu.hidden = true; }, reduceMotion() ? 0 : 600);
      }
    }
    toggle.addEventListener('click', function () { setOpen(toggle.getAttribute('aria-expanded') !== 'true'); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { setOpen(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', function (m) { if (m.matches) setOpen(false); });
  }

  /* ---------- Cover slideshow ---------- */
  function initCarousel() {
    var media = $('.carousel');
    var slides = $$('.slide', media);
    var controls = $('.carousel-controls', media);
    if (!media || slides.length < 2) return;

    var btnPrev = $('[data-prev]', controls);
    var btnNext = $('[data-next]', controls);
    var btnToggle = $('[data-toggle]', controls);
    var buttonsEl = $('.carousel-controls__buttons', controls);
    var elCurrent = $('[data-current]', controls);
    var elTotal = $('[data-total]', controls);
    var elCaption = $('[data-caption]', controls);
    var captionWrap = $('.carousel-controls__caption', controls);
    var bar = $('.carousel-controls__progress span', media);

    var DURATION = 6500;
    var index = 0, elapsed = 0, last = null;
    var userPaused = reduceMotion();
    var holds = {};
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    elTotal.textContent = pad(slides.length);

    function isPlaying() { return !userPaused && Object.keys(holds).length === 0; }
    function hold(key, on) { if (on) holds[key] = true; else delete holds[key]; }
    function syncToggle() {
      btnToggle.setAttribute('aria-pressed', String(userPaused));
      btnToggle.setAttribute('aria-label', userPaused ? 'Play slideshow' : 'Pause slideshow');
      captionWrap.setAttribute('aria-live', userPaused ? 'polite' : 'off');
    }

    function go(next) {
      next = (next + slides.length) % slides.length;
      if (next === index) return;
      var prev = slides[index], cur = slides[next];
      var img = $('img', cur);
      if (img && img.loading === 'lazy') img.loading = 'eager';
      prev.classList.remove('is-active'); prev.setAttribute('aria-hidden', 'true');
      cur.classList.add('is-active'); cur.removeAttribute('aria-hidden');
      index = next; elapsed = 0;
      bar.style.transform = 'scaleX(0)';
      elCurrent.textContent = pad(index + 1);
      var text = $('figcaption', cur).textContent;
      if (reduceMotion()) elCaption.textContent = text;
      else {
        elCaption.classList.add('is-swapping');
        setTimeout(function () { elCaption.textContent = text; elCaption.classList.remove('is-swapping'); }, 240);
      }
      var after = $('img', slides[(index + 1) % slides.length]);
      if (after && after.loading === 'lazy') after.loading = 'eager';
    }

    function tick(t) {
      if (last === null) last = t;
      var dt = t - last; last = t;
      if (isPlaying()) {
        elapsed += dt;
        bar.style.transform = 'scaleX(' + Math.min(elapsed / DURATION, 1) + ')';
        if (elapsed >= DURATION) go(index + 1);
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);

    btnPrev.addEventListener('click', function () { go(index - 1); });
    btnNext.addEventListener('click', function () { go(index + 1); });
    btnToggle.addEventListener('click', function () { userPaused = !userPaused; syncToggle(); });

    // Only hovering the buttons and keyboard focus pause autoplay; tapping or hovering the photo does not.
    buttonsEl.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hold('hover', true); });
    buttonsEl.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') hold('hover', false); });
    media.addEventListener('focusin', function (e) {
      var kb = false;
      try { kb = e.target.matches(':focus-visible'); } catch (err) { kb = false; }
      hold('focus', kb);
    });
    media.addEventListener('focusout', function () { hold('focus', false); });
    media.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); }
    });

    // Controls appear on tap or mouse movement, then hide 3 seconds after the last interaction.
    var hideTimer;
    function revealControls() {
      controls.classList.add('is-visible');
      clearTimeout(hideTimer);
      hideTimer = setTimeout(function () { controls.classList.remove('is-visible'); hold('hover', false); }, 3000);
    }
    media.addEventListener('click', revealControls);
    media.addEventListener('pointermove', function (e) { if (e.pointerType === 'mouse') revealControls(); });
    media.addEventListener('touchend', revealControls, { passive: true });

    onSwipe(media, function (dir) { go(index + dir); }, function (active) {
      if (active) hold('touch', true); else setTimeout(function () { hold('touch', false); }, 1200);
    });

    doc.addEventListener('visibilitychange', function () { hold('tab', doc.hidden); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { hold('offscreen', !entries[0].isIntersecting); }, { threshold: 0.2 }).observe(media);
    }
    reduceMotionQuery.addEventListener('change', function () { if (reduceMotion()) { userPaused = true; syncToggle(); } });
    syncToggle();
  }

  /* ---------- Scroll reveals ---------- */
  function initReveals() {
    var items = $$('[data-reveal]');
    if (!('IntersectionObserver' in window)) { items.forEach(function (el) { el.classList.add('is-in'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
    // Stagger items that sit side by side in a grid.
    $$('.rooms, .stops, .boats__grid, .other-stays__grid, .packages__grid').forEach(function (grid) {
      $$('[data-reveal]', grid).forEach(function (el, i) { el.style.transitionDelay = (i % 3) * 0.08 + 's'; });
    });
  }

  /* ---------- Tabs (menu, routes) ---------- */
  function initTabs() {
    $$('[role="tablist"]').forEach(function (list) {
      var tabs = $$('[role="tab"]', list);
      function select(tab, focus) {
        tabs.forEach(function (t) {
          var on = t === tab;
          t.setAttribute('aria-selected', String(on));
          t.tabIndex = on ? 0 : -1;
          doc.getElementById(t.getAttribute('aria-controls')).hidden = !on;
        });
        if (focus) tab.focus();
      }
      tabs.forEach(function (tab, i) {
        tab.addEventListener('click', function () { select(tab, false); });
        tab.addEventListener('keydown', function (e) {
          var n = null;
          if (e.key === 'ArrowRight') n = (i + 1) % tabs.length;
          else if (e.key === 'ArrowLeft') n = (i - 1 + tabs.length) % tabs.length;
          else if (e.key === 'Home') n = 0;
          else if (e.key === 'End') n = tabs.length - 1;
          if (n !== null) { e.preventDefault(); select(tabs[n], true); }
        });
      });
    });
  }

  /* ---------- Gallery filter + lightbox ---------- */
  function filterItems(items, show) {
    var hiding = items.filter(function (el) { return !show(el) && !el.hidden; });
    var showing = items.filter(show);
    var delay = reduceMotion() ? 0 : 300;
    hiding.forEach(function (el) { el.classList.add('is-hiding'); });
    setTimeout(function () {
      hiding.forEach(function (el) { el.hidden = true; el.classList.remove('is-hiding'); });
      showing.forEach(function (el) { if (el.hidden) { el.classList.add('is-hiding'); el.hidden = false; } });
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        showing.forEach(function (el, i) { el.style.transitionDelay = reduceMotion() ? '0s' : Math.min(i * 0.035, 0.35) + 's'; el.classList.remove('is-hiding'); });
        setTimeout(function () { showing.forEach(function (el) { el.style.transitionDelay = ''; }); }, 900);
      }); });
    }, delay);
  }

  function initGallery() {
    var grid = $('[data-gallery-grid]');
    var lb = $('#lightbox');
    var items = grid ? $$('li', grid) : [];
    var buttons = $$('[data-gallery-filter]');
    var moreWrap = $('.gallery__more');
    var moreBtn = $('[data-gallery-more]');
    var INITIAL = 12, filter = 'all', expanded = !moreBtn;

    function matches(el) { return filter === 'all' || el.getAttribute('data-cat') === filter; }
    function visible(el) { return matches(el) && (filter !== 'all' || expanded || items.indexOf(el) < INITIAL); }
    function apply(animate) {
      if (animate) filterItems(items, visible); else items.forEach(function (el) { el.hidden = !visible(el); });
      if (moreWrap) moreWrap.hidden = filter !== 'all' || expanded;
      if (moreBtn) moreBtn.setAttribute('aria-expanded', String(expanded));
    }
    if (grid) {
      apply(false);
      buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
          filter = btn.getAttribute('data-gallery-filter');
          buttons.forEach(function (b) { var on = b === btn; b.classList.toggle('is-active', on); b.setAttribute('aria-pressed', String(on)); });
          apply(true);
        });
      });
      if (moreBtn) moreBtn.addEventListener('click', function () {
        expanded = true; apply(true);
        var firstNew = items[INITIAL];
        if (firstNew) setTimeout(function () { var b = $('button', firstNew); if (b) b.focus({ preventScroll: true }); }, 400);
      });
    }

    if (!lb || typeof lb.showModal !== 'function') return;
    var fig = $('.lightbox__figure', lb), img = $('[data-lb-img]', lb), cap = $('[data-lb-caption]', lb), count = $('[data-lb-count]', lb);
    var list = [], pos = 0, trigger = null, closing = false;

    function fromGridItem(li) {
      var b = $('button', li);
      return { full: b.getAttribute('data-full'), w: b.getAttribute('data-w'), h: b.getAttribute('data-h'), caption: b.getAttribute('data-caption'), alt: $('img', li).alt, id: li.getAttribute('data-id') };
    }
    function fromSetItem(li) {
      return { full: li.getAttribute('data-full'), w: li.getAttribute('data-w'), h: li.getAttribute('data-h'), caption: li.getAttribute('data-caption'), alt: li.getAttribute('data-alt'), id: li.getAttribute('data-id') };
    }
    function render(dir) {
      var e = list[pos];
      var set = function () {
        img.src = e.full; img.alt = e.alt || ''; img.width = +e.w; img.height = +e.h;
        cap.textContent = e.caption || '';
        count.textContent = (pos + 1) + ' / ' + list.length;
        if (list.length > 1) [list[(pos + 1) % list.length], list[(pos - 1 + list.length) % list.length]].forEach(function (n) { var p = new Image(); p.src = n.full; });
      };
      if (!dir || reduceMotion()) { set(); return; }
      fig.style.setProperty('--swap-dir', (dir > 0 ? 16 : -16) + 'px');
      fig.classList.add('is-swapping');
      setTimeout(function () {
        set();
        fig.style.setProperty('--swap-dir', (dir > 0 ? -16 : 16) + 'px');
        var done = function () { requestAnimationFrame(function () { fig.classList.remove('is-swapping'); }); };
        if (img.complete) done(); else { img.onload = done; img.onerror = done; }
      }, 200);
    }
    function openAt(entries, start, from) {
      if (!entries.length) return;
      list = entries; pos = Math.max(0, start); trigger = from || null;
      lb.classList.toggle('is-single', list.length < 2);
      render(0);
      lb.showModal();
      requestAnimationFrame(function () { lb.classList.add('is-open'); });
      $('[data-lb-close]', lb).focus();
    }
    function close() {
      if (closing || !lb.open) return;
      closing = true;
      lb.classList.remove('is-open');
      setTimeout(function () { lb.close(); closing = false; if (trigger) trigger.focus({ preventScroll: true }); }, reduceMotion() ? 0 : 400);
    }
    function step(d) { if (list.length < 2) return; pos = (pos + d + list.length) % list.length; render(d); }

    if (grid) grid.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var current = items.filter(matches);
      openAt(current.map(fromGridItem), current.indexOf(b.closest('li')), b);
    });
    // Buttons elsewhere open a named set: a hidden data-set list, or a gallery category.
    $$('[data-lightbox]').forEach(function (b) {
      b.addEventListener('click', function () {
        var name = b.getAttribute('data-lightbox');
        var setEl = $('[data-set="' + name + '"]');
        var entries = setEl ? $$('li', setEl).map(fromSetItem) : items.filter(function (li) { return li.getAttribute('data-cat') === name; }).map(fromGridItem);
        var startId = b.getAttribute('data-start');
        var start = startId ? entries.map(function (x) { return x.id; }).indexOf(startId) : 0;
        openAt(entries, start, b);
      });
    });

    $('[data-lb-prev]', lb).addEventListener('click', function () { step(-1); });
    $('[data-lb-next]', lb).addEventListener('click', function () { step(1); });
    $('[data-lb-close]', lb).addEventListener('click', close);
    lb.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
    });
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lightbox__stage')) close(); });
    onSwipe(lb, step);
  }

  /* ---------- FAQ with smooth height ---------- */
  function initFaq() {
    $$('.qa').forEach(function (d) {
      var summary = $('summary', d), body = $('.qa__body', d), anim = null;
      summary.addEventListener('click', function (e) {
        if (reduceMotion() || !body.animate) return;
        e.preventDefault();
        if (anim) anim.cancel();
        if (d.open) {
          anim = body.animate([{ height: body.offsetHeight + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], { duration: 360, easing: 'cubic-bezier(.65,0,.35,1)' });
          anim.onfinish = function () { d.open = false; anim = null; };
        } else {
          d.open = true;
          anim = body.animate([{ height: '0px', opacity: 0 }, { height: body.offsetHeight + 'px', opacity: 1 }], { duration: 460, easing: 'cubic-bezier(.16,1,.3,1)' });
          anim.onfinish = function () { anim = null; };
        }
      });
    });
  }

  /* ---------- Floating Book Now on small screens ---------- */
  function initMobileCta() {
    var cta = $('[data-mobile-cta]');
    if (!cta || !('IntersectionObserver' in window)) return;
    var state = { hero: !!$('.hero, .flow-hero'), contact: false, footer: false };
    var update = function () { cta.classList.toggle('is-visible', !state.hero && !state.contact && !state.footer); };
    [['.hero, .flow-hero', 'hero'], ['#contact, #book', 'contact'], ['.site-footer', 'footer']].forEach(function (p) {
      var el = $(p[0]);
      if (el) new IntersectionObserver(function (en) { state[p[1]] = en[0].isIntersecting; update(); }).observe(el);
    });
  }

  /* ---------- Horizontal photo strip (native swipe; arrows on wider screens) ---------- */
  function initStrip() {
    var track = $('[data-strip]');
    if (!track) return;
    var prev = $('[data-strip-prev]'), next = $('[data-strip-next]');
    function update() {
      var max = track.scrollWidth - track.clientWidth - 2;
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max;
    }
    function go(dir) { track.scrollBy({ left: dir * track.clientWidth * 0.8, behavior: reduceMotion() ? 'auto' : 'smooth' }); }
    prev.addEventListener('click', function () { go(-1); });
    next.addEventListener('click', function () { go(1); });
    track.addEventListener('scroll', update, { passive: true });
    track.addEventListener('keydown', function (e) {
      if (e.target !== track) return;
      if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
    });
    window.addEventListener('resize', update);
    // Arrows appear on interaction and fade 3 seconds later.
    var frame = track.parentNode, t;
    function showArrows() {
      frame.classList.add('arrows-on'); clearTimeout(t);
      t = setTimeout(function () { var a = doc.activeElement, kb = false; if (a && a.classList && a.classList.contains('strip__arrow')) { try { kb = a.matches(':focus-visible'); } catch (e) {} if (kb) return; a.blur(); } frame.classList.remove('arrows-on'); }, 3000);
    }
    frame.addEventListener('pointermove', showArrows);
    frame.addEventListener('touchstart', showArrows, { passive: true });
    frame.addEventListener('focusin', showArrows);
    [prev, next].forEach(function (b) { b.addEventListener('click', showArrows); });
    update();
  }

  /* ---------- Opening film: muted autoplay loop, pause/play, sound and volume.
     Controls appear on load, tap, mouse movement or focus, then fade after 5 seconds. ---------- */
  function initFilm() {
    var video = $('[data-film]');
    var btn = $('[data-film-toggle]');
    var mute = $('[data-film-mute]');
    var vol = $('[data-film-volume]');
    var box = $('[data-film-controls]');
    if (!video || !btn) return;
    var frame = video.parentNode;
    var saveData = navigator.connection && navigator.connection.saveData;
    var userPaused = false, hideTimer;
    video.muted = true;
    function play() { var p = video.play(); if (p && p.catch) p.catch(function () {}); }
    function sync() {
      btn.setAttribute('aria-pressed', String(video.paused));
      btn.setAttribute('aria-label', video.paused ? 'Play the film' : 'Pause the film');
      if (mute) {
        var off = video.muted || video.volume === 0;
        mute.setAttribute('aria-pressed', String(off));
        mute.setAttribute('aria-label', off ? 'Turn sound on' : 'Turn sound off');
      }
    }
    function show() {
      if (!box) return;
      box.classList.add('is-visible');
      clearTimeout(hideTimer);
      hideTimer = setTimeout(function () {
        // Stay visible only for keyboard users; a mouse or tap leaves focus on the button, so release it.
        var a = document.activeElement, kb = false;
        if (box.contains(a)) { try { kb = a.matches(':focus-visible'); } catch (e) { kb = false; } if (!kb) a.blur(); }
        if (!kb) box.classList.remove('is-visible');
      }, 5000);
    }
    if (reduceMotion() || saveData) { video.removeAttribute('autoplay'); video.pause(); }
    btn.addEventListener('click', function () { if (video.paused) { userPaused = false; play(); } else { userPaused = true; video.pause(); } show(); });
    if (mute) mute.addEventListener('click', function () {
      video.muted = !video.muted;
      if (!video.muted && video.volume === 0) { video.volume = 0.6; if (vol) vol.value = 0.6; }
      sync(); show();
    });
    if (vol) {
      video.volume = +vol.value;
      vol.addEventListener('input', function () { video.volume = +vol.value; video.muted = +vol.value === 0; sync(); show(); });
    }
    ['play', 'pause', 'volumechange'].forEach(function (ev) { video.addEventListener(ev, sync); });
    frame.addEventListener('pointermove', show);
    frame.addEventListener('click', show);
    frame.addEventListener('touchstart', show, { passive: true });
    if (box) { box.addEventListener('focusin', show); box.addEventListener('focusout', show); }
    reduceMotionQuery.addEventListener('change', function () { if (reduceMotion()) video.pause(); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { if (!userPaused && !reduceMotion() && !saveData && video.paused) play(); }
        else if (!video.paused) video.pause();
      }, { threshold: 0.15 }).observe(video);
    }
    sync(); show();
  }

  /* ---------- Slideshow (included amenities): swipe, arrows, dots, autoplay with pause ---------- */
  function initSliders() {
    $$('[data-slider]').forEach(function (root) {
      var track = $('[data-slider-track]', root), items = $$('.slide-item', track);
      var dotsEl = $('[data-slider-dots]', root) || doc.createElement('div'), toggle = $('[data-slider-toggle]', root) || doc.createElement('button');
      if (!items.length) return;
      var paused = reduceMotion(), hold = false, timer;
      // Each slide is centred in turn (gallery-style showcase).
      function pages() { return items.length; }
      function center(el) { return el.offsetLeft - track.offsetLeft + el.offsetWidth / 2; }
      function current() {
        var mid = track.scrollLeft + track.clientWidth / 2, best = 0, d = Infinity;
        items.forEach(function (el, i) { var x = Math.abs(center(el) - mid); if (x < d) { d = x; best = i; } });
        return best;
      }
      function go(i) {
        var n = pages(); i = (i + n) % n;
        track.scrollTo({ left: center(items[i]) - track.clientWidth / 2, behavior: reduceMotion() ? 'auto' : 'smooth' });
        items.forEach(function (el, k) { el.classList.toggle('is-current', k === i); });
      }
      function sync() { var c = current(); items.forEach(function (el, k) { el.classList.toggle('is-current', k === c); }); $$('.slider__dot', dotsEl).forEach(function (d, i) { d.setAttribute('aria-current', String(i === c)); }); }
      function buildDots() {
        dotsEl.innerHTML = '';
        for (var i = 0; i < pages(); i++) {
          var b = doc.createElement('button');
          b.type = 'button'; b.className = 'slider__dot'; b.setAttribute('aria-label', 'Show slide ' + (i + 1));
          (function (k) { b.addEventListener('click', function () { go(k); restart(); }); })(i);
          dotsEl.appendChild(b);
        }
        sync();
      }
      function restart() { clearInterval(timer); if (!paused) timer = setInterval(function () { if (!hold && !doc.hidden) go(current() + 1); }, 4500); }
      function syncToggle() { toggle.setAttribute('aria-pressed', String(paused)); toggle.setAttribute('aria-label', paused ? 'Play slideshow' : 'Pause slideshow'); }
      $('[data-slider-prev]', root).addEventListener('click', function () { go(current() - 1); restart(); });
      $('[data-slider-next]', root).addEventListener('click', function () { go(current() + 1); restart(); });
      toggle.addEventListener('click', function () { paused = !paused; syncToggle(); restart(); });
      track.addEventListener('scroll', function () { requestAnimationFrame(sync); }, { passive: true });
      track.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); go(current() + 1); restart(); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); go(current() - 1); restart(); }
      });
      // Pause while the visitor is hovering, focused inside, or touching the slideshow.
      track.addEventListener('pointerenter', function () { hold = true; });
      track.addEventListener('pointerleave', function () { hold = false; });
      root.addEventListener('focusin', function () { hold = true; });
      root.addEventListener('focusout', function () { hold = false; });
      track.addEventListener('touchstart', function () { hold = true; }, { passive: true });
      track.addEventListener('touchend', function () { setTimeout(function () { hold = false; }, 2500); }, { passive: true });
      reduceMotionQuery.addEventListener('change', function () { if (reduceMotion()) { paused = true; syncToggle(); restart(); } });
      window.addEventListener('resize', buildDots);
      // Edge arrows appear on interaction and fade 3 seconds later.
      var arrowTimer;
      function showArrows() {
        root.classList.add('arrows-on');
        clearTimeout(arrowTimer);
        arrowTimer = setTimeout(function () {
          var a = doc.activeElement;
          if (a && a.classList && a.classList.contains('slider__arrow')) { var kb = false; try { kb = a.matches(':focus-visible'); } catch (e) {} if (kb) return; a.blur(); }
          root.classList.remove('arrows-on');
        }, 3000);
      }
      root.addEventListener('pointermove', showArrows);
      root.addEventListener('touchstart', showArrows, { passive: true });
      root.addEventListener('focusin', showArrows);
      $$('.slider__arrow', root).forEach(function (b) { b.addEventListener('click', showArrows); });
      // Start on a middle slide so photos sit on both sides, as in the reference.
      var startAt = Math.floor(items.length / 2);
      track.scrollLeft = center(items[startAt]) - track.clientWidth / 2;
      buildDots(); syncToggle(); restart();
    });
  }

  function initYear() { var y = $('[data-year]'); if (y) y.textContent = String(new Date().getFullYear()); }

  function start() {
    try { initReveals(); } catch (err) { root.classList.remove('js-anim'); }
    [initHeader, initCarousel, initTabs, initGallery, initFaq, initMobileCta, initStrip, initFilm, initSliders, initYear].forEach(safe);
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start); else start();
})();
