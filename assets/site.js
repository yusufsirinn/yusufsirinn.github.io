(function () {
  var root = document.documentElement;
  var STORAGE_KEY = 'sirin-lang';
  var tr = window.SIRIN_TR || {};
  var meta = window.SIRIN_META || {};

  var aria = {
    en: {
      appstore: function (n) { return n + ' on the App Store'; },
      play: function (n) { return n + ' on Google Play'; },
      huawei: function (n) { return n + ' on AppGallery'; },
      alt: function (n) { return n + ' icon'; },
      more: function (n) { return n + ' details'; }
    },
    tr: {
      appstore: function (n) { return n + " — App Store'da"; },
      play: function (n) { return n + " — Google Play'de"; },
      huawei: function (n) { return n + " — AppGallery'de"; },
      alt: function (n) { return n + ' ikonu'; },
      more: function (n) { return n + ' ayrıntıları'; }
    }
  };

  var nodes = Array.prototype.slice.call(document.querySelectorAll('[data-i18n]'));
  nodes.forEach(function (el) { el.setAttribute('data-en', el.innerHTML); });
  var desc = document.querySelector('meta[name="description"]');
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.lang button'));

  function read(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }
  function write(key, val) { try { localStorage.setItem(key, val); } catch (e) {} }

  function initial() {
    var q = /[?&]lang=(en|tr)\b/.exec(location.search);
    if (q) return q[1];
    var saved = read(STORAGE_KEY);
    if (saved === 'en' || saved === 'tr') return saved;
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || 'en';
    return /^tr\b/i.test(nav) ? 'tr' : 'en';
  }

  // Cihaza uygun mağaza öne çıkar; yalnızca sayfada gerçekten bağlantısı olan mağazalar.
  function platform() {
    var ua = navigator.userAgent || '';
    if (/HMSCore|HUAWEI|HONOR|HarmonyOS/i.test(ua)) return 'huawei';
    if (/iPhone|iPad|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)) return 'appstore';
    if (/Android/i.test(ua)) return 'play';
    return '';
  }
  function arrangeStores() {
    var want = platform();
    if (!want) return;
    document.querySelectorAll('.stores').forEach(function (box) {
      var links = Array.prototype.slice.call(box.querySelectorAll('a.store'));
      var first = links.filter(function (a) { return a.getAttribute('data-store') === want; })[0];
      if (!first && want === 'huawei') {
        first = links.filter(function (a) { return a.getAttribute('data-store') === 'play'; })[0];
      }
      if (!first) return;
      box.insertBefore(first, box.firstChild);
      links.forEach(function (a) { if (a !== first) a.classList.add('alt'); });
    });
  }

  function apply(lang) {
    root.lang = lang;
    root.setAttribute('data-lang', lang);
    nodes.forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      el.innerHTML = lang === 'tr' && tr[key] ? tr[key] : el.getAttribute('data-en');
    });
    document.querySelectorAll('a[data-store]').forEach(function (a) {
      a.setAttribute('aria-label', aria[lang][a.getAttribute('data-store')](a.getAttribute('data-app')));
    });
    document.querySelectorAll('a[data-more]').forEach(function (a) {
      a.setAttribute('aria-label', aria[lang].more(a.getAttribute('data-more')));
    });
    document.querySelectorAll('img[data-app]').forEach(function (img) {
      img.setAttribute('alt', aria[lang].alt(img.getAttribute('data-app')));
    });
    if (desc && meta.desc && meta.desc[lang]) desc.setAttribute('content', meta.desc[lang]);
    if (meta.title && meta.title[lang]) document.title = meta.title[lang];
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang)); });
  }

  function setLang(lang, animate) {
    if (lang === root.getAttribute('data-lang')) return;
    write(STORAGE_KEY, lang);
    try { history.replaceState(null, '', '?lang=' + lang + location.hash); } catch (e) {}
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!animate || reduce) { apply(lang); return; }
    root.classList.add('switching');
    setTimeout(function () { apply(lang); root.classList.remove('switching'); }, 150);
  }

  buttons.forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang'), true); });
  });
  arrangeStores();
  apply(initial());
})();
