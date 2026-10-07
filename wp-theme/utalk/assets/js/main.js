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
