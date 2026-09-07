# Assets V3

Fonte autoritativa: `github-profile-assets-v3.zip`, fornecido em 2026-09-07. Branch: `feat/profile-readme-v3`.

Os três WebPs animados são cópias byte a byte dos originais. PNGs: alpha real confirmado; removido apenas resíduo quase invisível (alpha <= 8/255) antes do bounding box, sem remover preto interno da arte. Padding transparente 8px (6px nos micro-assets). Famílias estáticas têm derivados proporcionais normalizados; os masters permanecem em `source/`, sem redução. Sem OCR. Coordenadas reproduzíveis em `crop-map.json`.

Jardim de contribuições adiado por solicitação do usuário: não renderizar seção nem exigir sua placa neste checkpoint. Os seis arquivos `assets/arvore-*.jpg` foram recuperados de `origin/main` apenas para preservar o workflow existente, sem alterar a branch main.

O checkpoint contém entrada, Sobre mim e divisor; Vergil permanece visível como footer provisório. Nenhuma seção adicional foi montada. Placas de Contato/Projetos estão ausentes; os QUATRO ÍCONES de contato estão presentes.

| Nome lógico | Path relativo a assets/v3 | Origem no ZIP | Status | Dimensões | Uso |
|---|---|---|---|---|---|
| border-bottom | source/border-bottom.png | border-bottom.png | source | 2172 × 724 | Original do ZIP; não usar diretamente no README. |
| border-top | source/border-top.png | border-top.png | source | 2172 × 724 | Original do ZIP; não usar diretamente no README. |
| contatos-icons | source/contatos-icons.png | contatos-icons.png | source | 1254 × 1254 | Original do ZIP; não usar diretamente no README. |
| divisor principal | source/divisor principal.png | divisor principal.png | source | 2172 × 724 | Original do ZIP; não usar diretamente no README. |
| divisor-secundario | source/divisor-secundario.png | divisor-secundario.png | source | 2172 × 724 | Original do ZIP; não usar diretamente no README. |
| divisors | source/divisors.png | divisors.png | source | 1448 × 1086 | Original do ZIP; não usar diretamente no README. |
| elevenlabs-ico | source/elevenlabs-ico.png | elevenlabs-ico.png | source | 1254 × 1254 | Original do ZIP; não usar diretamente no README. |
| header-sobre-mim | source/header-sobre-mim.png | header-sobre-mim.png | source | 2172 × 724 | Original do ZIP; não usar diretamente no README. |
| header-tecnica | source/header-tecnica.png | header-tecnica.png | source | 2172 × 724 | Original do ZIP; não usar diretamente no README. |
| label-charts | source/label-charts.png | label-charts.png | source | 1448 × 1086 | Original do ZIP; não usar diretamente no README. |
| micro-assets | source/micro-assets.png | micro-assets.png | source | 1448 × 1086 | Original do ZIP; não usar diretamente no README. |
| stack-icones-2 | source/stack-icones-2.png | stack-icones-2.png | source | 1536 × 1024 | Original do ZIP; não usar diretamente no README. |
| stack-icons-1 | source/stack-icons-1.png | stack-icons-1.png | source | 1448 × 1086 | Original do ZIP; não usar diretamente no README. |
| vite-ico | source/vite-ico.png | vite-ico.png | source | 1254 × 1254 | Original do ZIP; não usar diretamente no README. |
| Katana original | source/katana_asset_transparente_v4.gif | katana_asset_transparente_v4.gif | source | 1600 × 380 | GIF original preservado. |
| frame-top | frame/frame-top.png | border-top.png | final | 2188 × 353 | Recorte [0, 165, 2172, 502]; padding 8px. Escala nativa. |
| frame-bottom | frame/frame-bottom.png | border-bottom.png | final | 2188 × 356 | Recorte [0, 313, 2172, 653]; padding 8px. Escala nativa. |
| divisor-principal | dividers/divisor-principal.png | divisor principal.png | final | 2159 × 174 | Recorte [15, 282, 2158, 440]; padding 8px. Escala nativa. |
| divisor-secundario | dividers/divisor-secundario.png | divisor-secundario.png | final | 2038 × 130 | Recorte [75, 302, 2097, 416]; padding 8px. Escala nativa. |
| sobre-mim | headers/sobre-mim.png | header-sobre-mim.png | final | 1962 × 545 | Recorte [113, 98, 2059, 627]; padding 8px. Escala nativa. |
| forja-tecnica | headers/forja-tecnica.png | header-tecnica.png | final | 1962 × 448 | Recorte [113, 138, 2059, 570]; padding 8px. Escala nativa. |
| github | contact/github.png | contatos-icons.png | final | 440 × 440 | Recorte [180, 189, 571, 584]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| linkedin | contact/linkedin.png | contatos-icons.png | final | 440 × 440 | Recorte [697, 196, 1107, 587]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| email | contact/email.png | contatos-icons.png | final | 440 × 440 | Recorte [164, 705, 591, 1064]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| instagram | contact/instagram.png | contatos-icons.png | final | 440 × 440 | Recorte [701, 693, 1097, 1063]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| nodejs | stack/nodejs.png | stack-icons-1.png | final | 400 × 400 | Recorte [24, 178, 359, 507]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| react | stack/react.png | stack-icons-1.png | final | 400 × 400 | Recorte [377, 178, 715, 507]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| postgresql | stack/postgresql.png | stack-icons-1.png | final | 400 × 400 | Recorte [734, 178, 1095, 507]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| redis | stack/redis.png | stack-icons-1.png | final | 400 × 400 | Recorte [1095, 178, 1427, 509]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| docker | stack/docker.png | stack-icons-1.png | final | 400 × 400 | Recorte [24, 562, 359, 892]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| n8n | stack/n8n.png | stack-icons-1.png | final | 400 × 400 | Recorte [377, 562, 715, 892]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| openai | stack/openai.png | stack-icons-1.png | final | 400 × 400 | Recorte [734, 562, 1095, 892]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| github | stack/github.png | stack-icons-1.png | final | 400 × 400 | Recorte [1095, 562, 1426, 892]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| typescript | stack/typescript.png | stack-icones-2.png | final | 400 × 400 | Recorte [72, 72, 512, 493]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| bullmq | stack/bullmq.png | stack-icones-2.png | final | 400 × 400 | Recorte [512, 72, 1024, 493]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| linux | stack/linux.png | stack-icones-2.png | final | 400 × 400 | Recorte [1024, 72, 1464, 493]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| express | stack/express.png | stack-icones-2.png | final | 400 × 400 | Recorte [74, 517, 512, 942]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| neon | stack/neon.png | stack-icones-2.png | final | 400 × 400 | Recorte [512, 517, 1024, 940]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| nginx | stack/nginx.png | stack-icones-2.png | final | 400 × 400 | Recorte [1024, 519, 1464, 940]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| elevenlabs | stack/elevenlabs.png | elevenlabs-ico.png | final | 400 × 400 | Recorte [184, 228, 1070, 1026]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| vite | stack/vite.png | vite-ico.png | final | 400 × 400 | Recorte [207, 210, 1049, 997]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| backend | chips/backend.png | label-charts.png | final | 536 × 180 | Recorte [170, 259, 667, 410]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| frontend | chips/frontend.png | label-charts.png | final | 536 × 180 | Recorte [778, 259, 1278, 413]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| banco-de-dados | chips/banco-de-dados.png | label-charts.png | final | 536 × 180 | Recorte [170, 433, 676, 587]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| ia | chips/ia.png | label-charts.png | final | 536 × 180 | Recorte [780, 433, 1278, 587]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| automacao | chips/automacao.png | label-charts.png | final | 536 × 180 | Recorte [170, 607, 675, 764]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| integracoes | chips/integracoes.png | label-charts.png | final | 536 × 180 | Recorte [777, 607, 1282, 764]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| apis | chips/apis.png | label-charts.png | final | 536 × 180 | Recorte [169, 784, 675, 939]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| infra | chips/infra.png | label-charts.png | final | 536 × 180 | Recorte [779, 785, 1282, 939]; padding 8px. Derivado normalizado proporcionalmente; master intacto em source/. |
| divisor-01 | dividers/divisor-01.png | divisors.png | final | 1362 × 92 | Recorte [48, 100, 1398, 180]; padding 6px. Escala nativa. |
| divisor-02 | dividers/divisor-02.png | divisors.png | final | 1376 × 99 | Recorte [42, 255, 1406, 342]; padding 6px. Escala nativa. |
| divisor-03 | dividers/divisor-03.png | divisors.png | final | 1360 × 87 | Recorte [50, 420, 1398, 495]; padding 6px. Escala nativa. |
| divisor-04 | dividers/divisor-04.png | divisors.png | final | 1359 × 81 | Recorte [51, 592, 1398, 661]; padding 6px. Escala nativa. |
| divisor-05 | dividers/divisor-05.png | divisors.png | final | 1359 × 71 | Recorte [51, 756, 1398, 815]; padding 6px. Escala nativa. |
| divisor-06 | dividers/divisor-06.png | divisors.png | final | 1363 × 76 | Recorte [49, 926, 1400, 990]; padding 6px. Escala nativa. |
| micro-ponto-cyan | dividers/micro-ponto-cyan.png | micro-assets.png | final | 189 × 181 | Recorte [121, 149, 298, 318]; padding 6px. Escala nativa. |
| micro-lanterna | dividers/micro-lanterna.png | micro-assets.png | final | 185 × 181 | Recorte [455, 149, 628, 318]; padding 6px. Escala nativa. |
| micro-losango | dividers/micro-losango.png | micro-assets.png | final | 172 × 173 | Recorte [805, 157, 965, 318]; padding 6px. Escala nativa. |
| micro-seta-dupla | dividers/micro-seta-dupla.png | micro-assets.png | final | 187 × 149 | Recorte [1151, 169, 1326, 306]; padding 6px. Escala nativa. |
| micro-seta-tripla | dividers/micro-seta-tripla.png | micro-assets.png | final | 223 × 152 | Recorte [101, 490, 312, 630]; padding 6px. Escala nativa. |
| micro-codigo | dividers/micro-codigo.png | micro-assets.png | final | 217 × 157 | Recorte [445, 489, 650, 634]; padding 6px. Escala nativa. |
| micro-conexao | dividers/micro-conexao.png | micro-assets.png | final | 194 × 184 | Recorte [800, 475, 982, 647]; padding 6px. Escala nativa. |
| micro-colchetes | dividers/micro-colchetes.png | micro-assets.png | final | 183 × 167 | Recorte [1151, 483, 1322, 638]; padding 6px. Escala nativa. |
| micro-estrela | dividers/micro-estrela.png | micro-assets.png | final | 188 × 192 | Recorte [121, 782, 297, 962]; padding 6px. Escala nativa. |
| micro-corte | dividers/micro-corte.png | micro-assets.png | final | 239 × 242 | Recorte [428, 755, 655, 985]; padding 6px. Escala nativa. |
| micro-lua | dividers/micro-lua.png | micro-assets.png | final | 194 × 199 | Recorte [808, 783, 990, 970]; padding 6px. Escala nativa. |
| micro-torii | dividers/micro-torii.png | micro-assets.png | final | 225 × 199 | Recorte [1137, 782, 1350, 969]; padding 6px. Escala nativa. |
| banner-animado | banner/banner-animado.webp | pedro-artur-v2-animado.webp | final | 2172 × 724 | WebP original intacto; 74.71 MiB. |
| banner-fallback | banner/banner-fallback.png | pedro-artur-v2-animado.webp | fallback | 2172 × 724 | Primeiro frame; não substitui animação nesta montagem. |
| personagem-animado | about/personagem-animado.webp | programador-transparente.webp | final | 448 × 528 | WebP original intacto; 35.79 MiB. |
| personagem-fallback | about/personagem-fallback.png | programador-transparente.webp | fallback | 448 × 528 | Primeiro frame; não substitui animação nesta montagem. |
| vergil-animado | footer/vergil-animado.webp | vergil-runtime-v3.7-exact-color.webp | final | 1200 × 240 | WebP original intacto; 20.60 MiB. |
| vergil-fallback | footer/vergil-fallback.png | vergil-runtime-v3.7-exact-color.webp | fallback | 1200 × 240 | Primeiro frame; não substitui animação nesta montagem. |
| Katana acento | dividers/katana-acento.webp | katana_asset_transparente_v4.gif | final | 1265 × 150 | Recorte união de 63 frames (128, 133, 1377, 267); WebP lossless; tempos e loop preservados; exibir a 24%. |
| Projetos | headers/projetos.png | Não consta no ZIP | MISSING_APPROVED_ASSET | — | Não substituir por asset inventado. |
| Contato (placa) | headers/contato.png | Não consta no ZIP | MISSING_APPROVED_ASSET | — | Não substituir por asset inventado. |
| REST API | stack/rest-api.png | Não consta no ZIP | MISSING_APPROVED_ASSET | — | Não substituir por asset inventado. |

## Verificação do checkpoint

- README passou pelo endpoint Markdown do GitHub: percentuais, `align="right"` e `br clear="right"` foram preservados pelo sanitizador.
- Preview local usa esse HTML e aproxima o tema escuro do GitHub; conferido a 1100px e 390px, com as oito imagens carregadas e sem overflow horizontal. Não é screenshot da página remota.
- Banner: 2172 × 724; personagem: 448 × 528; Vergil: 1200 × 240. Os três WebPs são byte a byte iguais ao ZIP, sem recompressão.
- Molduras: 2188 × 353 e 2188 × 356, incluindo padding. A altura restante pertence ao desenho das extremidades; não é área vazia da spritesheet.
- Stack: 400 × 400; contatos: 440 × 440; chips: 536 × 180. Escala proporcional, sem deformação; fontes em resolução original preservadas.
- Katana: 1265 × 150, 63 frames. Recorte pela união de TODOS os frames; derivado WebP lossless; original GIF preservado.
- Os PNGs do ZIP têm alpha real, mas continham resíduos com alpha mínimo espalhados por grandes áreas. Recortes descartam somente alpha <= 8/255. Preto visível interno não foi convertido em transparência.
- Risco pendente: os três WebPs somam 131,10 MiB. O envio Git comporta cada arquivo, mas o carregamento frio do README pode ser demorado; validar o carregamento remoto antes de decidir por uma versão otimizada.
- Restam ausentes apenas a placa de Projetos, a placa de Contato e o ícone de stack REST API. Jardim está fora do escopo por decisão do usuário.
