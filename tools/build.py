#!/usr/bin/env python3
"""Sirin Apps site builder.

Tek kaynak: aşağıdaki APPS listesi. Çalıştırınca şunları üretir:
  - <slug>/index.html  (her uygulamanın ayrıntı sayfası)
  - index.html içindeki  <!--sprite-->…<!--/sprite-->  ve  <!--cards-->…<!--/cards-->  blokları
  - sitemap.xml, robots.txt

Çalıştırma:  python3 tools/build.py
Yeni mağaza (ör. Huawei AppGallery) eklemek: ilgili uygulamanın "stores" sözlüğüne
"huawei": "<AppGallery Connect'ten alınan resmî bağlantı>" yaz, betiği çalıştır.
Yayında olmayan mağaza için anahtar eklenmez.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://yusufsirinn.github.io"
OWNER = "Yusuf Şirin"

STORE_LABEL = {"appstore": "App Store", "play": "Google Play", "huawei": "AppGallery"}
STORE_OS = {"appstore": "iOS", "play": "Android", "huawei": "Android"}

APPS = [
  dict(slug="shapio", name="Shapio", accent="#2fa9e0", pat="p-shapio", cat="GameApplication",
       stores={"appstore": "https://apps.apple.com/app/id6803520460",
               "play": "https://play.google.com/store/apps/details?id=com.shapio.app"},
       sub=("Pattern Logic Puzzle", "Zeka & Mantık Bulmaca"),
       desc=("Find the hidden row of shapes on the board and trace it in one line.",
             "Tahtada saklanan şekil dizisini bul ve parmağını kaydırarak tek çizgide işaretle."),
       lead=("A sequence of shapes appears. The same sequence is hidden on the board in a straight line, horizontal, vertical or diagonal. Find it, slide your finger across the shapes and clear the board.",
             "Bir şekil dizisi görünür. Aynı dizi tahtada düz bir çizgide saklanır: yatay, dikey ya da çapraz. Onu bul, parmağını şekillerin üzerinde kaydır ve tahtayı temizle."),
       feats=[("i-trace", ("Trace the pattern", "Deseni izle"),
               ("No text to read and no long rules. You start playing from the first second.",
                "Okunacak metin ve uzun kurallar yok. İlk saniyeden oynamaya başlarsın.")),
              ("i-star", ("Three lives, three stars", "Üç can, üç yıldız"),
               ("Each wrong line costs a life. The lives you have left at the end become stars.",
                "Her yanlış çizgi bir can götürür. Sonda kalan canlar yıldıza dönüşür.")),
              ("i-grid", ("A board that grows", "Seninle büyüyen tahta"),
               ("Start on a compact 3×3 grid and grow up to 10×10 as you improve.",
                "3×3'lük küçük bir tahtayla başla, ilerledikçe 10×10'a kadar büyür."))]),
  dict(slug="sudoku", name="Sudoku", accent="#f5c518", pat="p-sudoku", cat="GameApplication",
       stores={"appstore": "https://apps.apple.com/app/id6769049219",
               "play": "https://play.google.com/store/apps/details?id=com.minimalsudoku.app"},
       sub=("Hints & Number Logic", "İpucu & Sayı Mantığı"),
       desc=("Classic sudoku with hints that teach the logic behind each move.",
             "Her hamlenin ardındaki mantığı öğreten ipuçlarıyla klasik sudoku."),
       lead=("Classic 9×9 sudoku with the clutter removed. When you ask for a hint, it explains the reasoning behind the next move instead of only showing the number.",
             "Gereksiz ayrıntıdan arındırılmış klasik 9×9 sudoku. İpucu istediğinde yalnızca sayıyı göstermez, bir sonraki hamlenin mantığını anlatır."),
       feats=[("i-bulb", ("Hints that explain", "Açıklayan ipuçları"),
               ("See why a digit is forced or how a candidate can be ruled out.",
                "Bir rakamın neden zorunlu olduğunu ya da bir adayın nasıl elendiğini gör.")),
              ("i-levels", ("Four difficulty levels", "Dört zorluk seviyesi"),
               ("Every board is verified to have exactly one solution.",
                "Her tahtanın tam olarak tek bir çözümü olduğu doğrulanır.")),
              ("i-grid", ("A calm board", "Sakin bir tahta"),
               ("Rows, columns and 3×3 blocks stay easy to read, so you can focus on the logic.",
                "Satırlar, sütunlar ve 3×3 bloklar kolay okunur; mantığa odaklanabilirsin."))]),
  dict(slug="novaday", name="Novaday", accent="#f0a27f", pat="p-novaday", cat="LifestyleApplication",
       stores={"appstore": "https://apps.apple.com/app/id6791479855",
               "play": "https://play.google.com/store/apps/details?id=app.gungun"},
       sub=("Countdown Days Until", "Kaç Gün Kaldı?"),
       desc=("Count down the days to the moments that matter.",
             "Önemli anlara kalan günleri geri sayın."),
       lead=("Some days are worth counting down to. Name the event, pick the date and Novaday counts the days for you.",
             "Bazı günler saymaya değer. Etkinliğe bir ad ver, tarihi seç; günleri Novaday saysın."),
       feats=[("i-calendar", ("Any day that matters", "Önemli her gün"),
               ("Birthdays, trips, exams, weddings or anything else you are waiting for.",
                "Doğum günleri, yolculuklar, sınavlar, düğünler ya da beklediğin her şey.")),
              ("i-widget", ("Countdown on your home screen", "Ana ekranda geri sayım"),
               ("Keep the days left in view with a countdown widget.",
                "Kalan günleri bir geri sayım widget'ıyla gözünün önünde tut.")),
              ("i-heart", ("A friend to wait with", "Beklerken yanında bir dost"),
               ("A little companion keeps you company while the days go by.",
                "Günler geçerken küçük bir yoldaş sana eşlik eder."))]),
  dict(slug="odak", name="Odak", accent="#8f96b8", pat="p-odak", cat="ProductivityApplication",
       stores={"appstore": "https://apps.apple.com/app/id6771885024",
               "play": "https://play.google.com/store/apps/details?id=com.odakapp.timer"},
       sub=("Flip Clock", "Flip Clock"),
       desc=("A calm full-screen flip clock and focus timer.",
             "Sakin, tam ekran bir flip saat ve odaklanma zamanlayıcısı."),
       lead=("A minimal flip clock and focus timer. Set your time, press play and get on with your work. Odak means focus in Turkish.",
             "Minimal bir flip saat ve odaklanma zamanlayıcısı. Süreni ayarla, başlat ve işine bak. Odak, Türkçede dikkatini bir noktaya vermek demektir."),
       feats=[("i-timer", ("Full-screen flip clock", "Tam ekran flip saat"),
               ("A calm countdown that stays out of your way.",
                "Seni rahatsız etmeyen sakin bir geri sayım.")),
              ("i-palette", ("Five color themes", "Beş renk teması"),
               ("Pick the look that suits your desk or your room.",
                "Masana ya da odana uyan görünümü seç.")),
              ("i-bell", ("A soft bell at the end", "Sonunda yumuşak bir çan"),
               ("A bowl bell sound tells you the session is over.",
                "Bir kase çanı sesi oturumun bittiğini haber verir."))]),
  dict(slug="unitfab", name="UnitFab", accent="#c59a6a", pat="p-unitfab", cat="BusinessApplication",
       stores={"appstore": "https://apps.apple.com/app/id6766839274",
               "play": "https://play.google.com/store/apps/details?id=com.unitfab.app"},
       sub=("Craft Cost Calculator", "Stok Takip Programı"),
       desc=("Cost, pricing and stock tracking for craft workshops.",
             "Atölyeler ve el emeği ürünler için maliyet, fiyatlandırma ve stok takibi."),
       lead=("Cost, pricing, stock and production for handmade products, in one simple app.",
             "El yapımı ürünler için maliyet, fiyatlandırma, stok ve üretim tek basit uygulamada."),
       feats=[("i-calc", ("Cost and profit", "Maliyet ve kâr"),
               ("Add material, labour, shipping and commission costs to a recipe and see the net cost and margin.",
                "Bir tarife malzeme, işçilik, kargo ve komisyon maliyetlerini ekle; net maliyeti ve kâr marjını gör.")),
              ("i-box", ("Stock and production log", "Stok ve üretim kaydı"),
               ("Log a production run and the materials used are deducted from stock.",
                "Bir üretimi kaydet; kullanılan malzemeler stoktan düşer.")),
              ("i-list", ("How many can I make?", "Kaç tane yapabilirim?"),
               ("See how many more units you can make with the stock you have.",
                "Eldeki stokla her üründen kaç tane daha yapabileceğini gör."))]),
  dict(slug="miralo", name="Miralo", accent="#35b6a4", pat="p-miralo", cat="LifestyleApplication",
       stores={"play": "https://play.google.com/store/apps/details?id=com.miralo.app"},
       sub=("Vision Board Maker", "Vizyon Panosu & Kolaj"),
       desc=("Create photo collages and vision boards, then use them as a wallpaper or widget.",
             "Fotoğraf kolajları ve vizyon panoları oluştur, duvar kâğıdı ya da widget olarak kullan."),
       lead=("Pick a template, add your own photos and words, and design a personal board for your goals, plans and favorite things.",
             "Bir şablon seç, kendi fotoğraflarını ve sözlerini ekle; hedeflerin, planların ve sevdiklerin için kişisel bir pano tasarla."),
       feats=[("i-grid", ("Templates or a blank canvas", "Şablon ya da boş tuval"),
               ("Start from a ready-made template or a blank canvas in several sizes.",
                "Hazır bir şablonla ya da farklı boyutlarda boş bir tuvalle başla.")),
              ("i-image", ("Your photos, your words", "Fotoğrafların, sözlerin"),
               ("Crop photos into shapes, add text, then move, scale and rotate each piece.",
                "Fotoğrafları şekillere kırp, metin ekle; her parçayı taşı, ölçekle ve döndür.")),
              ("i-widget", ("Wallpaper or widget", "Duvar kâğıdı ya da widget"),
               ("Use your board as a wallpaper or a home screen widget.",
                "Panonu duvar kâğıdı ya da ana ekran widget'ı olarak kullan."))]),
  dict(slug="collagist", name="Collagist", accent="#6f737c", pat="p-collagist", cat="PhotographyApplication",
       stores={"play": "https://play.google.com/store/apps/details?id=com.collagist.app"},
       sub=("4-Cut Photo Collage", "4 Kare Foto Kolaj"),
       desc=("Seamless carousel slides, retro photo strips and scrapbook collages.",
             "Kesintisiz carousel dilimleri, retro fotoğraf şeritleri ve scrapbook kolajları."),
       lead=("A collage maker for seamless carousel slides, retro photo strips and freeform scrapbook layouts.",
             "Kesintisiz carousel dilimleri, retro fotoğraf şeritleri ve serbest scrapbook düzenleri için kolaj uygulaması."),
       feats=[("i-slides", ("Seamless carousel slides", "Kesintisiz carousel dilimleri"),
               ("Design a wide canvas and split it into slides that line up without seams.",
                "Geniş bir tuval tasarla, dikişsiz hizalanan dilimlere böl.")),
              ("i-strip", ("Retro 4-cut strips", "Retro 4 kare şeritler"),
               ("Vertical photo strips with date stamps, headers and paper borders.",
                "Tarih damgalı, başlıklı ve kâğıt kenarlıklı dikey fotoğraf şeritleri.")),
              ("i-image", ("Freeform scrapbook", "Serbest scrapbook"),
               ("Arrange photos freely for keepsake collages.",
                "Hatıra kolajları için fotoğrafları serbestçe yerleştir."))]),
]

E = html.escape
MARK = '<svg viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#15191f"/><path d="M43 22c0-8-22-8-22 3 0 11 22 5 22 17 0 11-22 10-22 1" fill="none" stroke="#fbfaf8" stroke-width="6.5" stroke-linecap="round"/><circle cx="51" cy="11.5" r="3.8" fill="#f0a27f"/></svg>'

# ───────────── Çizgi simgeler ve motifler ─────────────
def sym(id_, vb, body):
    return f'    <symbol id="{id_}" viewBox="{vb}">{body}</symbol>\n'

ICONS = {
  "i-trace": '<path d="M4 19c3-6 6-2 8-7s5-6 8-7"/><circle cx="20" cy="5" r="1.6"/>',
  "i-star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
  "i-grid": '<rect x="4" y="4" width="16" height="16" rx="2.5"/><path d="M4 9.3h16M4 14.7h16M9.3 4v16M14.7 4v16"/>',
  "i-bulb": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
  "i-levels": '<path d="M5 20v-6M12 20V9M19 20V4"/>',
  "i-calendar": '<rect x="4" y="5" width="16" height="15" rx="3"/><path d="M4 10h16M8 3v4M16 3v4"/>',
  "i-widget": '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
  "i-heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
  "i-timer": '<circle cx="12" cy="13.5" r="7.5"/><path d="M12 13.5V9.5M9.5 2.5h5M12 2.5v3.5"/>',
  "i-palette": '<path d="M12 3a9 9 0 1 0 0 18c1.1 0 1.8-.9 1.5-1.9-.3-1 .4-2.1 1.5-2.1H17a4 4 0 0 0 4-4c0-5-4-10-9-10z"/><path d="M7.5 11h.01M10 7.5h.01M14.5 7.5h.01"/>',
  "i-bell": '<path d="M6 16v-5a6 6 0 0 1 12 0v5l1.5 2h-15zM10 21h4"/>',
  "i-calc": '<rect x="5" y="3" width="14" height="18" rx="3"/><path d="M8.5 7.5h7M8.5 12h.01M12 12h.01M15.5 12h.01M8.5 16h.01M12 16h.01M15.5 16h.01"/>',
  "i-box": '<path d="M12 3l8 4v10l-8 4-8-4V7zM4 7l8 4 8-4M12 11v10"/>',
  "i-list": '<path d="M5 7h14M5 12h14M5 17h9"/>',
  "i-image": '<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="9" cy="10" r="1.8"/><path d="M21 16l-5-5-8 9"/>',
  "i-slides": '<rect x="3" y="6" width="9" height="12" rx="2"/><rect x="12" y="6" width="9" height="12" rx="2"/>',
  "i-strip": '<rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M7 8h10M7 12.5h10M7 17h10"/>',
}
PATTERNS = {
  "p-shapio": '<circle class="m1" cx="34" cy="36" r="15"/><path class="m2" d="M82 20l22 38H60z"/><rect class="m3" x="40" y="76" width="36" height="30" rx="8"/><path d="M34 51v25M70 58l-12 18" stroke-dasharray="3 6"/>',
  "p-sudoku": '<rect x="18" y="18" width="84" height="84" rx="10"/><path d="M46 18v84M74 18v84M18 46h84M18 74h84"/><circle class="m1" cx="60" cy="60" r="9"/>',
  "p-novaday": '<path d="M104 80V44a18 18 0 0 0-18-18H34a18 18 0 0 0-18 18v42a18 18 0 0 0 18 18h38"/><path d="M104 80H90a10 10 0 0 0-10 10v14M104 80L80 104"/><path class="m1" d="M42 18v16M78 18v16"/><circle cx="52" cy="54" r="7.5"/><circle cx="52" cy="76" r="10.5"/><path class="m2" d="M92 50c0-8 4-13 12-14 0 8-4 13-12 14zM92 50v-8"/>',
  "p-odak": '<circle cx="60" cy="60" r="44"/><circle cx="60" cy="60" r="30" stroke-dasharray="2 7"/><path class="m1" d="M60 60V34"/><path class="m2" d="M60 60l20 12"/><path d="M60 12v8M60 100v8M12 60h8M100 60h8"/>',
  "p-unitfab": '<path class="m2" d="M60 14l42 21v50L60 106 18 85V35zM18 35l42 21 42-21M60 56v50"/><path class="m1" d="M38 24l42 21" stroke-dasharray="3 6"/>',
  "p-miralo": '<rect class="m1" x="14" y="22" width="48" height="38" rx="8"/><rect class="m2" x="70" y="14" width="36" height="54" rx="8"/><rect class="m3" x="22" y="68" width="32" height="34" rx="8"/><rect class="m4" x="62" y="76" width="44" height="26" rx="8"/><circle cx="38" cy="41" r="6"/>',
  "p-collagist": '<rect x="38" y="8" width="44" height="104" rx="8"/><rect class="m1" x="46" y="16" width="28" height="20" rx="4"/><rect class="m2" x="46" y="42" width="28" height="20" rx="4"/><rect class="m3" x="46" y="68" width="28" height="20" rx="4"/><rect class="m4" x="46" y="94" width="28" height="12" rx="4"/>',
}

def pat_svg(app):
    return f'<svg class="pat {app["pat"]}" viewBox="0 0 120 120" aria-hidden="true">{PATTERNS[app["pat"]]}</svg>'

def sprite():
    s = '  <!--sprite-->\n  <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n'
    s += '    <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M8 6h10v10h-2V9.41l-9.3 9.3-1.42-1.42L14.59 8H8V6z"/></symbol>\n'
    s += '    <symbol id="i-mail" viewBox="0 0 24 24"><path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm1.6 2 7.4 5.6L19.4 7H4.6z"/></symbol>\n'
    for k, v in ICONS.items():
        s += sym(k, "0 0 24 24", v)
    s += '  </svg>\n  <!--/sprite-->'
    return s

# ───────────── Parçalar ─────────────
def store_links(app, cls="store"):
    out = []
    for key in ("appstore", "play", "huawei"):
        url = app["stores"].get(key)
        if not url:
            continue
        label = STORE_LABEL[key]
        out.append(
          f'<a class="{cls}" href="{E(url)}" aria-label="{app["name"]} on {label}" data-app="{app["name"]}" data-store="{key}">'
          f'{label}<svg class="i" aria-hidden="true"><use href="#i-arrow"/></svg></a>')
    return "\n                ".join(out)

def card(app, i):
    n = app["name"]
    return f'''          <article class="app rise" id="{app["slug"]}" style="--accent:{app["accent"]}; --i:{4 + i}">
            {pat_svg(app)}
            <a href="{app["slug"]}/" tabindex="-1" aria-hidden="true"><img class="app-icon" src="icons/{app["slug"]}.webp" width="108" height="108" alt="{n} icon" data-app="{n}"></a>
            <div class="body">
              <h3>{n}<span class="sr">: </span><span class="sub" data-i18n="{app["slug"]}.sub">{E(app["sub"][0])}</span></h3>
              <p data-i18n="{app["slug"]}.desc">{E(app["desc"][0])}</p>
              <div class="stores">
                {store_links(app)}
                <a class="more" href="{app["slug"]}/" data-more="{n}"><span data-i18n="card.more">Details</span><svg class="i" aria-hidden="true"><use href="#i-arrow"/></svg></a>
              </div>
            </div>
          </article>'''

def cards():
    return "<!--cards-->\n" + "\n\n".join(card(a, i) for i, a in enumerate(APPS)) + "\n          <!--/cards-->"

def js_dict(d):
    return "{\n" + ",\n".join(f"        {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in d.items()) + "\n      }"

COMMON_TR = {
  "nav.contact": "İletişim",
  "page.back": "Tüm uygulamalar",
  "page.others": "Diğer uygulamalar",
  "card.more": "Ayrıntılar",
  "contact.title": "Soru, destek ya da geri bildirim?",
  "contact.text": "Bana yazın, yardımcı olmaktan memnuniyet duyarım.",
  "footer.legal": "App Store, Apple Inc.'in hizmet markasıdır. Google Play, Google LLC'nin ticari markasıdır. Sirin Apps, Apple veya Google ile bağlantılı değildir ve bunlar tarafından onaylanmamıştır.",
}

def favicon_line():
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    return re.search(r'  <link rel="icon" href="data:[^\n]+\n', src).group(0)

def page(app):
    n, slug = app["name"], app["slug"]
    title_en = f'{n}: {app["sub"][0]} — Sirin Apps'
    title_tr = f'{n}: {app["sub"][1]} — Sirin Apps'
    url = f"{SITE}/{slug}/"
    tr = dict(COMMON_TR)
    tr[f"{slug}.sub"] = app["sub"][1]
    tr[f"{slug}.lead"] = app["lead"][1]
    feats_html = ""
    for j, (icon, t, d) in enumerate(app["feats"], 1):
        tr[f"{slug}.f{j}t"], tr[f"{slug}.f{j}d"] = t[1], d[1]
        feats_html += f'''        <div class="feat">
          <svg viewBox="0 0 24 24" aria-hidden="true"><use href="#{icon}"/></svg>
          <h3 data-i18n="{slug}.f{j}t">{E(t[0])}</h3>
          <p data-i18n="{slug}.f{j}d">{E(d[0])}</p>
        </div>
'''
    others = "".join(
      f'          <li><a href="../{a["slug"]}/"><img src="../icons/{a["slug"]}.webp" width="44" height="44" alt="">{a["name"]}</a></li>\n'
      for a in APPS if a["slug"] != slug)
    ld = {
      "@context": "https://schema.org", "@type": "MobileApplication", "name": n,
      "description": app["lead"][0], "applicationCategory": app["cat"],
      "operatingSystem": " / ".join(sorted({STORE_OS[k] for k in app["stores"]})),
      "url": url, "image": f"{SITE}/icons/{slug}.webp",
      "author": {"@type": "Person", "name": OWNER},
    }
    meta = {"desc": {"en": app["lead"][0], "tr": app["lead"][1]}, "title": {"en": title_en, "tr": title_tr}}
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(title_en)}</title>
  <meta name="description" content="{E(app["lead"][0])}">
  <link rel="canonical" href="{url}">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#fbfaf8" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0c0f14" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Sirin Apps">
  <meta property="og:title" content="{E(title_en)}">
  <meta property="og:description" content="{E(app["lead"][0])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/icons/{slug}.webp">
  <meta name="twitter:card" content="summary">
{favicon_line()}  <link rel="preload" href="../fonts/bricolage-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../assets/site.css">
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body class="sub-page">
{sprite()}

  <div class="wrap">
    <header class="top">
      <a class="brand" href="../" aria-label="Sirin Apps"><span class="mark" aria-hidden="true">{MARK}</span>Sirin Apps</a>
      <div class="top-actions">
        <div class="lang" role="group" aria-label="Language">
          <button type="button" data-lang="en" lang="en" aria-label="English" aria-pressed="true">EN</button>
          <button type="button" data-lang="tr" lang="tr" aria-label="Türkçe" aria-pressed="false">TR</button>
        </div>
        <a class="btn ghost small" href="../#contact" data-i18n="nav.contact">Contact</a>
      </div>
    </header>

    <main id="top">
      <a class="crumb" href="../#apps"><svg class="i" aria-hidden="true"><use href="#i-arrow"/></svg><span data-i18n="page.back">All apps</span></a>

      <section class="page-hero rise" style="--accent:{app["accent"]}">
        {pat_svg(app)}
        <img class="app-icon" src="../icons/{slug}.webp" width="168" height="168" alt="{n} icon" data-app="{n}">
        <div>
          <h1>{n}<span class="sr">: </span><span class="sub" data-i18n="{slug}.sub">{E(app["sub"][0])}</span></h1>
          <p class="lead" data-i18n="{slug}.lead">{E(app["lead"][0])}</p>
          <div class="stores">
            {store_links(app)}
          </div>
        </div>
      </section>

      <section class="features rise" style="--accent:{app["accent"]}; --i:2">
{feats_html}      </section>

      <section class="others">
        <h2 data-i18n="page.others">More apps</h2>
        <ul>
{others}        </ul>
      </section>

      <section id="contact">
        <div class="contact">
          <div>
            <h2 data-i18n="contact.title">Questions, support or feedback?</h2>
            <p data-i18n="contact.text">Write to me — I'm happy to help.</p>
          </div>
          <a class="btn" href="mailto:yusufsirindev@icloud.com"><svg class="i"><use href="#i-mail"/></svg>yusufsirindev@icloud.com</a>
        </div>
      </section>
    </main>

    <footer>
      <p>© 2026 {OWNER} · Türkiye</p>
      <p class="legal" data-i18n="footer.legal">App Store is a service mark of Apple Inc. Google Play is a trademark of Google LLC. Sirin Apps is not affiliated with or endorsed by Apple or Google.</p>
    </footer>
  </div>
  <script>
    window.SIRIN_TR = {js_dict(tr)};
    window.SIRIN_META = {json.dumps(meta, ensure_ascii=False)};
  </script>
  <script src="../assets/site.js"></script>
</body>
</html>
'''

def replace_block(src, name, new):
    pat = re.compile(rf"[ ]*<!--{name}-->.*?<!--/{name}-->", re.S)
    assert pat.search(src), name
    return pat.sub(lambda m: new if name == "sprite" else "          " + new.lstrip(), src, count=1)

def main():
    for a in APPS:
        d = os.path.join(ROOT, a["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(a))
    p = os.path.join(ROOT, "index.html")
    src = open(p, encoding="utf-8").read()
    src = replace_block(src, "sprite", sprite())
    src = replace_block(src, "cards", cards())
    open(p, "w", encoding="utf-8").write(src)
    urls = [f"{SITE}/"] + [f"{SITE}/{a['slug']}/" for a in APPS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("ok:", len(APPS), "sayfa")

if __name__ == "__main__":
    main()
