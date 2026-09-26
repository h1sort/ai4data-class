# Fuentes — Clase 3 (WS2)

Todas las cifras se verificaron el **2026-09-26** contra la fuente citada. Cuando un número es una
estimación (no medido directamente por quien lo publicó), está marcado explícitamente **«estimado»**
tanto aquí como en el texto pensado para la diapositiva. Nada de lo listado abajo fue inventado o
redondeado sin decirlo.

---

## 1 · Diapositiva 2 «LLM» — receta simplificada

### 1a. «Un pedazo de internet» → Common Crawl

**Texto sugerido para la diapositiva (ES):**
> Common Crawl: más de 300 mil millones de páginas web archivadas desde 2007, con 3 000–5 000
> millones de páginas nuevas cada mes.

**English note:** Common Crawl is the standard example of "a chunk of the internet" used across the
LLM industry (GPT-3, RedPajama, FineWeb, Llama 1, etc. all cite it explicitly as a training-data
component). It illustrates the *category* of ingredient, not a claim about Llama 3.1 specifically —
see the caveat below.

- **Cifra:** "Over 300 billion pages spanning 15 years." · "3–5 billion new pages added each month."
  · "Free and open corpus since 2007." · "Cited in over 10,000 research papers."
- **Fuente primaria:** [commoncrawl.org](https://commoncrawl.org/) (official homepage) — accessed
  2026-09-26.
- **Caveat (importante, no lo pierdas en la diapositiva):** el propio paper de Meta para Llama 3
  **no nombra a Common Crawl**. Su model card solo dice "A new mix of publicly available online
  data" y "~15 trillion tokens of data from publicly available sources" (ver §1b). Common Crawl es
  el ejemplo citable más conocido de "un pedazo de internet" para LLMs en general — no afirmamos que
  sea el corpus de Llama 3.1. Si alguien del público pregunta "¿Llama usó Common Crawl?", la
  respuesta honesta es "Meta no lo confirma en el paper; probablemente sí, como casi todos, pero no
  está documentado públicamente."

### 1b. Llama 3.1 405B — entrenamiento (medido, no estimado)

**Texto sugerido para la diapositiva (ES):**
> Llama 3.1 405B: 15.6 billones de tokens («trillion» en inglés), 16 384 GPUs H100, 30.84 millones
> de horas-GPU de cómputo. Medido y publicado por Meta.

| Métrica | Valor | Cita exacta de la fuente |
|---|---|---|
| Tokens de preentrenamiento | **15.6T tokens** (405B específico) | "we pre-trained a flagship model with 405B trainable parameters on 15.6T text tokens" |
| Tokens (familia completa, cifra redondeada del model card) | 15T+ | "Llama 3.1 was pretrained on ~15 trillion tokens of data from publicly available sources." |
| GPUs usadas | **16,384 H100** ("hasta 16K") | "Llama 3 405B is trained on up to 16K H100 GPUs, each running at 700W TDP with 80GB HBM3" |
| Horas-GPU acumuladas (405B) | **30.84M GPU hours** (H100-80GB, 700W TDP) | Tabla "Hardware and Software" del model card: fila `Llama 3.1 405B` → `30.84M` |
| Cómputo total | 3.8×10²⁵ FLOPs | "our flagship language model was pre-trained using 3.8×10²⁵ FLOPs, almost 50× more than the largest version of Llama 2" |
| Emisiones (referencia, no pedida pero útil) | 8,930 t CO2eq (location-based) / 0 t CO2eq (market-based, Meta compra energía renovable) | Tabla del model card, fila `Llama 3.1 405B` |

- **Fuente primaria (paper):** Dubey et al., "The Llama 3 Herd of Models", arXiv:2407.21783 —
  https://arxiv.org/abs/2407.21783 (versión HTML consultada:
  https://ar5iv.labs.arxiv.org/html/2407.21783) — accessed 2026-09-26.
- **Fuente primaria (model card oficial de Meta):**
  https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md — accessed
  2026-09-26.
- Ambas fuentes son de Meta directamente (el desarrollador del modelo); no son estimaciones de
  terceros.

### 1c. Llama 3.1 405B — costo de entrenamiento (⚠️ ESTIMADO, no publicado por Meta)

**Texto sugerido para la diapositiva (ES), con la etiqueta obligatoria:**
> Costo de entrenamiento — **estimado**: ≈ US$170–176 millones (alquiler de GPU en la nube, precio
> histórico). Fuente: Epoch AI. Meta nunca publicó una cifra oficial de costo.

**Detalle para las notas del presentador (rango completo, tres metodologías distintas, mismo
dataset):**

| Metodología | Estimado | Nota |
|---|---|---|
| Costo de hardware amortizado (2023 USD) | **$52.9M** | Amortiza el clúster sobre el período de entrenamiento; "about half of this spending on GPUs, with the remainder on other hardware and energy" |
| Costo de alquiler en la nube (**recomendado para la diapositiva**) | **$176.0M** | "chip-hours × precio histórico de alquiler en la nube"; incluye margen de proveedor cloud (~67 %) |
| Capex de compra de hardware por adelantado | **$928.4M** | Costo de comprar (no alquilar) todo el clúster de GPUs de una sola vez |

- **Fuente:** Epoch AI, dataset "Notable AI Models" / "Frontier AI Models", fila `Llama 3.1-405B`
  (Organization: Meta AI; Training compute 3.8e+25 FLOP; Hardware quantity 16,384 × NVIDIA H100
  SXM5 80GB) — https://epoch.ai/models/llama-3-1-405b y
  https://epoch.ai/data/frontier_ai_models.csv — accessed 2026-09-26. Metodología general descrita
  en https://epoch.ai/data/ai-models-documentation/estimation .
- **Por qué este número y no otro:** hay estimaciones de terceros dispersas en redes/prensa que van
  de ~$60M a ~$640M (p. ej. un hilo de X de un analista, o "16k GPUs × $25–40k c/u"); Epoch AI es la
  única fuente que publica metodología reproducible y tres bases de cálculo distintas sobre el mismo
  registro verificado, así que es más defendible citarla a ella que un tuit suelto. El propio Meta
  **no publica** cifra de costo — por eso la etiqueta «estimado» es obligatoria en la diapositiva.

### 1d. RLHF — «hacer que le guste a la gente»

**Texto sugerido para la diapositiva (ES, una línea):**
> RLHF: personas comparan respuestas del modelo; esa preferencia humana entrena una señal de
> recompensa que ajusta el modelo para que sus respuestas gusten más.

- **Fuente primaria:** Ouyang et al. (OpenAI), "Training language models to follow instructions with
  human feedback" (el paper de InstructGPT), arXiv:2203.02155 —
  https://arxiv.org/abs/2203.02155 — accessed 2026-09-26.
- **Cita exacta:** "We then collect a dataset of rankings of model outputs, which we use to further
  fine-tune this supervised model using reinforcement learning from human feedback. We call the
  resulting models InstructGPT."
- El model card de Llama 3.1 también confirma que RLHF es la técnica estándar de alineación: "The
  tuned versions use supervised fine-tuning (SFT) and reinforcement learning with human feedback
  (RLHF) to align with human preferences for helpfulness and safety." (mismo model card de §1b).

### 1e. RLVR — «hacer que funcione en la computadora»

**Texto sugerido para la diapositiva (ES, una línea):**
> RLVR: en vez de que una persona califique la respuesta, un verificador automático (¿el resultado
> es correcto? ¿el código corre?) da la recompensa — sirve para tareas con respuesta comprobable
> (matemáticas, código).

- **Fuente primaria:** Lambert et al. (Ai2), "Tülu 3: Pushing Frontiers in Open Language Model
  Post-Training", arXiv:2411.15124 — https://arxiv.org/abs/2411.15124 (texto completo:
  https://arxiv.org/html/2411.15124v3) — accessed 2026-09-26. Este paper acuña y define el término.
- **Cita exacta (abstract):** "The training algorithms for our models include supervised
  finetuning (SFT), Direct Preference Optimization (DPO), and a novel method we call Reinforcement
  Learning with Verifiable Rewards (RLVR)."
- **Cita exacta (mecanismo, cuerpo del paper):** RLVR "only provide[s] rewards when the model's
  generations are verified to be correct", usando "a novel RL objective tailored to enhance specific
  skills with verifiable answers, such as mathematics and precise instruction following" — en
  contraste con RLHF, que entrena un modelo de recompensa aprendido a partir de preferencias
  humanas.
- **Nota secundaria (no es la fuente primaria, solo contexto):** Ai2 tiene una explicación en
  lenguaje llano en su blog: https://allenai.org/blog/tulu-3-technical — accessed 2026-09-26.

---

## 2 · Diapositiva 4 «Agente» — definición de Simon Willison

**Cita exacta (verbatim, verificada contra el HTML crudo de la página, no un resumen):**
> "An LLM agent runs tools in a loop to achieve a goal."

- **Fuente:** Simon Willison, "Agents", 18 September 2025 —
  https://simonwillison.net/2025/Sep/18/agents/ — accessed 2026-09-26.
- Contexto inmediato en el post (para que quien presente sepa de dónde sale): Willison explica que
  venía evitando la palabra "agente" por años por ser buzzword-bingo, y que esta es la definición que
  decidió adoptar "moving forward".

---

## 3 · Diapositiva 10 «Trampa 3» — «lethal trifecta» de Simon Willison

- **URL:** https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ — "The lethal trifecta for AI
  agents: private data, untrusted content, and external communication", 16 June 2025 — accessed
  2026-09-26.
- **Las tres capacidades (cita exacta, verbatim):**
  1. "Access to your private data—one of the most common purposes of tools in the first place!"
  2. "Exposure to untrusted content—any mechanism by which text (or images) controlled by a
     malicious attacker could become available to your LLM"
  3. "The ability to externally communicate in a way that could be used to steal your data"
- **Resumen en español para el presentador:** si un agente (1) puede leer tus datos privados, (2)
  puede recibir texto de una fuente no confiable (un email, una página web, una celda de una hoja de
  cálculo), y (3) puede comunicarse hacia afuera (llamar una API, mandar un link, hacer un request) —
  las tres juntas permiten que un atacante lo instruya, a través de ese contenido no confiable, para
  robar los datos privados y sacarlos por el canal de comunicación externo.

---

## 4 · Diapositiva 2 — Transformer Explainer (verificación de disponibilidad)

- **URL:** https://poloclub.github.io/transformer-explainer/
- **Verificado:** `curl` HTTP status **200**, `<title>Transformer Explainer: LLM Transformer Model
  Visually Explained</title>` — accessed 2026-09-26, 08:55 local. Carga sin errores; visualización
  interactiva de un GPT-2 (small, 124M parámetros) corriendo en el navegador vía ONNX Runtime.
  Confirmado independientemente por curl y por un fetch de contenido; ambos coinciden.
- **Riesgo para vivo:** es un sitio externo (GitHub Pages) fuera de nuestro control. Si el WiFi del
  venue falla o el sitio está caído el día de la clase, tener un screenshot/GIF de respaldo (no
  generado por WS2 — pedir a WS6 que capture uno antes de la clase como fallback).

---

## 5 · Diapositiva 5 «Ya los usamos» — logos

Ver `slides/assets/logos/ATTRIBUTION.md` para la tabla completa con fuente + licencia de cada
archivo. Resumen:

| Herramienta | Archivo | Fuente | Licencia |
|---|---|---|---|
| Anthropic Claude Code | `slides/assets/logos/claude-code.svg` | Simple Icons `simple-icons@16.32.0` (`claude.svg`) | CC0 1.0 |
| OpenAI Codex | `slides/assets/logos/openai-codex.svg` | `@lobehub/icons-static-svg@1.95.1` (`icons/codex.svg`), lobehub/lobe-icons | MIT (© 2023 LobeHub) |
| Cognition Devin Desktop | `slides/assets/logos/devin.svg` | `https://devin.ai/favicon.svg` (directo del sitio oficial de Cognition) | Sin licencia abierta publicada; marca registrada de Cognition AI — uso nominativo, sin modificar |
| OpenCode | `slides/assets/logos/opencode.svg` | Simple Icons `simple-icons@16.32.0` (`opencode.svg`) | CC0 1.0 |

Nota sobre Claude Code: Anthropic no publica un glifo separado para "Claude Code" distinto de la
marca "Claude"; el asterisco/estrella de Claude es lo que representa tanto al asistente como a la
CLI. Nota sobre Codex: OpenAI tampoco publica un asset de marca oficial descargable para Codex
específicamente (a diferencia de su logo general); se usó el glifo de LobeHub, que es la
representación visual estándar que circula para "Codex" (el mismo ícono con forma de nudo/flor usado
en la app de Codex) y está bajo licencia MIT, clara para uso en material de enseñanza.

---

## Todo lo demás que se buscó pero NO se usó (para que nadie lo re-busque)

- No se encontró un asset de marca oficial de Cognition/Devin con licencia explícita — solo el
  favicon de su propio sitio, que es la fuente más autorizada disponible sin recurrir a agregadores
  de terceros tipo Brandfetch/SeekLogo (que además no confirman licencia).
- No se encontró un ícono "Codex" separado dentro del repo oficial `github.com/openai/codex` (solo
  hay un PNG de splash para la CLI, no un logo/ícono de marca).
- Simple Icons **no tiene** slugs para `codex`, `devin` ni `cognition` (probado con HTTP HEAD contra
  `cdn.jsdelivr.net/npm/simple-icons@latest/icons/<slug>.svg`: 404 en los tres casos, 200 en
  `claude`, `anthropic`, `openai`, `opencode`).
