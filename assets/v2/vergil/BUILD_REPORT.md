# Build report — Vergil footer V1

Frames finais: **188**
Duração aproximada: **33.4s**
Canvas: **920×210**

## Correções desta versão

- removido movimento de sprite right-facing para a esquerda; walk-left é um ciclo espelhado estável;
- removidas poses traseiras do Judgment Cut cast;
- chroma magenta agora é alpha binário sem borda semi-transparente;
- pixels transparentes têm RGB zerado para evitar halo roxo no GIF;
- Judgment Cut source 06 recortado em grid 4×3, evitando cortes no VFX;
- timings aumentados em caminhada, cabelo, viradas e Judgment Cut;
- loop fecha retornando fisicamente ao ponto inicial, sem teleporte horizontal.

## Mapeamento manual

- walk-right: 09
- turn: 01
- iai: 10
- hair: 07
- judgment cast: 08 (somente primeira fileira + neutral final)
- judgment FX: 06 (4×3)

## Pendente

O piso continua procedural até o asset autoral de pedra ser disponibilizado separadamente.
