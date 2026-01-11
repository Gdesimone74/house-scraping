-- Tabla de propiedades
CREATE TABLE IF NOT EXISTS propiedades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT NOT NULL,
    url TEXT NOT NULL,
    titulo TEXT NOT NULL,
    precio DECIMAL,
    moneda TEXT DEFAULT 'USD' CHECK (moneda IN ('USD', 'ARS')),
    barrio TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('departamento', 'casa')),
    ambientes INTEGER,
    dormitorios INTEGER,
    banos INTEGER,
    metros_cuadrados DECIMAL,
    metros_totales DECIMAL,
    fotos TEXT[] DEFAULT '{}',
    descripcion TEXT,
    fuente TEXT NOT NULL CHECK (fuente IN ('mercadolibre', 'zonaprop', 'argenprop')),
    operacion TEXT DEFAULT 'venta' CHECK (operacion IN ('venta', 'alquiler')),
    fecha_publicacion TIMESTAMPTZ,
    fecha_primer_visto TIMESTAMPTZ DEFAULT NOW(),
    fecha_ultima_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    activo BOOLEAN DEFAULT TRUE,

    -- Unique constraint para evitar duplicados
    UNIQUE(external_id, fuente)
);

-- Índices para búsquedas eficientes
CREATE INDEX IF NOT EXISTS idx_propiedades_barrio ON propiedades(barrio);
CREATE INDEX IF NOT EXISTS idx_propiedades_precio ON propiedades(precio);
CREATE INDEX IF NOT EXISTS idx_propiedades_tipo ON propiedades(tipo);
CREATE INDEX IF NOT EXISTS idx_propiedades_fuente ON propiedades(fuente);
CREATE INDEX IF NOT EXISTS idx_propiedades_activo ON propiedades(activo);
CREATE INDEX IF NOT EXISTS idx_propiedades_fecha_primer_visto ON propiedades(fecha_primer_visto DESC);
CREATE INDEX IF NOT EXISTS idx_propiedades_activo_fecha ON propiedades(activo, fecha_primer_visto DESC);

-- Función para actualizar fecha_ultima_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_fecha_ultima_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_ultima_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar automáticamente
DROP TRIGGER IF EXISTS trigger_update_fecha ON propiedades;
CREATE TRIGGER trigger_update_fecha
    BEFORE UPDATE ON propiedades
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_ultima_actualizacion();

-- Enable Row Level Security (opcional, para mayor seguridad)
ALTER TABLE propiedades ENABLE ROW LEVEL SECURITY;

-- Política para permitir lectura pública
CREATE POLICY "Permitir lectura publica" ON propiedades
    FOR SELECT USING (true);

-- Política para permitir escritura con service key
CREATE POLICY "Permitir escritura con service key" ON propiedades
    FOR ALL USING (true) WITH CHECK (true);
