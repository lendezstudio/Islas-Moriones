/* Islas Moriones Beach Resort: site interactions.
   Progressive enhancement: everything readable and usable without this file. */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduceMotion = function () { return reduceMotionQuery.matches; };
  var $ = function (sel, ctx) { return (ctx || doc).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); };

  var CONTACT = {
    whatsapp: '639178925752',
    email: 'islasmoriones.cmhi@gmail.com',
    phoneDisplay: '+63 917 892 5752'
  };

  root.classList.add('js-anim');

  function safe(fn) { try { fn(); } catch (err) { if (window.console) console.error(err); } }

  // Horizontal swipe detection on touch screens; calls onDir(+1) for next, (-1) for previous.
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

  /* ------------------------------------------------------------
     Header state, current section, mobile menu
     ------------------------------------------------------------ */
  function initHeader() {
    var header = $('.site-header');
    var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 24); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    var links = $$('.primary-nav a');
    if ('IntersectionObserver' in window) {
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

    // Mobile menu
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
        closeTimer = setTimeout(function () { menu.hidden = true; }, reduceMotion() ? 0 : 700);
      }
    }
    toggle.addEventListener('click', function () { setOpen(toggle.getAttribute('aria-expanded') !== 'true'); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { setOpen(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', function (m) { if (m.matches) setOpen(false); });
  }

  /* ------------------------------------------------------------
     Hero slideshow
     ------------------------------------------------------------ */
  function initCarousel() {
    var media = $('.carousel');
    var slides = $$('.slide', media);
    var controls = $('.carousel-controls');
    if (!media || slides.length < 2) return;

    var btnPrev = $('[data-prev]', controls);
    var btnNext = $('[data-next]', controls);
    var btnToggle = $('[data-toggle]', controls);
    var elCurrent = $('[data-current]', controls);
    var elTotal = $('[data-total]', controls);
    var elCaption = $('[data-caption]', controls);
    var captionWrap = $('.carousel-controls__caption', controls);
    var bar = $('.carousel-controls__progress span', controls);
    var track = $('.carousel__track', media);

    var DURATION = 6500;
    var index = 0;
    var elapsed = 0;
    var last = null;
    var userPaused = reduceMotion();
    var holds = {};      // temporary pauses: hover, focus, offscreen, hidden tab, touch
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };

    elTotal.textContent = pad(slides.length);

    function isPlaying() { return !userPaused && Object.keys(holds).length === 0; }

    function syncToggle() {
      btnToggle.setAttribute('aria-pressed', String(userPaused));
      btnToggle.setAttribute('aria-label', userPaused ? 'Play slideshow' : 'Pause slideshow');
      // Announce slide changes only when the visitor is in control.
      captionWrap.setAttribute('aria-live', userPaused ? 'polite' : 'off');
    }

    function go(next) {
      next = (next + slides.length) % slides.length;
      if (next === index) return;
      var prev = slides[index];
      var cur = slides[next];
      var img = $('img', cur);
      if (img && img.loading === 'lazy') img.loading = 'eager';
      prev.classList.remove('is-active');
      prev.classList.add('is-leaving');
      prev.setAttribute('aria-hidden', 'true');
      cur.classList.remove('is-leaving');
      cur.classList.add('is-active');
      cur.removeAttribute('aria-hidden');
      setTimeout(function () { prev.classList.remove('is-leaving'); }, 1500);
      index = next;
      elapsed = 0;
      bar.style.transform = 'scaleX(0)';
      elCurrent.textContent = pad(index + 1);
      var text = $('figcaption', cur).textContent;
      if (reduceMotion()) { elCaption.textContent = text; }
      else {
        elCaption.classList.add('is-swapping');
        setTimeout(function () { elCaption.textContent = text; elCaption.classList.remove('is-swapping'); }, 260);
      }
      // Warm the following image so the next crossfade is instant.
      var after = $('img', slides[(index + 1) % slides.length]);
      if (after && after.loading === 'lazy') after.loading = 'eager';
    }

    function tick(t) {
      if (last === null) last = t;
      var dt = t - last;
      last = t;
      if (isPlaying()) {
        elapsed += dt;
        bar.style.transform = 'scaleX(' + Math.min(elapsed / DURATION, 1) + ')';
        if (elapsed >= DURATION) go(index + 1);
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);

    function hold(key, on) { if (on) holds[key] = true; else delete holds[key]; }

    btnPrev.addEventListener('click', function () { go(index - 1); });
    btnNext.addEventListener('click', function () { go(index + 1); });
    btnToggle.addEventListener('click', function () {
      userPaused = !userPaused;
      if (!userPaused) { delete holds.focus; }
      syncToggle();
    });

    // Pause while a visitor is looking closely at the photo or using the controls.
    [media, controls].forEach(function (el) {
      el.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hold('hover', true); });
      el.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') hold('hover', false); });
    });
    media.addEventListener('focusin', function () { hold('focus', true); });
    media.addEventListener('focusout', function () { hold('focus', false); });

    function onKey(e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); }
    }
    media.addEventListener('keydown', onKey);
    controls.addEventListener('keydown', onKey);

    // Touch swipe (vertical scrolling stays native via touch-action: pan-y)
    onSwipe(media, function (dir) { go(index + dir); }, function (active) {
      if (active) hold('touch', true); else setTimeout(function () { hold('touch', false); }, 1200);
    });

    doc.addEventListener('visibilitychange', function () { hold('tab', doc.hidden); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        hold('offscreen', !entries[0].isIntersecting);
      }, { threshold: 0.2 }).observe(media);
    }
    reduceMotionQuery.addEventListener('change', function () { if (reduceMotion()) { userPaused = true; syncToggle(); } });

    syncToggle();
  }

  /* ------------------------------------------------------------
     Scroll reveals
     ------------------------------------------------------------ */
  function initReveals() {
    var items = $$('[data-reveal]');
    if (!('IntersectionObserver' in window)) { items.forEach(function (el) { el.classList.add('is-in'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    items.forEach(function (el) { io.observe(el); });

    // Arrival steps reveal one after another as the list arrives.
    $$('.steps .step').forEach(function (step, i) { step.style.transitionDelay = (i * 0.14) + 's'; });
  }

  /* ------------------------------------------------------------
     Shared: animated show/hide for filtered lists
     ------------------------------------------------------------ */
  function filterItems(items, show, onDone) {
    var hiding = items.filter(function (el) { return !show(el) && !el.hidden; });
    var showing = items.filter(function (el) { return show(el); });
    var delay = reduceMotion() ? 0 : 320;
    hiding.forEach(function (el) { el.classList.add('is-hiding'); });
    setTimeout(function () {
      hiding.forEach(function (el) { el.hidden = true; el.classList.remove('is-hiding'); });
      showing.forEach(function (el) {
        if (el.hidden) { el.classList.add('is-hiding'); el.hidden = false; }
      });
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        showing.forEach(function (el, i) {
          el.style.transitionDelay = reduceMotion() ? '0s' : Math.min(i * 0.04, 0.4) + 's';
          el.classList.remove('is-hiding');
        });
        setTimeout(function () { showing.forEach(function (el) { el.style.transitionDelay = ''; }); }, 900);
        if (onDone) onDone();
      }); });
    }, delay);
  }

  function setPressed(buttons, active) {
    buttons.forEach(function (b) {
      var on = b === active;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', String(on));
    });
  }

  /* ------------------------------------------------------------
     Rooms: collection filter + detail drawer
     ------------------------------------------------------------ */
  function initRooms() {
    var buttons = $$('[data-room-filter]');
    var rooms = $$('[data-room-grid] > .room').concat([$('.kubo')]);
    var noteWrap = $('[data-collection-note]');
    var notes = $$('[data-note]', noteWrap);

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-room-filter');
        setPressed(buttons, btn);
        filterItems(rooms, function (el) {
          return f === 'all' || (el.getAttribute('data-groups') || '').split(' ').indexOf(f) > -1;
        });
        noteWrap.hidden = f === 'all';
        notes.forEach(function (n) { n.hidden = n.getAttribute('data-note') !== f; });
        if (f !== 'all') { noteWrap.style.animation = 'none'; void noteWrap.offsetWidth; noteWrap.style.animation = ''; }
      });
    });

    // Detail drawer
    var drawer = $('#room-drawer');
    if (!drawer || typeof drawer.showModal !== 'function') return; // native <details> remains as fallback
    var mediaEl = $('[data-drawer-media]', drawer);
    var whereEl = $('[data-drawer-where]', drawer);
    var titleEl = $('#drawer-title', drawer);
    var rateEl = $('[data-drawer-rate]', drawer);
    var specEl = $('[data-drawer-spec]', drawer);
    var inquireEl = $('[data-drawer-inquire]', drawer);
    var returnFocus = null;
    var closing = false;

    function figure(src, srcset, w, h, alt, pos) {
      var fig = doc.createElement('figure');
      if (pos) fig.style.setProperty('--pos', pos);
      var img = doc.createElement('img');
      img.src = src;
      if (srcset) { img.srcset = srcset; img.sizes = '(min-width: 900px) 560px, 100vw'; }
      img.width = w; img.height = h; img.alt = alt; img.decoding = 'async';
      if (pos) img.style.setProperty('--pos', pos);
      fig.appendChild(img);
      return fig;
    }

    function open(details) {
      var room = details.closest('.room');
      var thumb = $('.room__media img', room);
      var pos = $('.room__media', room).style.getPropertyValue('--pos');
      mediaEl.innerHTML = '';
      mediaEl.appendChild(figure(thumb.currentSrc || thumb.src, thumb.getAttribute('srcset'), thumb.width, thumb.height, thumb.alt, pos));
      var extra = details.getAttribute('data-extra-img');
      if (extra) {
        var p = extra.split('|');
        mediaEl.appendChild(figure(p[0], null, +p[1], +p[2], p[3], '50% 55%'));
      }
      whereEl.textContent = $('.room__where', room).textContent;
      titleEl.textContent = $('.room__name', room).textContent;
      rateEl.innerHTML = $('.room__rate', room).innerHTML;
      specEl.innerHTML = '';
      specEl.appendChild($('.spec', details).cloneNode(true));
      inquireEl.setAttribute('data-interest', details.getAttribute('data-room'));
      returnFocus = $('summary', details);
      drawer.showModal();
      drawer.scrollTop = 0;
      $('.drawer__panel', drawer).scrollTop = 0;
      $('[data-close]', drawer).focus({ preventScroll: true });
      requestAnimationFrame(function () { drawer.classList.add('is-open'); });
    }

    function close() {
      if (closing || !drawer.open) return;
      closing = true;
      drawer.classList.remove('is-open');
      setTimeout(function () {
        drawer.close();
        closing = false;
        if (returnFocus) returnFocus.focus({ preventScroll: true });
      }, reduceMotion() ? 0 : 520);
    }

    $$('.room__details').forEach(function (details) {
      $('summary', details).addEventListener('click', function (e) { e.preventDefault(); open(details); });
    });
    $('[data-close]', drawer).addEventListener('click', close);
    drawer.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
    drawer.addEventListener('click', function (e) {
      if (!e.target.closest('.drawer__panel')) close();
    });
    inquireEl.addEventListener('click', function (e) {
      e.preventDefault();
      applyInterest(inquireEl.getAttribute('data-interest'));
      returnFocus = null;
      close();
      setTimeout(function () { scrollToInquiry(); }, reduceMotion() ? 0 : 380);
    });
  }

  /* ------------------------------------------------------------
     Gallery: filter, show more, lightbox
     ------------------------------------------------------------ */
  var openLightboxFor = null;

  function initGallery() {
    var grid = $('[data-gallery-grid]');
    if (!grid) return;
    var items = $$('li', grid);
    var buttons = $$('[data-gallery-filter]');
    var moreWrap = $('.gallery__more');
    var moreBtn = $('[data-gallery-more]');
    var INITIAL = 12;
    var filter = 'all';
    var expanded = false;

    function matches(el) { return filter === 'all' || el.getAttribute('data-cat') === filter; }
    function visible(el) {
      if (!matches(el)) return false;
      if (filter !== 'all' || expanded) return true;
      return items.indexOf(el) < INITIAL;
    }
    function apply(animate) {
      if (animate) filterItems(items, visible);
      else items.forEach(function (el) { el.hidden = !visible(el); });
      moreWrap.hidden = filter !== 'all' || expanded;
      moreBtn.setAttribute('aria-expanded', String(expanded));
    }
    apply(false);

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filter = btn.getAttribute('data-gallery-filter');
        setPressed(buttons, btn);
        apply(true);
      });
    });
    moreBtn.addEventListener('click', function () {
      expanded = true;
      apply(true);
      var firstNew = items[INITIAL];
      if (firstNew) setTimeout(function () { var b = $('button', firstNew); if (b) b.focus({ preventScroll: true }); }, 400);
    });

    // Lightbox
    var lb = $('#lightbox');
    if (!lb || typeof lb.showModal !== 'function') return;
    var fig = $('.lightbox__figure', lb);
    var img = $('[data-lb-img]', lb);
    var cap = $('[data-lb-caption]', lb);
    var count = $('[data-lb-count]', lb);
    var list = [];
    var pos = 0;
    var trigger = null;
    var closing = false;

    function entry(li) {
      var b = $('button', li);
      return { full: b.getAttribute('data-full'), w: b.getAttribute('data-w'), h: b.getAttribute('data-h'),
               caption: b.getAttribute('data-caption'), alt: $('img', li).alt, button: b };
    }
    function render(dir) {
      var e = list[pos];
      var set = function () {
        img.src = e.full; img.alt = e.alt; img.width = +e.w; img.height = +e.h;
        cap.textContent = e.caption;
        count.textContent = (pos + 1) + ' / ' + list.length;
        [list[(pos + 1) % list.length], list[(pos - 1 + list.length) % list.length]].forEach(function (n) {
          if (n) { var pre = new Image(); pre.src = n.full; }
        });
      };
      if (!dir || reduceMotion()) { set(); return; }
      fig.style.setProperty('--swap-dir', (dir > 0 ? 16 : -16) + 'px');
      fig.classList.add('is-swapping');
      setTimeout(function () {
        set();
        fig.style.setProperty('--swap-dir', (dir > 0 ? -16 : 16) + 'px');
        var done = function () { requestAnimationFrame(function () { fig.classList.remove('is-swapping'); }); };
        if (img.complete) done(); else { img.onload = done; img.onerror = done; }
      }, 220);
    }
    function openAt(entries, start, from) {
      list = entries; pos = Math.max(0, start); trigger = from || null;
      render(0);
      lb.showModal();
      requestAnimationFrame(function () { lb.classList.add('is-open'); });
      $('[data-lb-close]', lb).focus();
    }
    function close() {
      if (closing || !lb.open) return;
      closing = true;
      lb.classList.remove('is-open');
      setTimeout(function () {
        lb.close(); closing = false;
        if (trigger) trigger.focus({ preventScroll: true });
      }, reduceMotion() ? 0 : 420);
    }
    function step(d) { pos = (pos + d + list.length) % list.length; render(d); }

    grid.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var current = items.filter(matches).map(entry);
      var idx = current.map(function (x) { return x.button; }).indexOf(b);
      openAt(current, idx, b);
    });
    openLightboxFor = function (cat, startId, from) {
      var set = items.filter(function (li) { return li.getAttribute('data-cat') === cat; });
      var start = startId ? set.map(function (li) { return li.getAttribute('data-id'); }).indexOf(startId) : 0;
      openAt(set.map(entry), start, from);
    };
    $$('[data-open-gallery]').forEach(function (b) {
      b.addEventListener('click', function () { openLightboxFor(b.getAttribute('data-open-gallery'), b.getAttribute('data-start'), b); });
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

  /* ------------------------------------------------------------
     FAQ accordion with smooth height
     ------------------------------------------------------------ */
  function initFaq() {
    $$('.qa').forEach(function (d) {
      var summary = $('summary', d);
      var body = $('.qa__body', d);
      var anim = null;
      summary.addEventListener('click', function (e) {
        if (reduceMotion() || !body.animate) return;
        e.preventDefault();
        if (anim) anim.cancel();
        if (d.open) {
          anim = body.animate([{ height: body.offsetHeight + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], { duration: 380, easing: 'cubic-bezier(.65,0,.35,1)' });
          anim.onfinish = function () { d.open = false; anim = null; };
        } else {
          d.open = true;
          var h = body.offsetHeight;
          anim = body.animate([{ height: '0px', opacity: 0 }, { height: h + 'px', opacity: 1 }], { duration: 480, easing: 'cubic-bezier(.16,1,.3,1)' });
          anim.onfinish = function () { anim = null; };
        }
      });
    });
  }

  /* ------------------------------------------------------------
     Inquiry builder (opens a draft; never claims to send)
     ------------------------------------------------------------ */
  var form, roomSelect, questionField;

  function applyInterest(value, question) {
    if (!roomSelect) return;
    var opt = $$('option', roomSelect).filter(function (o) { return (o.value || o.textContent) === value; })[0];
    if (opt) roomSelect.value = opt.value || opt.textContent;
    if (question && questionField && (!questionField.value || questionField.dataset.auto === 'true')) {
      questionField.value = question;
      questionField.dataset.auto = 'true';
    }
    roomSelect.dispatchEvent(new Event('change', { bubbles: true }));
    var field = roomSelect.closest('.field');
    field.classList.remove('flash');
    void field.offsetWidth;
    field.classList.add('flash');
  }

  function scrollToInquiry() {
    var target = $('#inquire');
    target.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' });
  }

  function isoToday() {
    var d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 10);
  }
  function niceDate(iso) {
    if (!iso) return '';
    var p = iso.split('-');
    var d = new Date(+p[0], +p[1] - 1, +p[2]);
    return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
  }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  function interestPhrase(v) {
    switch (v) {
      case 'Help me choose': return "We'd appreciate help choosing a suitable room.";
      case 'Room for one or two': return "We're interested in a room for one or two.";
      case 'Family or group stay': return "We're interested in a family or group stay.";
      default: return "We're interested in the " + v + '.';
    }
  }

  function openDraft(channel, subject, text, statusEl) {
    var url;
    if (channel === 'email') {
      url = 'mailto:' + CONTACT.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
      window.location.href = url;
      statusEl.innerHTML = '';
      statusEl.appendChild(doc.createTextNode('Your email app should now show a draft addressed to the resort. Nothing has been sent yet: review it there and press send. No email app? Write to '));
      var a = doc.createElement('a'); a.href = 'mailto:' + CONTACT.email; a.textContent = CONTACT.email;
      statusEl.appendChild(a);
      statusEl.appendChild(doc.createTextNode(' or call ' + CONTACT.phoneDisplay + '.'));
    } else {
      url = 'https://wa.me/' + CONTACT.whatsapp + '?text=' + encodeURIComponent(text);
      var link = doc.createElement('a');
      link.href = url; link.target = '_blank'; link.rel = 'noopener';
      doc.body.appendChild(link); link.click(); link.remove();
      statusEl.innerHTML = '';
      statusEl.appendChild(doc.createTextNode('WhatsApp should open in a new tab with your message ready. Nothing has been sent yet: review it there and press send. If it didn’t open, '));
      var again = doc.createElement('a'); again.href = url; again.target = '_blank'; again.rel = 'noopener'; again.textContent = 'open WhatsApp again';
      statusEl.appendChild(again);
      statusEl.appendChild(doc.createTextNode(' or call ' + CONTACT.phoneDisplay + '.'));
    }
  }

  function setError(input, msg) {
    var field = input.closest('.field');
    var err = $('.field__error', field);
    field.classList.toggle('has-error', !!msg);
    input.setAttribute('aria-invalid', msg ? 'true' : 'false');
    err.textContent = msg || '';
    return !msg;
  }

  function initInquiry() {
    form = $('#inquiry-form');
    if (!form) return;
    roomSelect = $('#f-room');
    questionField = $('#f-question');
    var checkin = $('#f-checkin');
    var checkout = $('#f-checkout');
    var adults = $('#f-adults');
    var children = $('#f-children');
    var preview = $('[data-preview]', form);
    var status = $('.form-status', form);
    var today = isoToday();
    checkin.min = today;
    checkout.min = today;

    questionField.addEventListener('input', function () { questionField.dataset.auto = 'false'; });

    function build() {
      var a = parseInt(adults.value, 10);
      var c = parseInt(children.value, 10);
      var who = (isNaN(a) ? '[adults]' : plural(a, 'adult', 'adults')) +
        (isNaN(c) || c === 0 ? '' : ' and ' + plural(c, 'child', 'children'));
      var text = 'Hi Islas Moriones! I’d like to ask about a stay from ' +
        (checkin.value ? niceDate(checkin.value) : '[check-in]') + ' to ' +
        (checkout.value ? niceDate(checkout.value) : '[check-out]') + ' for ' + who + '. ' +
        interestPhrase(roomSelect.value) +
        ' Could you share room availability, rates and what’s included?';
      var q = questionField.value.trim();
      if (q) text += '\n\n' + q;
      return text;
    }
    var pending;
    function updatePreview() {
      preview.textContent = build();
      clearTimeout(pending);
      preview.classList.remove('is-updated');
      pending = setTimeout(function () { preview.classList.add('is-updated'); }, 10);
    }
    form.addEventListener('input', updatePreview);
    form.addEventListener('change', updatePreview);
    updatePreview();

    checkin.addEventListener('change', function () {
      if (checkin.value) {
        var p = checkin.value.split('-');
        var next = new Date(+p[0], +p[1] - 1, +p[2] + 1);
        next.setMinutes(next.getMinutes() - next.getTimezoneOffset());
        checkout.min = next.toISOString().slice(0, 10);
        if (checkout.value && checkout.value <= checkin.value) checkout.value = '';
      }
      if ($('#f-checkin').closest('.field').classList.contains('has-error')) validate();
    });

    $$('.stepper', form).forEach(function (s) {
      var input = $('input', s);
      $$('button', s).forEach(function (b) {
        b.addEventListener('click', function () {
          var v = parseInt(input.value, 10); if (isNaN(v)) v = 0;
          v = Math.max(+input.min, Math.min(+input.max, v + +b.getAttribute('data-step')));
          input.value = v;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        });
      });
    });

    function validate() {
      var ok = true;
      ok = setError(checkin, checkin.value ? (checkin.value < today ? 'Choose a check-in date from today onward.' : '') : 'Choose your check-in date.') && ok;
      ok = setError(checkout, !checkout.value || (checkin.value && checkout.value <= checkin.value) ? 'Choose a check-out date after check-in.' : '') && ok;
      var a = adults.value.trim(), c = children.value.trim();
      ok = setError(adults, /^\d+$/.test(a) && +a >= 1 ? '' : 'Enter the number of adults.') && ok;
      ok = setError(children, /^\d+$/.test(c) ? '' : 'Enter zero or more children.') && ok;
      return ok;
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      status.textContent = '';
      if (!validate()) {
        var first = $('[aria-invalid="true"]', form);
        if (first) first.focus();
        return;
      }
      var via = $('input[name="via"]:checked', form).value;
      openDraft(via, 'Stay inquiry: ' + niceDate(checkin.value) + ' to ' + niceDate(checkout.value), build(), status);
    });
    [checkin, checkout, adults, children].forEach(function (el) {
      el.addEventListener('blur', function () { if (el.closest('.field').classList.contains('has-error')) validate(); });
    });

    // Links that pre-select a room or preference
    doc.addEventListener('click', function (e) {
      var link = e.target.closest('a[data-interest]');
      if (!link || link.hasAttribute('data-drawer-inquire')) return;
      applyInterest(link.getAttribute('data-interest'), link.getAttribute('data-question'));
    });

    // Arrival question builder
    var arr = $('#arrival-form');
    if (arr) {
      var date = $('#arr-date');
      var origin = $('#arr-origin');
      var arrStatus = $('.form-status', arr);
      date.min = today;
      arr.addEventListener('submit', function (e) {
        e.preventDefault();
        arrStatus.textContent = '';
        var ok = setError(date, date.value ? '' : 'Choose your planned arrival date.');
        ok = setError(origin, origin.value.trim() ? '' : 'Tell us where you’ll be traveling from.') && ok;
        if (!ok) { $('[aria-invalid="true"]', arr).focus(); return; }
        var text = 'Hi Islas Moriones! We’re planning to visit on ' + niceDate(date.value) + ' from ' + origin.value.trim() +
          '. Could you advise on the departure point, boat arrangements and arrival details?';
        openDraft($('input[name="arr-via"]:checked', arr).value, 'Getting to Islas Moriones on ' + niceDate(date.value), text, arrStatus);
      });
    }
  }

  /* ------------------------------------------------------------
     Mobile inquiry button: visible between hero and inquiry
     ------------------------------------------------------------ */
  function initMobileCta() {
    var cta = $('[data-mobile-cta]');
    if (!cta || !('IntersectionObserver' in window)) return;
    var state = { hero: true, inquire: false, footer: false };
    var update = function () { cta.classList.toggle('is-visible', !state.hero && !state.inquire && !state.footer); };
    var watch = function (el, key) {
      if (!el) return;
      new IntersectionObserver(function (en) { state[key] = en[0].isIntersecting; update(); }).observe(el);
    };
    watch($('.hero'), 'hero');
    watch($('#inquire'), 'inquire');
    watch($('.site-footer'), 'footer');
  }

  function initYear() {
    var y = $('[data-year]');
    if (y) y.textContent = String(new Date().getFullYear());
  }

  function start() {
    try { initReveals(); } catch (err) { root.classList.remove('js-anim'); }
    [initHeader, initCarousel, initRooms, initGallery, initFaq, initInquiry, initMobileCta, initYear].forEach(safe);
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start); else start();
})();
