# Demo en vivo: AI 4 Data

Abre una conversación nueva de Codex en este repositorio. Pega el prompt 0 una vez y después los siguientes, uno por turno. Espera a ver el SQL y los resultados antes de continuar. La secuencia completa toma aproximadamente 10–15 minutos, según la latencia del agente.

Encuesta: [AI 4 Data](https://h1sort.com/p/JFQES4AF97). Administración: [h1sort.com/polls](https://h1sort.com/polls).

La encuesta tiene seis preguntas de opción única; las escalas son opciones de texto `1` a `5`. La pregunta abierta sobre tareas para automatizar todavía no existe. Esta demo consulta una base transaccional compartida con el sitio: es una simplificación para un grupo pequeño, no el warehouse aislado del curso. Las instrucciones de solo lectura de estos prompts no sustituyen permisos técnicos de solo lectura.

## 0. Conectar y acordar cómo analizamos

```text
Eres mi analista durante una clase de AI for Data. Responde en español, con resultados breves que pueda proyectar. Vamos a analizar la encuesta real «AI 4 Data» mediante el MCP cloudflare-bindings, usando d1_database_query. No simules datos ni uses resultados de conversaciones anteriores.

Localiza la base D1 h1sort-chat con d1_databases_list y conserva su ID para las siguientes consultas. La encuesta se identifica por poll_groups.code = 'JFQES4AF97'; confirma también su título. No la confundas con real-time-processing-class, que es una encuesta de prueba.

Consulta únicamente el esquema necesario y estas tablas: poll_groups, polls, poll_options y poll_votes. Esta base también guarda chats del sitio: no consultes conversations, messages ni las tablas de autenticación. Usa exclusivamente SELECT, CTE de lectura y EXPLAIN QUERY PLAN. No escribas datos, cierres preguntas, cambies permisos ni modifiques el sitio. Si el MCP no está disponible, detente y explica el problema.

Verifica el esquema real antes de escribir las consultas. Relaciones esperadas: polls.group_id → poll_groups.id; poll_options.poll_id → polls.id; poll_votes.poll_id → polls.id y poll_votes.option_id → poll_options.id. Une opciones y votos por poll_id además de option_id. Una respuesta es un voto; un participante observable es un voter_hash distinto dentro de esta encuesta. El hash identifica un navegador, no garantiza una persona única. Úsalo para unir respuestas, pero nunca lo muestres ni exportes perfiles individuales.

Obtén un corte UTC con SELECT datetime('now', '-1 second') y conserva el valor literal. En los prompts 1–7 filtra siempre poll_votes.created_at <= ese corte: así las comparaciones usan la misma ventana aunque sigan entrando respuestas. No actualices el corte hasta el prompt 8. Conserva también el conjunto de preguntas y su estado; si detectas cambios de esquema, opciones o preguntas, avísame antes de comparar.

Resuelve los IDs reales y crea este mapa en memoria:
Q1: uso de IA para datos en los últimos 7 días (Sí/No).
Q2: haber usado un agente conectado a una base de datos (Sí/No).
Q3: confianza revisando SQL generado por IA (1–5).
Q4: confianza en un análisis generado por IA (1–5).
Q5: trabajo principal.
Q6: comprobación más rigurosa que hace habitualmente al recibir SQL de una IA.

Para cada respuesta posterior, muestra el corte, el SQL ejecutado con sus parámetros y un resultado compacto con numeradores y denominadores. No conviertas ausencias en No o cero; si no hay respuestas, una proporción o media es indefinida. No infieras el tamaño total del público a partir de quienes respondieron. Las comparaciones describen autoinformes de esta sala, no causalidad ni competencia demostrada. No fuerces hallazgos: si la muestra es pequeña, dilo. No ordenes segmentos por porcentajes cuando tengan menos de 5 respuestas válidas.

Ahora muestra solamente el mapa de las seis preguntas con sus opciones, estado y corte UTC. Detente y espera mi siguiente prompt.
```

## 1. ¿Cuánta gente ha participado?

```text
Con el corte acordado, calcula: navegadores que respondieron al menos una pregunta, número total de respuestas, participantes que completaron las seis y participantes con respuestas parciales. Muestra también respuestas y faltantes por pregunta, respecto de los navegadores participantes.

Comprueba que no hay más de una respuesta por participante y pregunta, que cada opción pertenece a su pregunta y que la suma de respuestas por pregunta coincide con el total. Si alguna comprobación falla, explica el problema antes de interpretar.

Concluye con una frase que distinga «personas en la sala», «navegadores participantes» y «respuestas». No llames abandono a una encuesta incompleta mientras siga abierta.
```

## 2. ¿Quién está en la sala y cuánto usa IA?

```text
Describe el perfil del grupo con Q5: recuento y porcentaje por rol entre quienes respondieron esa pregunta, incluyendo opciones con cero votos. Después calcula el porcentaje de Sí en Q1 y Q2, cada uno con su propio denominador.

Cruza Q1 con Q2 solo entre quienes respondieron ambas. Devuelve las cuatro combinaciones Sí/No con sus recuentos, incluidos ceros, y cuántos participantes quedan fuera por respuestas incompletas. Resume la diferencia entre usar IA recientemente y haber usado alguna vez un agente conectado a datos: son comportamientos y ventanas temporales distintos, no etapas de un embudo de conversión.
```

## 3. Confianza en revisar frente a confianza en el resultado

```text
Para Q3 y Q4, muestra la distribución completa de 1 a 5, n válido, mediana y porcentaje que marcó 4 o 5. Puedes añadir la media como resumen descriptivo de esta escala ordinal, sin tratarla como una medida precisa de capacidad.

Luego usa solo participantes con ambas respuestas y cuenta cuántos tienen Q3 > Q4, Q3 = Q4 y Q3 < Q4. Muestra el denominador pareado y las exclusiones. Si ayuda a explicar el patrón, dibuja una matriz 5×5 de recuentos.

¿La sala declara más confianza en revisar SQL o en aceptar un análisis generado por IA? Sustenta la respuesta con los datos; no llames a esto «confianza bien calibrada», porque no hemos medido desempeño real.
```

## 4. ¿Qué significa validar para esta sala?

```text
Analiza Q6 con recuentos y porcentajes por opción. Separa «No uso IA para generar SQL» de quienes sí la usan; no lo clasifiques como falta de validación. Entre las otras cuatro opciones, calcula por separado:
1. No valida.
2. Revisa el código.
3. Ejecuta y comprueba plausibilidad.
4. Compara con un resultado conocido o pruebas.

Conserva las etiquetas completas y declara el denominador. Como cada persona eligió su comprobación habitual más rigurosa, no podemos sumar estas respuestas como si fueran acciones independientes ni saber qué otras comprobaciones realiza.

Cierra con una observación sobre lo que la sala dice hacer y una pregunta para debatir la diferencia entre SQL que se ejecuta y una respuesta correcta.
```

## 5. ¿Coinciden confianza y hábitos de comprobación?

```text
Usa solo participantes con Q4 y Q6 contestadas. Excluye de este cruce «No uso IA para generar SQL» y muestra cuántos excluyes por esa razón y por respuestas faltantes, sin contar a nadie dos veces.

Cruza confianza alta en el análisis (Q4 = 4 o 5) frente a confianza 1–3 con las cuatro prácticas de validación. Muestra recuentos y porcentajes dentro de cada práctica, con denominadores. Destaca, si existe, cuántos declaran confianza alta y «No lo valido»; no los identifiques ni infieras que su trabajo es incorrecto.

Después compara la distribución de Q3 entre quienes contestaron Sí y No a Q2, usando únicamente pares completos para ese cruce. ¿Qué asociación descriptiva aparece entre experiencia con agentes y confianza para revisar SQL? No la conviertas en efecto causal ni hagas rankings con segmentos n < 5. Si no hay suficiente información, muestra las tablas y limita la conclusión.
```

## 6. El giro semántico: ¿cuántos están preparados?

```text
La pregunta del instructor es: «¿Qué porcentaje de la sala está preparado para trabajar con agentes?». Explica brevemente por qué esta encuesta no mide directamente esa preparación y qué definición y denominador faltan. No inventes una cifra única.

Para mostrar cómo cambia un indicador al cambiar su definición, usa el mismo conjunto de participantes con las seis respuestas completas y calcula estas tres convenciones de aula, explícitamente no validadas:
A. Adopción reciente: Q1 = Sí.
B. Adopción con experiencia: A y Q2 = Sí.
C. Adopción, experiencia y hábito de comprobación: B y Q6 = «Lo comparo con un resultado conocido o pruebas».

Muestra numerador, denominador común, porcentaje y cuántos participantes quedaron fuera por respuestas incompletas. Comprueba C <= B <= A. No uses las puntuaciones de confianza como prueba de competencia. Si no hay cuestionarios completos, muestra que los porcentajes son indefinidos.

Termina con una frase sobre por qué tres SQL válidos pueden dar tres números distintos y por qué necesitamos acordar la definición antes de llamar «preparación» a cualquiera de ellos. El denominador representa cuestionarios completos, no a toda la sala.
```

## 7. Convertir la descripción en decisiones para la clase

```text
Combina lo anterior en un resumen de máximo 200 palabras: tres observaciones respaldadas por n/N y dos ajustes concretos que propones para esta clase. Distingue cada observación de la decisión pedagógica que sugieres.

Usa el perfil de roles para elegir ejemplos, la experiencia con agentes para decidir cuánto explicar MCP y las prácticas de validación para decidir cuánto tiempo dedicar a SQL, contexto y pruebas. No conviertas una diferencia pequeña o un subgrupo diminuto en un titular. Si no hay suficientes respuestas, indica qué decisión todavía no está respaldada.

Termina con una pregunta de discusión conectada con la tesis del curso: producir análisis es barato; acordar el significado y comprobar la respuesta sigue requiriendo criterio.
```

## 8. Actualizar en vivo sin confundir cambios de muestra con cambios de opinión

```text
Conserva el corte anterior. Obtén un nuevo corte UTC con SELECT datetime('now', '-1 second') y repite los indicadores principales para ambos cortes usando exactamente las mismas definiciones: participantes, respuestas, cuestionarios completos, porcentajes de Sí en Q1 y Q2, confianza 4–5 en Q3 y Q4, y comparación con un resultado conocido o pruebas entre usuarios de IA para SQL en Q6.

Muestra «antes → ahora», n/N y la diferencia en puntos porcentuales donde ambos porcentajes estén definidos. Indica las respuestas nuevas en (corte anterior, corte nuevo] y separa navegadores nuevos de participantes anteriores que contestaron más preguntas. Comprueba que no disminuyan recuentos acumulados; si ocurre, investiga cambios de datos en vez de atribuirlos a opiniones.

Esto es acumulación de respuestas, no una encuesta antes/después de la clase: no digas que aumentó la confianza de las mismas personas ni que hubo aprendizaje. Si no cambió nada, dilo y termina. No hagas polling continuo. Conserva el nuevo corte como referencia para la siguiente actualización que yo solicite.
```
