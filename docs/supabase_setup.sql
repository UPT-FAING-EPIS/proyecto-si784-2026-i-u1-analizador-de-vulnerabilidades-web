-- =====================================================
-- VulnScan - Tabla de escaneos en Supabase
-- Ejecutar en: Supabase Dashboard → SQL Editor
-- =====================================================

-- Crear tabla principal de escaneos
CREATE TABLE IF NOT EXISTS scans (
    id            TEXT PRIMARY KEY,
    url           TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending',
    progress      INTEGER DEFAULT 0,
    current_task  TEXT,
    started_at    DOUBLE PRECISION,
    completed_at  DOUBLE PRECISION,
    results       TEXT,          -- JSON serializado como texto
    error         TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_scans_status     ON scans(status);
CREATE INDEX IF NOT EXISTS idx_scans_started_at ON scans(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);

-- Política de acceso público (Row Level Security desactivado para API key)
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

-- Permitir todas las operaciones con la API key del servidor
CREATE POLICY "allow_all_with_service_key"
  ON scans
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- Verificar que la tabla se creó correctamente
-- =====================================================
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'scans'
ORDER BY ordinal_position;
