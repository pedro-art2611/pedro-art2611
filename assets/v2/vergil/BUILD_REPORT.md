# Build report — Vergil footer V2

Frames finais: **268**
Duração aproximada: **38.1s**
Canvas: **1000×235**
Piso autoral: **sim**

## Correções estruturais

- chroma removido apenas quando conectado à borda; detalhes internos do Vergil não são mais apagados por cor;
- chroma-spill corrigido somente na borda externa, sem reduzir alpha do personagem;
- todos os pixels transparentes têm RGB zerado e alpha final é binário para evitar silhueta roxa no GIF;
- sprites ancorados pela região dos pés em vez do centro do recorte;
- turn reduzido a 8 poses e reutilizado em reverso para manter consistência;
- walk-left usa ciclo de caminhada espelhado estável, não poses de virada;
- timings ampliados em ações, cabelo e viradas;
- Judgment Cut usa grid 4×3 e fit simultâneo de largura/altura;
- piso autoral floor.jpg integrado à renderização;
- loop fecha fisicamente no ponto inicial, sem teleporte.

## Observação

A V2 prioriza preservação do personagem e fluidez. Se a virada ainda não convencer visualmente, o próximo passo será substituir a rotação por uma transição autoral curta construída a partir de poses selecionadas, em vez de insistir na sheet do Gemini.
