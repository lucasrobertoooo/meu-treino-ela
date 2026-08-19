# Treino-Ela · HANDOFF v1

PWA single-file de treino pra ela. Android/Chrome. Fork do MeuTreino (do Lucas) que **já divergiu bastante** — não assuma que o que vale lá vale aqui.

**Última atualização:** 2026-08-15.04 (dia de mais cardio; camada de inteligência reescrita; auditoria de 8 bugs. SHELL v45)

## Antes de codar: ler primeiro
- **§ Diferenças pro MeuTreino** — o que diverge, e por quê. É onde mora quase todo bug de porte.
- **§ Auditoria 2026-08-15** — a rotação ABCD estava morta e o boot apagava cardio em silêncio. Entenda a causa antes de mexer em `ST.logs`.
- **`CREDITS.md`** — licenças das imagens (CC-BY exige atribuição).

## Perfil dela
- 33 anos, 166cm, ~60kg. Treina **3 a 4x/semana**, quase sempre na academia.
- **Objetivo principal: perda de gordura.** Depois: glúteo e membros inferiores.
- **Lesão no joelho.** A seleção de exercícios de hoje foi validada na prática (não incomoda) — trate como restrição dada. Sem corrida; bike só.
- Pescetariana (come peixe).

## Regras de produto (herdadas do MeuTreino, valem aqui)
- **Sem emojis em nada visível.** Usar SVG do objeto `I` ou texto puro.
- **Don't fix what isn't broken** nas funções centrais de progressão.
- **Storage isolado por feature**; migração **nunca destrutiva**.

---

## Quick facts
- **Produção:** https://lucasrobertoooo.github.io/meu-treino-ela/
- **Repo:** `lucasrobertoooo/meu-treino-ela` (público, exigência do Pages free)
- **Stack:** HTML/CSS/JS inline, 1 arquivo, sem build, sem dependência externa
- **Tamanho:** ~5.800 linhas / ~293KB

### Deploy
```bash
cd ~/Documents/Treino-Ela
# editar index.html
# OBRIGATÓRIO: bumpar treino-shell-vNN em sw.js, senão o cache não invalida
git add -A && git commit -m "..." && git push
```
No Android: abrir o app, puxar pra baixo (refresh), fechar e reabrir. `APP_VERSION` aparece no rodapé da aba Mais — use pra distinguir "não deployou" de "deployou bugado".

---

## Arquitetura: DOIS programas completos (não é o modelo do MeuTreino)

O MeuTreino tem `WK` (academia) + `HOME_SESSIONS` (5 sessões livres, storage separado em `freelog`).
Aqui é diferente:

- **`WK_GYM`** e **`WK_CASA`** são dois programas ABCD **completos e paralelos**.
- Alterna pelo toggle Academia/Casa → grava `ST.meta.local` (`'academia'` | `'casa'`).
- `_progMode()` → `'academia'|'casa'` · `_progBase()` → `WK_GYM|WK_CASA` · `dayEx(d)` → a lista de exercícios que está **de fato na tela**.
- Os ids dos dois conjuntos são disjuntos (casa termina em `c`: `a_1c`, `b_3c`...). **Nunca deixe colidir** — é isso que impede o log da academia de se misturar com o de casa.

### `ST.prog` — programa editável pelo usuário (não existe no MeuTreino)
Ela pode **trocar, adicionar e remover** exercício pelo app (`EX_BANK` + modal de edição).

- `ensureProgDay(d)` faz **snapshot do DIA INTEIRO** (`JSON.parse(JSON.stringify(...))`) em `ST.prog[modo][dia]`.
- **Armadilha:** a partir do primeiro toque em qualquer exercício daquele dia, o dia inteiro congela. Melhorias futuras que você fizer no `WK_GYM` **não chegam mais nesse dia**. Não há merge nem versionamento do snapshot.
- Exercício trocado/adicionado recebe id novo via `uid()` (`u3_18402`) — existe só em `ST.prog`, não no código.
- Consequência prática: **antes de "corrigir o programa no código", confira se o dia já está congelado** — senão o commit não muda nada no aparelho dela.

### `ST.logs` é keyado por **id estável**, não por posição
Diferença crítica pro MeuTreino, onde a chave é `A_0`, `B_3` (posicional).

- `exId(day,i)` devolve `dayEx(day)[i].id`.
- `migrateLogsStableId()` (flag `ST.meta._logsV2`) remapeou as chaves antigas uma vez.
- **Vantagem:** reordenar/mover exercício entre dias não embaralha histórico (no MeuTreino isso exigiu migração manual quando o core mudou de dia).
- **Custo:** o id **não é rótulo de dia**. `c_7` mora no dia A. Nunca deduza o dia por `id.split('_')[0]` — use **`dayOfExId(id)`**. Foi exatamente esse erro que matou a rotação ABCD (ver auditoria).

---

## Programa (academia — o que ela usa de fato)

| Dia | Nome | Foco |
|---|---|---|
| A | Inferior 1 | Quadríceps + Glúteo |
| B | Inferior 2 | Glúteo/Posterior + Cardio |
| C | **Superior** | Peito, Costas, Ombro, Braço + Cardio |
| D | Inferior 3 | Glúteo/Posterior + Cardio |

Volume semanal (séries diretas / equivalentes, se fizer os 4 dias): glúteo 11/18 · quadríceps 13/17 · posterior 13/13 · glúteo médio 8/8 · panturrilha 9 · core 9 · costas 6 · peito 3 · ombro ant 3 · ombro lat 2 · bíceps 2. **Total 79 séries + 70 min de cardio Z2.**

- **Cardio é um tipo de exercício** (`t:"cardio"`), sempre o último do dia, logado em **minutos** (input único, sem kg/RIR/timer). 15 min nos dias A/B/D, 25 min no C.
- `t` possíveis: `comp` · `iso` · `core` · `cardio`. `REST` só tem os 3 primeiros; cardio cai no fallback e não mostra botão de descanso.

### Restos do fork que NÃO são dela
- **`HOME_SESSIONS`** (5 templates: Core Completo, Panturrilha+Cardio, Posterior+Mobilidade, **Calistenia Peito+Tríceps**, **Ombro Lateral+Postura**) veio do MeuTreino e foi desenhado pras prioridades do Lucas (largura de ombro, peito superior). Usa `mg` que **nem existem** no `MG_LABELS` daqui (`peito_sup`, `ombro_post`) — esse volume é somado e depois sumido da tela. Ainda aparece na aba Hoje via `pickHomeSessions()`. **Ela já tem `WK_CASA`; isso aqui é redundante.**
- **Metas nutricionais default** (`proteinTarget||150`, `carbTarget||350`, `calTarget||2800`) são as do Lucas (homem, 75kg, ganho limpo). Pra ela, 2800 kcal é superávit. Só muda com decisão dele.

---

## Storage (localStorage, 16 chaves `treinoela_*`)

```
logs, bw, sleep, protein, suppl, photos(legado), measures, cardio, meta,
session, freelog, exmeta, prog, measureCfg, photometa, photoCfg
```
- **Pixels de foto no IndexedDB** (`treinoela_photos_db`, store `pixels`); metadados leves em `photometa`.
- `prog` / `measureCfg` / `photoCfg` **não existem no MeuTreino**.
- **`ST.meta.syncPat`** = token do GitHub do publisher `treino-status` (ver abaixo). **Excluído do backup de propósito** — o JSON do backup passa pelo share sheet.
- Backup: `exportData` cobre as 16 chaves; fotos têm export/import próprio (`exportPhotosBackup`). Import tem guarda `looksLikeAncientRawLogs` (formato pré-versionamento) — não remova, foi criada depois de uma corrupção real.

## Publisher `treino-status` (integração com o app "Meu Cuidado")
`publishTreinoStatus()` faz PUT de `treino-status.json` em `lucasrobertoooo/meu-cuidado-sync` usando um PAT colado na aba Mais. Só dispara se houver token. Não é sync de dados — publica só `{dia, foco, doneToday, local}`.

---

## Auditoria 2026-08-15 (8 correções, 50 asserts em node)

### CRÍTICO
1. **Rotação ABCD morta.** `suggestedNextDay()` e `todayTrainedDays()` faziam `id.split("_")[0]`, herdado da época em que a chave era posicional. Com id estável isso devolve `"a"`/`"b"` minúsculo → `indexOf` = −1 → `seq[0]` → o app sugeria **sempre o dia A**. E `todayTrainedDays()` retornava sempre vazio, então "✓ HOJE" nunca aparecia e a home vivia dizendo "Hoje · Inferior 1". Corrigido com **`dayOfExId(id)`** (consulta `ST.prog` primeiro, depois `WK_GYM`/`WK_CASA`, depois chave posicional antiga). Regressão entrou no commit `77e1d21`.
2. **Faxina do boot apagava dado em silêncio.** `cleanupPhantomSessions()` usa `hasValidDoneSafe`, que exigia `kg>0`. Toda sessão de cardio (só minutos) e todo exercício sem carga do programa de casa (flexão, prancha, agachamento na parede) era **deletado no boot seguinte**. Agora a regra é `done && reps>0`.
3. **Trocar exercício apagava o histórico pra sempre** (`delete ST.logs[old.id]`). O substituto já entra com id novo, então a progressão zera por construção — o delete só destruía dado. Removido.
4. **Datas em UTC.** `today()`/`todayISO()`/`dateAdd()` usavam `toISOString()`: das 21h à meia-noite tudo caía no dia seguinte. Novo helper **`localISO()`**.

### ALTO
5. **Cardio e corpo livre nunca contavam.** `isValidDone` exigia `kg>0`. A barra "Cardio" do volume semanal ficava sempre em 0, o dia não contava como treino (streak, "X/4 desta semana") e `isWorkoutComplete` nunca disparava, porque o cardio é o **último** exercício de todo dia. Regra nova: `done && reps>0`. Força (`suggestNext`, `bestE1RM`, `sessionTop`) continua exigindo `kg>0` por conta própria.
6. **Falso plateau.** `detectPlateau` comparava só e1RM e o Brzycki **capa reps em 12**. Em **16 dos 25** exercícios da academia (topo ≥13 reps) progredir 13→15→17 dá e1RM idêntico → o app acusava plateau e mandava trocar o exercício. Agora usa `sessionTop`/`cmpTop` (dupla progressão, o mesmo modelo que o `suggestNext` prescreve).
7. **Token do GitHub vazava no backup.** `syncPat` saía em texto puro no JSON que vai pro clipboard e pro share sheet. Removido do export (cópia rasa do `meta`, o token continua no app) e preservado no import.

### MÉDIO
8. **Incremento ignorava o equipamento** → `inferLoadStep(id)` deduz o passo (5/2.5/2/1) pelas cargas já usadas, com ≥2 cargas distintas. Sem configuração. Cardio não recebe mais sugestão de carga. **Preset do timer** 2:00 → **2:30**, alinhado com `REST.comp=150`.

### Efeito de transição (não é bug novo)
- Registros noturnos antigos continuam com data adiantada em 1 dia. Não reescrevi dado do usuário — migração cega seria pior que o sintoma. Some sozinho.
- **Histórico de cardio anterior a 15/08 provavelmente já foi apagado** pela faxina do boot. Não tem como recuperar sem um backup antigo.

### Verificação
50 asserts em node rodando o código real do app (`vm` + localStorage/DOM stubados): fuso, rotação nos 4 dias + modo casa + id trocado + chave antiga, plateau nos 5 cenários, cardio/corpo livre, faxina do boot, troca de exercício, incremento, backup, + smoke das 5 telas. **Sem navegador** (endereços locais bloqueados no ambiente) — o visual segue pra conferir no device.

---

## Camada de inteligência (2026-08-15.03)

O app dava conselho útil por ~8 semanas e depois repetia a mesma frase pra sempre. Simulei 24 semanas rodando o código real: da semana 10 à 24 ele mostrava "bateu o topo, sobe carga", "plateau" e "considere trocar" ao mesmo tempo, se contradizendo.

- **`progressState(id, ex)`** é o ponto único: um estado, uma mensagem, uma ação. Estados: `inicio`, `progredindo`, `tentando`, `travado-passo`, `fadiga`, `mantendo`, `trocar`, `travado`. Substituiu os três banners independentes. **Nada é gravado**: o conselho anterior é recalculado da sessão anterior via `suggestFrom`, então funciona sobre o histórico atual, sem migração e sem chave nova.
- **`globalLoadStep()` / `loadStepFor()`** — o app fabricava o platô que depois diagnosticava, sugerindo +1kg numa pilha de placas de 5. `inferLoadStep` sozinho não resolve: travada, o exercício nunca acumula 2 cargas distintas. Agora cai pro passo do app inteiro.
- **`sessionRIR()`** — o RIR era gravado em toda série e nenhuma função lia. 3+ sessões travadas com RIR ≤1 viram diagnóstico de fadiga, não "troque de exercício".
- **`bwTrend()`** — a progressão nunca lia `ST.bw`. Carga parada com peso caindo é massa magra preservada (Helms, Aragon & Fitschen 2014), não fracasso. **Depende de ela se pesar** (mínimo 4 pesagens em 28 dias); sem isso cai no estado genérico.
- **`autoDetectDeload()`** (no boot) — semana leve é o que ela FAZ, não o que declara. Janela móvel de 7 dias contra as 4 anteriores (alinhadas por dia da semana por construção); ≤60% do volume marca sozinho. Antes o alerta vermelho ficava aceso até alguém tocar em "Feito".
- **`refSession()`** — depois do deload o app prescrevia a carga do deload. Detecta sessão leve pelo número de séries e retoma de onde parou.
- **`shouldSwapExercise()`** perdeu o gatilho "12 semanas no mesmo exercício", que ficava aceso por meses. Só sugere depois de deload feito (Fonseca et al 2014 e Baz-Valle et al 2019 argumentam contra variar por variar).

## Dia de mais cardio (2026-08-15.04)

Toggle no topo do treino aberto (`cardioDayOn` / `toggleCardioDay` / `cardioPlan`). Ligado, apaga os exercícios que menos fazem falta hoje e estende a bike com o tempo liberado.

Ordem de decisão em `cardioPlan(d)`: (1) o que o corpo **ainda não recebeu esta semana** (`weeklyVolume` dos últimos 7 dias contra `MG_TARGETS`), (2) `MG_PRIORITY` (glúteo e glúteo médio), (3) composto sai por último, (4) o primeiro exercício do dia nunca sai. Teto: sempre sobram 3 exercícios de força.

Dias A/B/D dobram (15→30 min). O dia C não dobra (25→43): dobrar 25 min exigiria apagar quase o treino inteiro. **Quando não dobra, a UI diz o número real** (`plan.dobrou` é a flag honesta). Exercício apagado continua registrável e conta no volume. Marcação por data em `ST.meta.cardioDays`, expira em 30 dias, entra no backup.

## Metas dela + ritmo de perda visível (2026-08-19.01)

Resolve a primeira pendência aberta e um bug encontrado ao resolvê-la.

**Metas nutricionais eram as dele.** O app ensinava no princípio 9 "déficit lento ~0,5-0,7%/semana" e, na tela de metas, mandava o oposto: 2800 kcal com o rótulo *"Superávit leve pra hipertrofia. Ajuste pela balança: subir 0,2-0,4kg/sem"*, mais textos citando "75kg" e "se balança não sobe, +200 kcal". Agora: **1550 kcal / 130g proteína / 145g carbo**, estimados por Mifflin-St Jeor (60kg, 166cm, 33a → basal ~1310; gasto ~1900-2000 com 3-4 treinos + bike) menos ~400 de déficit. Rótulos reescritos pro perfil dela (pescetariana, perda de gordura) e o ajuste inverteu de "subir" para "descer 0,3-0,4kg/sem" (Garthe et al 2011). **São estimativa: quem manda é a balança.**

**`bwTrend()` subestimava o ritmo em 33%.** Ele comparava a média dos primeiros N pontos com a dos últimos N, mas dividia pelo período INTEIRO da janela — e o centro de cada grupo fica pra dentro das pontas. Com 4 pesagens semanais caindo 0,36kg/sem, reportava 0,24. Isso atrasava o estado `mantendo` da progressão (limiar -0,15) e teria contaminado o número novo da tela. Divisor agora é a distância entre os centroides dos dois grupos.

**Ritmo na aba Corpo (`bwRateInfo`).** O card de peso mostrava só "delta desde a primeira pesagem" — número que só cresce e nunca diz se o ritmo está certo. Agora mostra **kg/semana + %/semana + veredito** contra a faixa 0,5-0,8%: `no alvo` (verde), `rápido — segura, senão perde músculo` (vermelho), `devagar pro alvo` (âmbar), `estável`, `subindo`. Percentual é sobre o peso atual. Sem 4 pesagens em 28 dias não inventa número: convida a pesar.

Verificado com 18 asserts em node no código real (5 faixas de classificação, guardas de dados insuficientes, render dos 3 estados, metas na tela).

---

## Pendências (precisam de decisão do Lucas)
- ~~Metas nutricionais~~ **resolvido em 2026-08-19.01** (1550/130/145). Confirmar os números com ela e ajustar pelo ritmo real depois de 2-3 semanas.
- **Glúteo médio só existe em A e B; o dia D (inferiores) não tem nenhum.** Proposta: 3 séries de abdução em D — aditivo, zero joelho, sobe 8→11 com 3 exposições. Aguarda decisão.
- **Cadeira extensora em A e B, que são dias consecutivos** (6 séries/sem do mesmo isolador). Pode ser proposital pelo raciocínio do joelho (JOSPT 2019) — conversar com ela antes de mexer.
- **Frequência do superior:** ela **escolheu manter 1x/semana** (2026-08-15). Com isso o dia C passa a ser manutenção, não crescimento, o que é legítimo num déficit. Não reabrir sem ela pedir.
- **Equilíbrio do `WK_CASA`:** dia B tem 52 min contra 68 do C. Proposta pendente: acrescentar concha com mini-band 3×15-20 e bom dia com halter leve 3×12-15 (ambos zero joelho, sobem glúteo médio 8→11 e posterior 8,5→11,5, e emparelham os 4 dias em 63-68 min).
- **Ponte de glúteo** no `WK_CASA` (`b_5c`, `d_5c`): **confirmado que fica** (2026-08-15). Joelho flexionado e parado, carga passa pelo quadril: sem prejuízo pro joelho dela.
- **Sequência A→B:** cadeira extensora aparece nos dois dias, que são consecutivos na rotação.
- **`HOME_SESSIONS`** do fork: remover ou substituir pelos templates dela.
- **`index.html.bak-*`** (9 arquivos, 2,2MB): gitignorados, não vão pro Pages, mas poluem qualquer `grep` na pasta.
