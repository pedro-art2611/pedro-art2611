# Assets da etapa de projetos

Recebidos em 07/09/2026. Cópias idênticas aos arquivos enviados, verificadas por SHA-256. Sem recorte, alteração de fundo, reescala ou edição. Integrados ao README entre Forja Técnica e Contribuições, com os textos fornecidos pelo usuário.

Header: `../headers/projetos.png`, origem `header-projetos.png`.

Ordem definida pelo usuário:

| Ordem | Projeto | Arquivo | Origem |
|---|---|---|---|
| 1 | Unimangas | `01-unimangas.png` | `codex-clipboard-b5cc7cfe-65a4-4c33-a5f2-15aa5cb146ec.png` |
| 2 | Casa Rara | `02-casa-rara.png` | `codex-clipboard-59b7088b-153b-48db-b5b7-35046e68e9ab.png` |
| 3 | Conferência Quantitativa | `03-conferencia-quantitativa.png` | `codex-clipboard-f0a22170-bc6b-4708-9498-a85a6c7da954.png` |
| 4 | Hermix | `04-hermix.png` | `codex-clipboard-d207d0e5-1c13-4ac5-a7df-7844e3d13233.png` |
| 5 | Maestro CRM | `05-maestro-crm.png` | `codex-clipboard-fb776c62-e0df-46b5-956e-ea81c3a1812c.png` |
| 6 | Next Chapter | `06-next-chapter.png` | `codex-clipboard-8c886717-f457-4da8-a923-90a12cafbd91.png` |

As imagens são referências visuais fornecidas pelo usuário; textos e métricas ilustrados nelas não foram verificados como dados reais dos projetos.

## Montagem

Header a 60%. Capas alternadas por `align`, com dimensões intrínsecas de 300 × 200 no desktop; Next Chapter usa 260 × 173,33. `<picture>` e `<source media>` usam os mesmos arquivos com dimensões originais no celular, limitados pela largura disponível do GitHub, para que o texto apareça abaixo. O fallback também usa a capa original. Textos reais em HTML, sem CSS customizado ou tabelas.

Os seis nodes leves `node-01.svg` a `node-06.svg`, explicitamente autorizados no prompt, aparecem centralizados, com pequenos segmentos verticais; a linha é segmentada para funcionar no README sem CSS de posicionamento e sem bordas de tabela.

Links públicos verificados: Unimangas, Casa Rara e Conferência Quantitativa. O repositório de Casa Rara é `https://github.com/ozelfls/1.1.1_site_ong`, informado pelo usuário, que participou usando sua conta acadêmica. Hermix e Maestro CRM exibem apenas `PRIVATE REPOSITORY`, sem URLs ou dados internos adicionais. Next Chapter encerra a sequência com o texto e terminal fornecidos.

## Refinamento dos micro-assets

Fonte: PNG `micro-assets.png` anexado, idêntico por SHA-256 a `../source/micro-assets.png`. Apenas cinco elementos foram recortados em `details/`; coordenadas em `details/crop-map.json`. Bounding box calculado pelo conteúdo com alpha maior que 8/255, ignorando resíduos praticamente invisíveis fora da arte; pixels e alpha dentro do recorte preservados, sem reescala, com padding transparente de 4 px.

| Recorte | Dimensões | Uso |
|---|---|---|
| `details/codigo.png` | 213 × 153 | Embutido no botão local `details/repositorio.svg`, 156 × 32, nos três links públicos. |
| `details/colchetes.png` | 179 × 163 | Uma vez antes de cada uma das cinco stacks, a 18 px. |
| `details/losango.png` | 168 × 169 | Nodes 01 a 05, a 14 px; números preservados. |
| `details/estrela.png` | 184 × 188 | Duas aparições: transições 03 e 05, a 16 px. |
| `details/lua.png` | 190 × 195 | Uso exclusivo junto ao node 06, a 20 px. |

Stacks em `<kbd>`, com cada tecnologia como texto real e quebra de linha entre tags. Cores e bordas nativas do tema do GitHub; o ícone técnico fornece o accent cyan. O botão usa SVG local, sem serviço de badges, com fundo navy, borda cyan, texto claro e o recorte aprovado embutido. Nenhum link adicionado aos projetos privados.

`../dividers/divisor-projetos.png`: cópia exata do divisor anexado, 780 × 38, exibido a 92% entre o fim da Forja e o header Projetos. O fundo desse anexo é opaco; foi preservado como solicitado.
