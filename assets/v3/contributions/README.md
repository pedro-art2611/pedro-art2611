# Painel de contribuições V3

`contributions.svg` é gerado integralmente por `scripts/generate-contributions.mjs`, em SVG estático de 2164 × 727. Referência visual: master aprovada `codex-clipboard-7b25d087-4618-4998-8dbd-cab20af4e640.png`. Moldura, divisórias `< | >`, texto e células são vetoriais. Não há imagem de fundo rasterizada, screenshot, fonte externa, animação ou dados de exemplo no gerador.

O README exibe o painel a 100% de largura, com proporção preservada. A árvore antiga e seu workflow permanecem preservados; a árvore já estava fora do README V3 antes desta integração temporária.

## Credencial e privacidade

1. Criar um **personal access token clássico**, da conta `pedro-art2611`, com somente **`read:user`**. Definir validade e renovar antes do vencimento.
2. Salvar em **Settings → Secrets and variables → Actions → New repository secret**, no repositório `pedro-art2611/pedro-art2611`, como **`PROFILE_CONTRIBUTIONS_TOKEN`**.
3. No perfil, em **Contribution settings**, manter **Private contributions** ativado. Essa opção já estava ativada na inspeção de 07/09/2026.
4. Se a organização exigir SAML SSO, autorizar o token em **Configure SSO** e conferir as políticas da organização. Atividade de um servidor GitHub Enterprise separado depende também da integração de contribuições do próprio GitHub.

O gerador verifica a identidade da conta e o escopo `read:user` (ou seu escopo pai `user`). Falha se o secret estiver ausente, inválido, sem escopo verificável ou se a API retornar erros. Não há fallback para o `GITHUB_TOKEN` do Actions. Esse token padrão é usado apenas para checkout e push do SVG.

A consulta solicita somente o calendário e indicadores agregados de contribuições restritas. O SVG contém apenas datas, contagens, níveis, meses e total. Nenhum nome de repositório/organização privada, commit, PR, branch ou mensagem é consultado pelo gerador ou publicado no SVG. Um contador `restrictedContributionsCount` zerado não prova ausência de atividade privada: credenciais com acesso aos repositórios podem enxergar os detalhes e não classificar essas contribuições como restritas.

## Geração e validação

Requer Node.js 22 ou superior, sem dependências de terceiros.

```sh
node scripts/generate-contributions.mjs
```

O token deve estar na variável de ambiente `PROFILE_CONTRIBUTIONS_TOKEN`; nunca escrever a credencial no comando, código ou documentação. Para validar localmente com a sessão autorizada do GitHub CLI:

```sh
node scripts/generate-contributions.mjs --gh --audit ../output/calendario-real.json
node scripts/test-contributions.mjs ../output/calendario-real.json
```

O arquivo de auditoria é local/temporário; não é commitado. Os testes comparam **todos os dias** da resposta real com o SVG: datas, posições, contagens, níveis, cores, semanas, meses e total. Também verificam continuidade na virada do ano e preservação de semanas incompletas, e rejeitam níveis desconhecidos, dias ausentes e total inconsistente. Não há fixtures de atividade fictícia.

O período padrão vem de `contributionsCollection`, sem reconstrução de histórico ou contagem manual de commits. `totalContributions` vem diretamente da API; a soma dos dias é usada apenas como validação. A legenda mapeia `NONE`, `FIRST_QUARTILE`, `SECOND_QUARTILE`, `THIRD_QUARTILE` e `FOURTH_QUARTILE`, sem thresholds locais. Dias sem contribuição continuam representados; posições fora do período não recebem células inventadas.

## Automação e limite da branch de trabalho

Workflow: `.github/workflows/update-contributions.yml`. Agendamento `0 3 * * *` (00h de Brasília), `workflow_dispatch` e push de alterações do gerador/testes/workflow exclusivamente na V3. Publica apenas o SVG quando há mudança, com commit semântico em português; o filtro de paths e o token do Actions evitam ciclos. Falhas não substituem o SVG publicado.

**O agendamento diário ainda não fica ativo enquanto o workflow existir apenas na V3.** O GitHub exige o arquivo na branch padrão para `schedule` e para registrar `workflow_dispatch`. A branch padrão continua `main`. Esta implementação não altera `main`, não muda a branch padrão e não faz merge. O gatilho por push permite validar o workflow agora. Na futura migração, será necessário aprovar a instalação na branch padrão e ajustar explicitamente a guarda e o destino de publicação; não remover essas proteções durante esta etapa.

Fontes: [calendário e read:user](https://docs.github.com/en/graphql/reference/users#contributionscollection), [atividade privada](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements), [agendamento do Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule).

## Evidência da primeira execução, 07/09/2026

- [Execução do Actions concluída com sucesso](https://github.com/pedro-art2611/pedro-art2611/actions/runs/34161262202), usando `PROFILE_CONTRIBUTIONS_TOKEN` e confirmando `read:user`.
- GraphQL autenticada local, GraphQL no Actions, calendário visível no perfil e SVG: **641 contribuições**. O Actions reproduziu o SVG sem alteração e não criou commit redundante.
- **366 dias, 53 semanas, 13 entradas de mês**: período de 07/09/2025 a 07/09/2026, inclusivo, com meses parciais nas extremidades. Conferência integral de datas, contagens, níveis e coordenadas; virada de 31/12/2025 para 01/01/2026; última semana contém apenas domingo e segunda, sem preencher o futuro.
- **Contribuições privadas da organização confirmadas**: o perfil autenticado mostra 11 contribuições de commits em dois repositórios privados em setembro; a visibilidade privada foi conferida separadamente. O calendário contém 8 contribuições em 03/09 e 3 em 04/09, além das 3 contribuições de discussões em 06/09. Essa inspeção não foi usada para gerar ou reconstruir o calendário, e nenhum identificador privado é publicado aqui.
- O GitHub retornou `restrictedContributionsCount: 0` também no Actions; esse indicador não foi usado para excluir, recalcular ou classificar células. O total completo confere com o perfil. O escopo cobre repositórios privados e internos conforme a API; não foi identificada atividade separada em repositórios de visibilidade **internal**, portanto não se afirma uma quantidade específica dessa categoria.
- Preview com HTML renderizado pela API de Markdown do GitHub: imagens carregadas e sem overflow horizontal em desktop (1280 px) e celular (390 px). No celular o painel horizontal reduz proporcionalmente; o link no README permite abrir e ampliar o SVG.
- A opção **Private contributions** já estava ativa. A sessão do CLI recebeu `read:user` e o usuário cadastrou o secret dedicado. Nenhuma mudança de branch padrão, de `main`, do workflow da árvore ou de outras seções aprovadas.

| Data conferida | Contagem da API e SVG | Nível oficial |
|---|---:|---|
| 31/12/2025 | 0 | NONE |
| 01/01/2026 | 0 | NONE |
| 04/08/2026 | 80 | FOURTH_QUARTILE |
| 03/09/2026 | 8 | SECOND_QUARTILE |
| 06/09/2026 | 3 | FIRST_QUARTILE |

Esses valores registram a validação inicial; o valor exibido no painel é sempre gerado novamente a partir da API.
