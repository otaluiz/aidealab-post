// Encaixe script(Tempting) x monumento(Inter 900) — formula do SKILL.md (Etapa 4,
// "O encaixe da script no monumento e CALCULADO em runtime"), nao top/margin fixo.
//
// Regra: a baseline da script cai no topo das caixas altas (cap-top) do monumento,
// data-lift=0, sem fudge manual. Isso entrega sozinho o leve mergulho de -15/-25px
// que a casa usa (Concorrente-Comunica-Melhor, Testa-uma-DUPLA) porque os
// descendentes da script (ex.: "p" de "soa a", "de escrever") cruzam por cima do
// cap-top do monumento — o corpo da palavra sem descendente fica encostado sem
// cobrir letra nenhuma.
//
// Mede pelo `H` do monumento (nunca a palavra inteira — til/cedilha como o Ô de
// ROBÔ infla actualBoundingBoxAscent e o encaixe sairia com folga falsa).
window.__encaixe = function () {
  var out = [];
  document.querySelectorAll('.t-lockup').forEach(function (wrap) {
    var s = wrap.querySelector('.script');
    var m = wrap.querySelector('.mono');
    if (!s || !m) return;

    function metrics(el, capProbe) {
      var cs = getComputedStyle(el);
      var c = document.createElement('canvas').getContext('2d');
      c.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
      var fm = c.measureText(capProbe || 'H');
      return {
        ascent: fm.fontBoundingBoxAscent,
        descent: fm.fontBoundingBoxDescent,
        capAscent: fm.actualBoundingBoxAscent,
        lineHeight: parseFloat(cs.lineHeight) || (fm.fontBoundingBoxAscent + fm.fontBoundingBoxDescent) * 1.15
      };
    }

    // topo do container (.t-lockup), origem para os `top` absolutos dos filhos
    var wrapTop = wrap.getBoundingClientRect().top;

    // --- monumento: cap-top medido pelo 'H' (nunca a palavra inteira) ---
    var mCS = getComputedStyle(m);
    var mLH = parseFloat(mCS.lineHeight);
    if (isNaN(mLH)) { mLH = parseFloat(mCS.fontSize) * 1.15; }
    var mMet = metrics(m, 'H');
    var mTopPx = parseFloat(m.style.top) || 0;
    // baseline do monumento dentro da SUA caixa de linha
    var mBaselineInBox = (mLH - (mMet.ascent + mMet.descent)) / 2 + mMet.ascent;
    // cap-top real (topo da tinta de 'H'), relativo ao topo do container
    var monCapTop = mTopPx + mBaselineInBox - mMet.capAscent;

    // --- script: baseline dentro da SUA caixa de linha ---
    var sCS = getComputedStyle(s);
    var sLH = parseFloat(sCS.lineHeight);
    if (isNaN(sLH)) { sLH = parseFloat(sCS.fontSize) * 1.15; }
    var sMet = metrics(s, s.textContent.trim());
    var sBaselineInBox = (sLH - (sMet.ascent + sMet.descent)) / 2 + sMet.ascent;

    // script.top = capTopDoMonumento - baselineDaScriptNaCaixa (formula do SKILL.md)
    var newTop = monCapTop - sBaselineInBox;
    s.style.top = newTop + 'px';

    out.push({
      mono_capTop_relwrap: Math.round(monCapTop),
      script_top_set: Math.round(newTop)
    });
  });
  return out;
};
