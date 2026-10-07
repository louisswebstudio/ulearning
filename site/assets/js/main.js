// Mobile menu toggle
(function () {
  var burger = document.getElementById('nav-burger');
  var menu = document.getElementById('nav-mobile');
  if (!burger || !menu) return;

  function setOpen(open) {
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    menu.hidden = !open;
  }

  burger.addEventListener('click', function () {
    setOpen(burger.getAttribute('aria-expanded') !== 'true');
  });
  menu.addEventListener('click', function (e) {
    if (e.target.closest('a')) setOpen(false);
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1180) setOpen(false);
  });
})();

// Testimonials slider arrows (Étudiants)
(function () {
  var track = document.getElementById('stu-track');
  var prev = document.getElementById('stu-prev');
  var next = document.getElementById('stu-next');
  if (!track || !prev || !next) return;

  function step() {
    var card = track.querySelector('.story');
    return card ? card.getBoundingClientRect().width + 20 : 400;
  }
  prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: 'smooth' }); });
  next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: 'smooth' }); });
})();

// Contact form: client-side check. On WordPress the form posts to admin-post.php (see functions.php).
(function () {
  var form = document.getElementById('contact-form');
  if (!form) return;
  var err = document.getElementById('cf-error');
  var ok = document.getElementById('cf-success');

  form.addEventListener('submit', function (e) {
    var valid = true;
    form.querySelectorAll('.field input, .field select').forEach(function (f) {
      var bad = !f.checkValidity();
      f.closest('.field').classList.toggle('field--error', bad);
      if (bad) valid = false;
    });
    err.hidden = valid;
    ok.hidden = true;
    if (!valid) { e.preventDefault(); return; }
    // WordPress theme: the form has an action and the server sends the message.
    if (form.hasAttribute('action')) return;
    e.preventDefault();
    ok.hidden = false;
    form.reset();
  });
  form.addEventListener('input', function (e) {
    var field = e.target.closest('.field');
    if (field && e.target.checkValidity()) field.classList.remove('field--error');
  });
})();

// Gallery filters (L'Expérience)
(function () {
  var buttons = document.querySelectorAll('.filter');
  var tiles = document.querySelectorAll('.tile');
  if (!buttons.length) return;

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cat = btn.getAttribute('data-filter');
      buttons.forEach(function (b) {
        var on = b === btn;
        b.classList.toggle('is-active', on);
        b.setAttribute('aria-pressed', String(on));
      });
      tiles.forEach(function (t) {
        t.hidden = cat !== 'all' && t.getAttribute('data-cat') !== cat;
      });
    });
  });
})();

// Hero 3D carousel: auto-spin, drag to turn (mouse + touch), momentum on release
(function () {
  var ring = document.querySelector('.ring');
  var track = ring && ring.querySelector('.ring__track');
  if (!track || !window.requestAnimationFrame) return;

  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var AUTO = reduce ? 0 : -4.5;          // deg/s, same pace as the old 80s CSS loop
  var angle = 0, speed = AUTO, target = AUTO;
  var dragging = false, pointerId = null, lastX = 0, lastT = 0, degPerPx = 0.07;
  var visible = true, last = 0, raf = 0;

  ring.classList.add('ring--js');

  // Screen px → degrees: depends on radius and perspective, which change per breakpoint
  function measure() {
    var cs = getComputedStyle(ring);
    var r = parseFloat(cs.getPropertyValue('--r')) || 1000;
    var p = parseFloat(cs.perspective) || 1500;
    degPerPx = 180 / (Math.PI * r * p / (p + r));
  }

  function frame(t) {
    var dt = last ? Math.min((t - last) / 1000, 0.05) : 0;
    last = t;
    if (!dragging) {
      speed += (target - speed) * (1 - Math.exp(-dt * 1.6)); // ease momentum back to auto pace
      angle += speed * dt;
    }
    track.style.transform = 'rotateY(' + angle + 'deg)';
    raf = visible ? requestAnimationFrame(frame) : 0;
  }
  function start() { if (!raf) { last = 0; raf = requestAnimationFrame(frame); } }

  ring.addEventListener('pointerdown', function (e) {
    if (e.button !== 0) return;
    measure();
    dragging = true; pointerId = e.pointerId;
    lastX = e.clientX; lastT = e.timeStamp; speed = 0;
    ring.classList.add('is-dragging');
    ring.setPointerCapture(e.pointerId);
  });
  ring.addEventListener('pointermove', function (e) {
    if (!dragging || e.pointerId !== pointerId) return;
    var dx = e.clientX - lastX, dts = Math.max((e.timeStamp - lastT) / 1000, 0.001);
    angle -= dx * degPerPx;
    speed = speed * 0.6 + (-dx * degPerPx / dts) * 0.4; // smoothed fling velocity
    lastX = e.clientX; lastT = e.timeStamp;
  });
  function release(e) {
    if (!dragging || e.pointerId !== pointerId) return;
    dragging = false;
    if (e.timeStamp - lastT > 80) speed = 0;              // held still before letting go: no fling
    speed = Math.max(-240, Math.min(240, speed));
    ring.classList.remove('is-dragging');
  }
  ring.addEventListener('pointerup', release);
  ring.addEventListener('pointercancel', release);
  ring.addEventListener('dragstart', function (e) { e.preventDefault(); });

  // Pause on mouse hover (as before), keep spinning on touch
  ring.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') target = 0; });
  ring.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') target = AUTO; });

  // Only animate while on screen
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible) start();
    }).observe(ring);
  }
  start();
})();
