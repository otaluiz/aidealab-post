// ENCAIXE DA SCRIPT NO MONUMENTO (arquivo historicamente chamado "anticolisao").
//
// ============================================================================
// O QUE ESTE ARQUIVO FAZ AGORA (e por que mudou)
// ============================================================================
//
// REGRA DA CASA, medida em peca aprovada real (pixel a pixel, 1080x1440):
//
//   a BASELINE da script cai EM CIMA do topo das caixas altas (capTop) do
//   monumento -- diferenca ZERO, nao "um vao pequeno".
//
//   Concorrente-Comunica-Melhor / 01_cro_1_hook.png : baseline 881 | capTop 883  -> -2px
//   2026-08-27_3-sites-fontes-vinho / 01_capa.png   : baseline 832 | capTop 833  -> -1px
//
//   Consequencia direta: a TINTA da script (descendentes, lacos, cedilha)
//   MERGULHA dentro da faixa de caixa alta do monumento. Na capa FONTES o
//   laco do "O" desce ate y=844, 11px ABAIXO do topo do "F" (833). Isso nao e
//   colisao -- e o lockup. E o que o cliente chama de "colado".
//
// O QUE ESTE ARQUIVO FAZIA ANTES, E POR QUE NUNCA COLAVA:
//
//   Ele era um GRAMPO DE UMA VIA SO:
//       sobra = scriptInkBottom + folga - monumentInkTop;
//       if (sobra > 0) s.style.top -= sobra;     // <= so SOBE. Nunca desce.
//
//   Tres defeitos empilhados, os tres confirmados rodando o build real em
//   Chrome headless (teste-referencia-automacao-com-criterio, 2026-09-19):
//
//   (1) RAIZ. A formula de encaixe documentada no SKILL.md ("script.top =
//       capTopDoMonumento - baselineDaScriptNaCaixa") NUNCA era aplicada por
//       ninguem -- nem por CSS, nem por template, nem por este arquivo. A
//       script ficava onde o `margin-bottom: 2px` do CSS a deixasse, ~30px
//       acima do alvo, e este grampo so sabia AFASTAR mais. Medido:
//         01_hook (SPAM., sem acento) -> retorno 0, top intacto em "0px",
//                                        baseline 991.3 vs capTop 1025 = -33.7px
//         06_cta  (COM CRITERIO.)     -> retorno 4, top 0 -> -4.28px,
//                                        baseline 1018.9 vs capTop 1048.9 = -30px
//       Ou seja: no hook o grampo foi NO-OP puro e a peca saiu 34px errada;
//       no CTA ele ainda PIOROU 4px. Mexer em `folga` jamais consertaria isso.
//
//   (2) Medir o ascent da PALAVRA INTEIRA (com acento) em vez de sondar "H"
//       supercorrige em monumento acentuado -- exatamente o que o SKILL.md ja
//       mandava evitar, e que este arquivo contrariava. Em "COM CRITERIO." o
//       agudo do E sobe 28px acima do capTop; com a palavra inteira o grampo
//       calculava sobra ~32px em vez de 4px, jogando a script 28px mais longe
//       ainda. Agora o topo do monumento SEMPRE vem da sonda "H".
//
//   (3) `folga = 16` pedia 16px de AR entre a tinta descendente da script e a
//       faixa de caixa alta do monumento. Isso e logicamente incompativel com
//       a regra da casa: quando baseline == capTop, a tinta descendente esta
//       por definicao DENTRO da faixa, entao `sobra = descent + 16 > 0`
//       dispararia SEMPRE, desfazendo o encaixe correto em toda peca. Um vao
//       positivo obrigatorio e o oposto do padrao aprovado. `folga` morreu.
//
// ============================================================================
// COMO FUNCIONA
// ============================================================================
//
// Passo unico e com SINAL (sobe OU desce):
//     delta = capTopDoMonumento - baselineDaScript
//     script.top += delta - lift
//
// - baseline dentro da caixa de linha = top + (alturaDaLinha - (fontAscent +
//   fontDescent)) / 2 + fontAscent, com os valores de `fontBoundingBox*` do
//   canvas (a caixa de linha e centrada no bloco de fonte).
// - capTop = baselineDoMonumento - actualBoundingBoxAscent sondando "H".
//   Sempre "H": til, cedilha e agudo (AUTOMACAO, CRITERIO) inflam a medida da
//   palavra e mudariam o encaixe de uma palavra para outra.
// - Mede por LINHA (getClientRects), nao pela uniao das linhas: a script usa a
//   ULTIMA linha (e ela que encosta), o monumento usa a PRIMEIRA. A versao
//   antiga usava getBoundingClientRect e calculava a baseline a partir da
//   altura somada -- errado assim que qualquer um dos dois quebrasse em duas
//   linhas.
// - Como `.script` e posicionada (relative/absolute), mover o `top` dela nao
//   mexe no fluxo: o monumento fica onde esta e so a script desce/sobe. Por
//   isso uma passada basta; a funcao ainda assim re-mede e devolve `residual`.
//
// `lift` e ESCAPE HATCH MANUAL, default 0 -- nunca automatico. A formula pura
// ja entrega o toque leve sozinha (e a ponta do descendente que deita no topo
// do bold, o corpo da palavra nao cobre letra nenhuma). So passe lift > 0
// quando a peca REALMENTE colidir a olho. Qualquer regra automatica do tipo
// "sobe se o acento passa da tinta da script" dispara sempre, porque com
// baseline == capTop o acento esta sempre acima da tinta -- foi esse raciocinio
// que produziu o grampo antigo.
//
// CONTRATO DE DOM: precisam existir `.script` e `.mono`, e precisam SER os
// elementos que carregam o texto (nao wrappers em volta deles). Se faltar um
// dos dois a funcao LANCA erro -- antes ela retornava null em silencio e a
// peca saia publicada com o vao. Se `.script` estiver `position: static` ou
// sem `top` inline, a funcao mesma resolve (aplica `position: relative` e
// `top: 0px`) em vez de desistir calada.
//
// ASSINATURA: window.__anticolisao({ lift: 0 })  ->  objeto de diagnostico.
// Chamadas legadas `window.__anticolisao(16)` passavam a antiga `folga`; o
// numero e IGNORADO de proposito (com aviso no console), para que build antigo
// re-renderizado ja saia no padrao novo. Para levantar de verdade: { lift: N }.
window.__anticolisao = function (opts) {
  if (typeof opts === 'number') {
    if (typeof console !== 'undefined' && console.warn) {
      console.warn('[encaixe] argumento numerico e a antiga "folga" e foi ignorado. ' +
                   'Use __anticolisao({ lift: N }) — lift e escape hatch manual, default 0.');
    }
    opts = null;
  }
  opts = opts || {};
  var lift = opts.lift || 0;

  function ctxFont(cs) {
    return cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
  }

  // Caixa de UMA linha: 'last' para a script (a linha que encosta no bold),
  // 'first' para o monumento (a linha que recebe a script).
  function lineRect(el, which) {
    var r = document.createRange();
    r.selectNodeContents(el);
    var rects = r.getClientRects();
    if (!rects || !rects.length) return el.getBoundingClientRect();
    return which === 'first' ? rects[0] : rects[rects.length - 1];
  }

  function metrics(el, which) {
    var cs = getComputedStyle(el);
    var box = lineRect(el, which);
    var c = document.createElement('canvas').getContext('2d');
    c.font = ctxFont(cs);
    // text-transform muda o desenho (e a altura do acento) mas nao o
    // textContent -- sem normalizar, a medida sai da caixa baixa.
    var txt = el.textContent.trim();
    if (!txt) {
      var vazio = '[encaixe] elemento sem texto (' + (el.className || el.tagName) +
                  '). Medir string vazia devolveria residual 0 falso.';
      if (typeof console !== 'undefined' && console.error) console.error(vazio);
      throw new Error(vazio);
    }
    if (cs.textTransform === 'uppercase') txt = txt.toUpperCase();
    else if (cs.textTransform === 'lowercase') txt = txt.toLowerCase();
    var m = c.measureText(txt);
    var mH = c.measureText('H');
    var fa = m.fontBoundingBoxAscent, fd = m.fontBoundingBoxDescent;
    var baseline = box.top + (box.height - (fa + fd)) / 2 + fa;
    return {
      baseline: baseline,
      capTop: baseline - mH.actualBoundingBoxAscent,   // sonda "H", nunca a palavra
      inkTopWord: baseline - m.actualBoundingBoxAscent, // so diagnostico (acento)
      inkBottom: baseline + m.actualBoundingBoxDescent
    };
  }

  var s = document.querySelector('.script');
  var mo = document.querySelector('.mono');
  if (!s || !mo) {
    var falta = '[encaixe] faltou ' + (!s ? '.script' : '') + (!s && !mo ? ' e ' : '') +
                (!mo ? '.mono' : '') + ' — .script e .mono precisam SER os elementos ' +
                'de texto, nao wrappers. A peca vai sair com o vao.';
    // console.error ANTES do throw: a chamada normalmente vive dentro de um
    // document.fonts.ready.then(), onde um throw vira unhandled rejection e
    // pode passar batido na captura. O log garante que aparece.
    if (typeof console !== 'undefined' && console.error) console.error(falta);
    throw new Error(falta);
  }
  if (getComputedStyle(s).position === 'static') s.style.position = 'relative';
  if (!s.style.top) s.style.top = '0px';

  var S = metrics(s, 'last');
  var M = metrics(mo, 'first');

  // Encaixe com sinal: desce quando a script esta alta, sobe quando esta baixa.
  var delta = M.capTop - S.baseline;
  var topAntes = parseFloat(s.style.top) || 0;
  s.style.top = (topAntes + delta - lift) + 'px';

  // ORDEM: o encaixe depende do corpo FINAL do monumento, entao tem que rodar
  // depois do fit de largura. Em vez de so pedir isso na prosa (e deixar a peca
  // sair torta em silencio se alguem inverter), o proprio arquivo se protege:
  // observa o monumento e refaz o encaixe se o corpo dele mudar depois. Nao ha
  // risco de loop -- o encaixe so escreve em `.script`, nunca em `.mono`.
  if (!mo.__encaixeObs && typeof MutationObserver !== 'undefined') {
    var last = getComputedStyle(mo).fontSize;
    mo.__encaixeObs = new MutationObserver(function () {
      var now = getComputedStyle(mo).fontSize;
      if (now === last) return;
      last = now;
      window.__anticolisao({ lift: lift });
    });
    mo.__encaixeObs.observe(mo, { attributes: true, attributeFilter: ['style', 'class'] });
  }

  var S2 = metrics(s, 'last');
  return {
    moveu: Math.round((delta - lift) * 100) / 100,   // px aplicados (+ desce, - sobe)
    topAntes: topAntes,
    topDepois: parseFloat(s.style.top),
    lift: lift,
    // residual ~0 confirma o encaixe. Este e o numero a auditar.
    residual: Math.round((S2.baseline - M.capTop + lift) * 100) / 100,
    capTopMonumento: Math.round(M.capTop * 100) / 100,
    baselineScript: Math.round(S2.baseline * 100) / 100,
    // Diagnostico para decidir `lift` A MAO (nunca automatico):
    // quanto a tinta da script mergulha na faixa de caixa alta...
    mergulhoDaScript: Math.round((S2.inkBottom - M.capTop) * 100) / 100,
    // ...e quanto o acento do monumento sobe acima do capTop.
    acentoAcimaDoCapTop: Math.round((M.capTop - M.inkTopWord) * 100) / 100
  };
};
