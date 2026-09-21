// Ajusta o monumento (.mono) a uma LARGURA-ALVO em px, medindo o span .mword
// (nao o bloco .mono, que e full-width). Roda ANTES do encaixe.js/anticolisao.js
// -- e o tamanho final da palavra que decide onde a script encosta.
window.__fitMonoWidth = function (targetWidth) {
  var mono = document.querySelector('.mono');
  var word = mono.querySelector('.mword');
  var lo = 20, hi = 400, size = 200;
  for (var i = 0; i < 26; i++) {
    size = (lo + hi) / 2;
    mono.style.fontSize = size + 'px';
    var w = word.getBoundingClientRect().width;
    if (w > targetWidth) hi = size; else lo = size;
  }
  mono.style.fontSize = lo + 'px';
  return Math.round(word.getBoundingClientRect().width);
};
