SELECT
  p.question AS pregunta,
  o.label AS opcion,
  COUNT(v.id) AS votos
FROM polls p
JOIN poll_groups g ON g.id = p.group_id
JOIN poll_options o ON o.poll_id = p.id
LEFT JOIN poll_votes v
  ON v.poll_id = p.id AND v.option_id = o.id
WHERE g.code = '8P56ZUVE9Q'
  AND p.code = 'XF97N39'
GROUP BY p.id, p.question, o.id, o.label, o.position
ORDER BY o.position;
