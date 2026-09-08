# Divisória animada do Vergil

`divisor-vergil.webp`: versão final, WebP com qualidade 94 e alpha real, 60 quadros a 20 fps e ciclo de 3 segundos. Exibida a 96% entre o painel de Contribuições e o rodapé aprovado do Vergil. `divisor-vergil-estatico.png`: fallback estático preservado.

Os quatro PNGs enviados foram preservados integralmente em `source/`:

| Arquivo | Original do usuário |
|---|---|
| `energia-01.png` | `ChatGPT Image 7 de set. de 2026, 20_19_33 (1).png` |
| `energia-02.png` | `ChatGPT Image 7 de set. de 2026, 20_19_34 (4).png` |
| `energia-03.png` | `ChatGPT Image 7 de set. de 2026, 20_19_33 (2).png` |
| `energia-04.png` | `ChatGPT Image 7 de set. de 2026, 20_19_34 (3).png` |

Todos medem 2172 × 724 e possuem transparência real. A animação usa recorte comum com 12 px de margem e derivação proporcional para 1600 px de largura. Coordenadas e dimensões finais em `animacao.json`. Originais mantidos sem reescala.

A energia transita suavemente entre os quatro estados, com mistura de alpha pré-multiplicado. Raios horizontais adicionais têm deslocamento periódico contínuo. A placa, a tipografia e a estrutura mecânica são estabilizadas pelo primeiro quadro; “motivation” mantém o azul aprovado. Não há mudança de tamanho ou posição entre quadros.

Reprodução: `python scripts/animar-divisor-vergil.py`, com Pillow e NumPy. O gerador de Contribuições preserva a divisória superior e não gera mais a inferior. O WebP fica separado do SVG do calendário para preservar os dados e a atualização automática.
