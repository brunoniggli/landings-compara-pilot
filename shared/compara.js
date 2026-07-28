/* =====================================================================
   Compara — Comportamientos compartidos
   nav sólido, reveals, luz del hero, carrusel de productos, marquee de
   aseguradoras y demo de chat. Cada módulo se autoactiva SOLO si su
   elemento existe en la página, así una landing simple no rompe.
   Requiere Lucide cargado antes (para los iconos de UI).
   ===================================================================== */
(function(){
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var isDesktop = finePointer && window.matchMedia('(min-width: 861px)').matches;
  var EASE = 'cubic-bezier(0.22, 0.61, 0.36, 1)';

  function icons(){ if (window.lucide) lucide.createIcons({attrs:{'stroke-width':1.75}}); }
  document.addEventListener('DOMContentLoaded', icons);
  window.addEventListener('load', icons);

  /* ---------- Nav: estado sólido (sentinela + IO) ------------------- */
  var nav = document.getElementById('nav');
  if (nav){
    var sentinel = document.createElement('div');
    sentinel.style.cssText = 'position:absolute;top:0;height:48px;width:1px;';
    document.body.prepend(sentinel);
    new IntersectionObserver(function(entries){
      entries[0].isIntersecting ? nav.removeAttribute('data-solid') : nav.setAttribute('data-solid','');
    }).observe(sentinel);
  }

  /* ---------- Nav móvil --------------------------------------------- */
  var burger = document.getElementById('burger');
  var panel = document.getElementById('navPanel');
  if (burger && panel){
    burger.addEventListener('click', function(){
      var open = panel.hasAttribute('data-open');
      panel.toggleAttribute('data-open', !open);
      burger.setAttribute('aria-expanded', String(!open));
    });
    panel.addEventListener('click', function(e){
      if (e.target.tagName === 'A'){ panel.removeAttribute('data-open'); burger.setAttribute('aria-expanded','false'); }
    });
  }

  /* ---------- Reveals por IO ----------------------------------------- */
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if (en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); }
    });
  }, {threshold:.2, rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.reveal, .step').forEach(function(el){ io.observe(el); });
  requestAnimationFrame(function(){
    document.querySelectorAll('.reveal:not(.in)').forEach(function(el){
      if (el.getBoundingClientRect().bottom < 0) el.classList.add('in');
    });
  });

  /* ---------- Hero: luz que sigue al cursor (solo desktop) ----------- */
  var hero = document.getElementById('hero');
  var glow = document.getElementById('heroGlow');
  if (hero && glow && !reduce && isDesktop){
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null, heroOn = false;
    function loop(){
      cx += (tx - cx) * 0.036;   /* 20% más lento que antes (0.045) */
      cy += (ty - cy) * 0.036;
      glow.style.transform = 'translate3d(' + cx + 'px,' + cy + 'px,0)';
      if (Math.abs(tx - cx) > .4 || Math.abs(ty - cy) > .4 || heroOn){ raf = requestAnimationFrame(loop); }
      else { raf = null; }
    }
    hero.addEventListener('pointermove', function(e){
      var r = hero.getBoundingClientRect();
      tx = e.clientX - r.left; ty = e.clientY - r.top;
      if (!raf) raf = requestAnimationFrame(loop);
    });
    hero.addEventListener('pointerenter', function(){ heroOn = true; hero.setAttribute('data-glow',''); });
    hero.addEventListener('pointerleave', function(){ heroOn = false; hero.removeAttribute('data-glow'); });
  }

  /* ---------- Hero: pulso al click/tap (desktop + mobile) ------------ */
  if (hero && !reduce){
    hero.addEventListener('click', function(e){
      if (e.target.closest('a, button')) return;
      var r = hero.getBoundingClientRect();
      var p = document.createElement('span');
      p.className = 'hero-pulse';
      p.style.left = (e.clientX - r.left) + 'px';
      p.style.top = (e.clientY - r.top) + 'px';
      hero.appendChild(p);
      p.animate(
        [{transform:'scale(1)', opacity:.8},{transform:'scale(16)', opacity:0}],
        {duration:800, easing:EASE, fill:'forwards'}
      ).onfinish = function(){ p.remove(); };
    });
  }

  /* ---------- Hero: CTA de producto clickeado cambia de color -------- */
  if (hero){
    var hpBtns = Array.prototype.slice.call(hero.querySelectorAll('.hp-btn'));
    hpBtns.forEach(function(b){
      b.addEventListener('click', function(e){
        var href = b.getAttribute('href');
        if (href && href !== '#') return; /* enlaces reales (p.ej. Auto → auto.html) navegan normal */
        e.preventDefault(); /* placeholders (#): solo marcan activo, no navegan */
        hpBtns.forEach(function(x){ x.classList.remove('is-active'); });
        b.classList.add('is-active');
      });
    });
  }

  /* ---------- Productos: carrusel que sigue al cursor (solo desktop) -- */
  var prodSec = document.getElementById('productos');
  var hwrap = document.getElementById('hwrap');
  var htrack = document.getElementById('htrack');
  if (prodSec && hwrap && htrack && isDesktop && !reduce){
    prodSec.classList.add('pan-hover');
    var pFill = prodSec.querySelector('.pan-progress i');
    var pDist = 0, pTarget = 0, pCur = 0, pRaf = null;
    function pMeasure(){
      pDist = Math.max(0, hwrap.scrollWidth - hwrap.clientWidth);
      pTarget = Math.min(pTarget, pDist);
    }
    function pLoop(){
      pCur += (pTarget - pCur) * 0.055;
      if (Math.abs(pTarget - pCur) < .3) pCur = pTarget;
      htrack.style.transform = 'translate3d(' + (-pCur) + 'px,0,0)';
      if (pFill && pDist > 0) pFill.style.transform = 'scaleX(' + (pCur / pDist) + ')';
      pRaf = (pCur !== pTarget) ? requestAnimationFrame(pLoop) : null;
    }
    function pGo(t){
      pTarget = Math.max(0, Math.min(pDist, t));
      if (!pRaf) pRaf = requestAnimationFrame(pLoop);
    }
    hwrap.addEventListener('pointermove', function(e){
      var r = hwrap.getBoundingClientRect();
      var ratio = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
      pGo(ratio * pDist);
    });
    hwrap.addEventListener('focusin', function(e){
      var card = e.target.closest('.pcard');
      if (card) pGo(card.getBoundingClientRect().left - hwrap.getBoundingClientRect().left + pCur - 80);
    });
    pMeasure();
    window.addEventListener('resize', pMeasure);
    window.addEventListener('load', pMeasure);
  }

  /* ---------- Aseguradoras: marquee en mobile (clones para loop) ----- */
  var cloud = document.getElementById('logoCloud');
  if (cloud){
    var mqMobile = window.matchMedia('(max-width: 860px)');
    var originals = Array.prototype.slice.call(cloud.children);
    var setInsurers = function(){
      var isMob = mqMobile.matches;
      Array.prototype.slice.call(cloud.querySelectorAll('[data-clone]')).forEach(function(c){ c.remove(); });
      cloud.classList.toggle('logo-cloud--marquee', isMob && !reduce);
      if (isMob){
        originals.forEach(function(o){ o.classList.add('in'); });
        if (!reduce){
          originals.forEach(function(o){
            var c = o.cloneNode(true);
            c.setAttribute('data-clone',''); c.setAttribute('aria-hidden','true'); c.classList.add('in');
            cloud.appendChild(c);
          });
        }
      }
    };
    setInsurers();
    if (mqMobile.addEventListener) mqMobile.addEventListener('change', setInsurers);
  }

  /* ---------- Demo de chat Comparini (copy aprobado) ------------------ */
  var chatBody = document.getElementById('chatBody');
  var chatEl = document.getElementById('chat');
  if (chatBody && chatEl){
    var SCRIPT = [
      {who:'user', text:'Necesito un seguro barato pero bueno', wait:900},
      {who:'typing', wait:1300},
      {who:'bot', text:'Entiendo. Quieres el mejor precio sin sacrificar coberturas importantes. ¿Qué es lo que más te preocupa que pase con tu auto?', wait:2100},
      {who:'user', text:'Que me lo roben', wait:900},
      {who:'typing', wait:1500},
      {who:'bot', text:'Esta opción cuesta $18.500 al mes y cubre robo total, choque y daños a terceros hasta USD 50.000. El deducible es UF 10. ¿La comparamos con otras dos?', wait:4200}
    ];
    var bubble = function(step){
      var el = document.createElement('div');
      if (step.who === 'typing'){
        el.className = 'bubble bubble--bot bubble--typing';
        el.innerHTML = '<i></i><i></i><i></i>';
      } else {
        el.className = 'bubble bubble--' + step.who;
        el.textContent = step.text;
      }
      chatBody.appendChild(el);
      if (!reduce){
        el.animate(
          [{opacity:0, transform:'translateY(8px) scale(.97)'},{opacity:1, transform:'translateY(0) scale(1)'}],
          {duration:280, easing:EASE, fill:'backwards'}
        );
      }
      return el;
    };
    var chatVisible = false, chatStep = 0, chatTimer = null, typingEl = null;
    var chatNext = function(){
      if (!chatVisible || document.hidden){ chatTimer = setTimeout(chatNext, 800); return; }
      if (typingEl){ typingEl.remove(); typingEl = null; }
      if (chatStep >= SCRIPT.length){
        var olds = Array.prototype.slice.call(chatBody.children);
        if (!reduce){
          olds.forEach(function(o){ o.animate([{opacity:1},{opacity:0}], {duration:240, easing:'ease-out', fill:'forwards'}); });
          setTimeout(function(){ chatBody.innerHTML = ''; chatStep = 0; chatNext(); }, 300);
        } else {
          chatBody.innerHTML = ''; chatStep = 0; chatTimer = setTimeout(chatNext, 600);
        }
        return;
      }
      var step = SCRIPT[chatStep++];
      var el = bubble(step);
      if (step.who === 'typing') typingEl = el;
      chatTimer = setTimeout(chatNext, step.wait);
    };
    if (reduce){
      SCRIPT.filter(function(s){ return s.who !== 'typing'; }).forEach(bubble);
    } else {
      new IntersectionObserver(function(en){
        chatVisible = en[0].isIntersecting;
        if (chatVisible && chatTimer === null) chatNext();
      }, {threshold:.35}).observe(chatEl);
    }
  }

  /* ---------- CTA sticky (mobile): aparece al perder de vista el CTA del hero,
       se oculta al llegar al CTA final. Visibilidad real la controla el CSS
       (solo <=860px). Se autoactiva solo si existe .cta-sticky. --------------- */
  var sticky = document.querySelector('.cta-sticky');
  if (sticky && 'IntersectionObserver' in window){
    var heroCtaEl = document.querySelector('.hero .hero-cta');
    var closerEl = document.querySelector('.closer');
    var heroCtaSeen = !!heroCtaEl;   /* al tope de la pagina el CTA del hero se ve */
    var closerSeen = false;
    var syncSticky = function(){ sticky.classList.toggle('is-visible', !heroCtaSeen && !closerSeen); };
    if (heroCtaEl){
      new IntersectionObserver(function(e){ heroCtaSeen = e[0].isIntersecting; syncSticky(); }, {threshold:0}).observe(heroCtaEl);
    } else {
      heroCtaSeen = false; /* sin CTA de hero, el sticky puede mostrarse */
    }
    if (closerEl){
      new IntersectionObserver(function(e){ closerSeen = e[0].isIntersecting; syncSticky(); }, {threshold:0}).observe(closerEl);
    }
    syncSticky();
  }
})();
