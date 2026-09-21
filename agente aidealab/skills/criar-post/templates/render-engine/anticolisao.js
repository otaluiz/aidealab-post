// ANTICOLISAO SCRIPT x PALAVRA GRANDE.
//
// O par da casa e Tempting (descida longa, com laco) sobre Inter 900 com
// line-height .84. Duas coisas invisiveis na marcacao se encontram: a descida
// do 'g'/'p'/'f' da script desce ALEM da caixa de linha dela, e o acento de
// "invisivel"/"BORRAO" sobe ALEM da caixa da palavra -- line-height menor que 1
// deixa a tinta vazar para fora da caixa nos dois lados. Resultado: o laco da
// script cruza o acento e o lettering fica sujo.
//
// Nao da para resolver escolhendo um vao fixo: cada palavra tem uma altura de
// tinta diferente (acento ou nao, descida ou nao). Entao a peca mede a TINTA
// real -- actualBoundingBoxAscent/Descent do canvas -- e sobe a linha script ate
// limpar. Verificacao obrigatoria em toda peca com script sobre palavra grande.
//
// CONTRATO DE DOM (nao documentado antes, achado quebrando silenciosamente em
// producao): .script e .mono precisam SER os elementos posicionados, cada um
// com style.top JA definido inline antes de chamar esta funcao -- nao
// wrappers em volta deles. Se qualquer um dos dois nao tiver s.style.top
// (string vazia conta como ausente), a funcao retorna null sem lançar erro
// e sem mover nada -- exatamente o tipo de falha silenciosa que o resto da
// skill alerta em outro lugar ("quebra o lockup sem avisar").
window.__anticolisao = function (folga) {
  folga = folga || 16;
  function tinta(el) {
    var cs = getComputedStyle(el);
    var r = document.createRange(); r.selectNodeContents(el);
    var caixa = r.getBoundingClientRect();
    var c = document.createElement('canvas').getContext('2d');
    c.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
    // text-transform:uppercase muda o desenho (e a altura do acento) mas nao o
    // textContent -- sem isso a medicao usa a caixa baixa (mais curta) e o
    // clearance sai insuficiente para o acento maiusculo real.
    var txt = el.textContent.trim();
    if (cs.textTransform === 'uppercase') txt = txt.toUpperCase();
    else if (cs.textTransform === 'lowercase') txt = txt.toLowerCase();
    var m = c.measureText(txt);
    var fa = m.fontBoundingBoxAscent, fd = m.fontBoundingBoxDescent;
    // a caixa de linha e centrada no bloco de fonte; dai sai a linha de base
    var base = caixa.top + (caixa.height - (fa + fd)) / 2 + fa;
    return { topo: base - m.actualBoundingBoxAscent, base: base + m.actualBoundingBoxDescent };
  }
  var s = document.querySelector('.script'), m = document.querySelector('.mono');
  if (!s || !m || !s.style.top) return null;
  var a = tinta(s), b = tinta(m);
  var sobra = a.base + folga - b.topo;
  if (sobra > 0) s.style.top = (parseFloat(s.style.top) - sobra) + 'px';
  return Math.max(0, Math.round(sobra));
};
