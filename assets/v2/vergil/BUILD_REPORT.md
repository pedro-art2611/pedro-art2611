# Build report — Vergil footer V3

Frames finais: **256**
Duração aproximada: **41.1s**
Canvas: **1000×230**
Piso autoral: **sim**

## Correções estruturais V3

- cada célula da sprite sheet é recortada antes da remoção de fundo;
- remoção de chroma é adaptativa à paleta da borda de cada célula;
- resíduos magenta próximos ao contorno são substituídos por cor vizinha, não por transparência;
- manchas magenta no solo dos próprios sprites são descartadas;
- cada sequência usa um único fator de escala calculado pela mediana de altura; não existe zoom frame-a-frame;
- anchor horizontal usa a região central dos pés, reduzindo drift causado por Yamato/casaco;
- virada reduzida para 5 poses fortes, em linguagem low-frame-rate deliberada;
- GIF reserva o índice 0 exclusivamente para transparência; preto/azul escuro do Vergil não pode mais virar transparente;
- APNG RGBA de QA gerado em rendered/vergil-footer-v3.png;
- piso autoral é detectado pela região ocupada por pedra, sem carregar o chroma superior inteiro.

## Direção

Se a V3 ainda apresentar deformações grandes nas poses, o gargalo restante será a inconsistência artística entre sprites. Nesse ponto faz mais sentido refazer o personagem em uma linguagem 8/16-bit mais simples e canônica do que continuar compensando os sheets atuais por código.
