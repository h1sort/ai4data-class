-- Table-level Unity Catalog access for the instructor running notebooks 01–03.
-- Replace the principal if the presenting Databricks account changes.
-- No catalog- or schema-level privileges are granted here.
GRANT SELECT ON TABLE workspace.ai4data.c1_dim_participante TO `__INSTRUCTOR_PRINCIPAL__`;
GRANT SELECT ON TABLE workspace.ai4data.c1_fct_respuestas TO `__INSTRUCTOR_PRINCIPAL__`;
GRANT SELECT ON TABLE workspace.ai4data.c1_vw_resumen_respuestas TO `__INSTRUCTOR_PRINCIPAL__`;
GRANT SELECT ON TABLE workspace.ai4data.dim_participante TO `__INSTRUCTOR_PRINCIPAL__`;
