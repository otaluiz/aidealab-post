---
name: humanizer-aidealab
description: Camada em português da aidealab aplicada depois da skill humanizer: acentuação, voz da casa e checagens de carrossel. Use em slides, legenda e primeiro comentário, depois do copy-aidealab e antes de renderizar.
---

# humanizer-aidealab

Primeiro rode a skill `humanizer` (original, em `.claude/skills/humanizer/`) em modo embutido: devolva só o texto final. As construções em inglês dela (not X but Y, fecho de uma linha, tríade, travessão) valem igual em português ("não é X, é Y", "não é só X, é Y"). Depois aplique as checagens abaixo, que são específicas da casa e valem acima da humanizer em caso de conflito.

Releia cada string (slides, legenda, primeiro_comentario, alt, CTA) e corrija:

1. **Acentos.** Português sem acento fora do `.script` é defeito bloqueante (voce, nao, ja, proxima, mao, so, ate). Só a linha `.script` do hook/CTA é escrita sem acento.
2. **Travessão (—) em série.** Troque por vírgula, ponto ou parênteses. Hífen em palavra composta pode ficar.
3. **"Não é X, é Y"** e variações ("não se trata de X, mas de Y"). Reescreva como afirmação direta.
4. **Tríade decorativa** ("rápido, simples e eficiente") e frase de efeito sozinha num parágrafo só para dar peso.
5. **Palavras de enchimento de texto de IA:** "no mundo de hoje", "é importante ressaltar", "potencializar", "alavancar", "jornada", "soluções inovadoras", "incrível", "revolucionário".
6. **Abertura e fecho de manual:** "Você sabia que...", "Em resumo", "Conclusão". Comece pelo fato.
7. **Ritmo.** Alterne frase curta e média; evite 3 frases seguidas do mesmo tamanho e da mesma estrutura.
8. **Voz.** Fale como pessoa que atende cliente: concreto, verbo no presente, sem hype. Pode usar "pra" onde soa natural.
9. **CTA repetido.** Conferir que o CTA da legenda é diferente do dos últimos posts.

Saída: o texto corrigido, nada de comentário sobre o que mudou dentro do post.
