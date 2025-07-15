/* ───────────────────────────────────────────────
   Table: sources
   ─────────────────────────────────────────────── */
CREATE TABLE IF NOT EXISTS sources (
    id                SERIAL      PRIMARY KEY,
    name              TEXT        NOT NULL,
    url               TEXT        NOT NULL,
    type              TEXT        NOT NULL -- e.g., 'rss' or 'reddit'
);

/* ───────────────────────────────────────────────
   Table: articles
   ─────────────────────────────────────────────── */
CREATE TABLE IF NOT EXISTS articles (
    id                TEXT         PRIMARY KEY,
    title             TEXT         NOT NULL,
    body              TEXT,
    published_at      TIMESTAMPTZ  NOT NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    source            TEXT         NOT NULL REFERENCES sources(name),
    severity_score    REAL         NOT NULL,
    wide_scope_score  REAL         NOT NULL,
    high_impact_score REAL         NOT NULL,
);