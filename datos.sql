-- =============================================
-- CREAR TABLAS
-- =============================================

CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(50),
    imagen_url VARCHAR(255),
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    tipo_cliente VARCHAR(50),
    cliente_frecuente BOOLEAN DEFAULT FALSE,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    usuario_id INT,
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    cantidad INT NOT NULL DEFAULT 0,
    valor_unitario NUMERIC(10,2) NOT NULL,
    valor_mayorista NUMERIC(10,2),
    categoria_id INT,
    imagen_url VARCHAR(255),
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_productos_categorias
        FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE SET NULL
);

CREATE TABLE compras (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario_aplicado NUMERIC(10,2) NOT NULL,
    total NUMERIC(12,2) NOT NULL,
    fecha TIMESTAMP DEFAULT NOW(),
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_compras_clientes
        FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
    CONSTRAINT fk_compras_productos
        FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE CASCADE
);

CREATE TABLE historial_eliminados (
    id SERIAL PRIMARY KEY,
    tabla VARCHAR(50) NOT NULL,
    registro_id INT NOT NULL,
    datos JSONB,
    eliminado_en TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- INSERTAR CATEGORÍAS DE PAPELERÍA
-- =============================================
INSERT INTO categorias (nombre, codigo, imagen_url) VALUES
('Escritura', 'ESC001', NULL),
('Cuadernos', 'CUA001', NULL),
('Papel', 'PAP001', NULL),
('Oficina', 'OFI001', NULL),
('Escolar', 'ESC002', NULL),
('Arte', 'ART001', NULL);

-- =============================================
-- INSERTAR CLIENTES
-- =============================================
INSERT INTO clientes (nombre, cedula, tipo_cliente, cliente_frecuente, telefono, direccion) VALUES
('Carlos Rodriguez', '1001234567', 'minorista', FALSE, '3101234567', 'Calle 45 #12-34'),
('Maria Lopez', '1009876543', 'mayorista', TRUE, '3209876543', 'Carrera 15 #67-89'),
('Juan Martinez', '1006789012', 'minorista', FALSE, '3156789012', 'Avenida 30 #45-67'),
('Ana Garcia', '1002345678', 'minorista', FALSE, '3182345678', 'Calle 78 #23-45'),
('Pedro Hernandez', '1003456789', 'mayorista', FALSE, '3123456789', 'Carrera 50 #12-34'),
('Laura Sanchez', '1005678901', 'minorista', TRUE, '3145678901', 'Calle 100 #56-78'),
('Diego Ramirez', '1007890123', 'minorista', FALSE, '3167890123', 'Avenida 68 #34-56'),
('Sofia Torres', '1008901234', 'mayorista', FALSE, '3178901234', 'Carrera 7 #89-01'),
('Andres Gomez', '1009012345', 'minorista', FALSE, '3189012345', 'Calle 22 #45-67'),
('Camila Diaz', '1000123456', 'minorista', TRUE, '3190123456', 'Avenida 19 #78-90'),
('Felipe Moreno', '1011234567', 'mayorista', FALSE, '3111234567', 'Carrera 33 #12-45'),
('Valentina Vargas', '1012345678', 'minorista', FALSE, '3132345678', 'Calle 55 #67-89'),
('Sebastian Castro', '1013456789', 'minorista', FALSE, '3153456789', 'Avenida 40 #23-56'),
('Isabella Ortiz', '1014567890', 'mayorista', TRUE, '3174567890', 'Carrera 25 #78-01'),
('Nicolas Rojas', '1015678901', 'minorista', FALSE, '3195678901', 'Calle 80 #34-67');

-- =============================================
-- INSERTAR PRODUCTOS DE PAPELERÍA
-- =============================================
INSERT INTO productos (nombre, descripcion, cantidad, valor_unitario, valor_mayorista, categoria_id, imagen_url) VALUES
('Lapiz Mirado #2', 'Lapiz grafito punta media', 500, 800.00, 600.00, 1, NULL),
('Boligrafo Kilometric azul', 'Boligrafo tinta azul', 400, 1200.00, 900.00, 1, NULL),
('Boligrafo Kilometric negro', 'Boligrafo tinta negra', 350, 1200.00, 900.00, 1, NULL),
('Boligrafo Kilometric rojo', 'Boligrafo tinta roja', 300, 1200.00, 900.00, 1, NULL),
('Marcador permanente Sharpie', 'Marcador punta fina negro', 150, 3500.00, 2800.00, 1, NULL),
('Resaltador amarillo', 'Resaltador punta biselada', 200, 2800.00, 2200.00, 1, NULL),
('Portaminas 0.5mm', 'Portaminas mecanico', 120, 4500.00, 3500.00, 1, NULL),
('Cuaderno cuadriculado 100h', 'Cuaderno argollado cuadriculado', 180, 5500.00, 4200.00, 2, NULL),
('Cuaderno rayado 100h', 'Cuaderno argollado rayado', 200, 5500.00, 4200.00, 2, NULL),
('Cuaderno cuadriculado 50h', 'Cuaderno cosido cuadriculado', 250, 3200.00, 2500.00, 2, NULL),
('Libreta pequeña', 'Libreta de notas 80 hojas', 150, 2500.00, 1800.00, 2, NULL),
('Agenda 2024', 'Agenda ejecutiva diaria', 50, 25000.00, 20000.00, 2, NULL),
('Resma papel carta', 'Resma 500 hojas papel bond', 100, 15000.00, 12000.00, 3, NULL),
('Resma papel oficio', 'Resma 500 hojas papel bond', 80, 17000.00, 13500.00, 3, NULL),
('Cartulina pliego', 'Cartulina colores surtidos', 300, 1500.00, 1200.00, 3, NULL),
('Papel silueta', 'Papel silueta colores', 400, 800.00, 600.00, 3, NULL),
('Carpeta legajadora', 'Carpeta plastica con gancho', 150, 4500.00, 3500.00, 4, NULL),
('Folder carta', 'Folder manila carta', 500, 600.00, 400.00, 4, NULL),
('Caja clips', 'Clips metalicos x100', 200, 2000.00, 1500.00, 4, NULL),
('Grapadora', 'Grapadora metalica mediana', 60, 12000.00, 10000.00, 4, NULL),
('Caja grapas', 'Grapas estandar x5000', 180, 3500.00, 2800.00, 4, NULL),
('Tijeras escolares', 'Tijeras punta roma', 150, 3000.00, 2300.00, 5, NULL),
('Sacapuntas metalico', 'Sacapuntas doble orificio', 250, 1500.00, 1100.00, 5, NULL),
('Borrador nata', 'Borrador blanco suave', 400, 1000.00, 700.00, 5, NULL),
('Caja colores x12', 'Colores largos 12 unidades', 100, 8500.00, 6500.00, 5, NULL),
('Caja colores x24', 'Colores largos 24 unidades', 80, 15000.00, 12000.00, 5, NULL),
('Regla 30cm', 'Regla plastica transparente', 200, 1200.00, 900.00, 5, NULL),
('Compas escolar', 'Compas metalico con lapiz', 90, 5500.00, 4200.00, 5, NULL),
('Temperas x6', 'Set temperas 6 colores', 100, 7500.00, 5800.00, 6, NULL),
('Acuarelas x12', 'Estuche acuarelas 12 colores', 70, 9500.00, 7500.00, 6, NULL),
('Pinceles set x5', 'Set 5 pinceles surtidos', 60, 8000.00, 6200.00, 6, NULL),
('Block cartulina', 'Block 20 hojas colores', 120, 6500.00, 5000.00, 6, NULL);

-- =============================================
-- INSERTAR 50 COMPRAS (ejemplos simplificados)
-- =============================================
INSERT INTO compras (cliente_id, producto_id, cantidad, precio_unitario_aplicado, total) VALUES
(1, 1, 5, 800.00, 4000.00),
(1, 8, 2, 5500.00, 11000.00),
(2, 2, 3, 1200.00, 3600.00),
(2, 11, 1, 2500.00, 2500.00),
(3, 13, 1, 15000.00, 15000.00),
(3, 19, 3, 2000.00, 6000.00),
(4, 5, 1, 3500.00, 3500.00),
(4, 6, 1, 2800.00, 2800.00),
(5, 14, 1, 17000.00, 17000.00),
(5, 25, 1, 8500.00, 8500.00),
(6, 9, 2, 5500.00, 11000.00),
(6, 18, 2, 600.00, 1200.00),
(7, 13, 2, 15000.00, 30000.00),
(7, 1, 10, 800.00, 8000.00),
(8, 14, 1, 17000.00, 17000.00),
(8, 2, 3, 1200.00, 3600.00),
(8, 3, 2, 1200.00, 2400.00),
(9, 12, 1, 25000.00, 25000.00),
(9, 17, 1, 4500.00, 4500.00),
(10, 10, 2, 3200.00, 6400.00),
(10, 6, 1, 2800.00, 2800.00),
(11, 7, 1, 4500.00, 4500.00),
(11, 11, 2, 2500.00, 5000.00),
(12, 15, 3, 1500.00, 4500.00),
(12, 16, 4, 800.00, 3200.00),
(13, 20, 1, 12000.00, 12000.00),
(13, 21, 2, 3500.00, 7000.00),
(14, 24, 5, 1000.00, 5000.00),
(14, 26, 2, 15000.00, 30000.00),
(15, 27, 1, 5500.00, 5500.00),
(1, 28, 3, 7500.00, 22500.00),
(2, 29, 2, 9500.00, 19000.00),
(3, 30, 1, 8000.00, 8000.00),
(4, 31, 2, 6500.00, 13000.00),
(5, 4, 4, 1200.00, 4800.00),
(6, 5, 2, 3500.00, 7000.00),
(7, 22, 3, 3000.00, 9000.00),
(8, 23, 1, 1500.00, 1500.00),
(9, 1, 6, 800.00, 4800.00),
(10, 8, 1, 5500.00, 5500.00),
(11, 9, 2, 5500.00, 11000.00),
(12, 10, 1, 3200.00, 3200.00),
(13, 12, 1, 25000.00, 25000.00),
(14, 13, 1, 15000.00, 15000.00),
(15, 14, 2, 17000.00, 34000.00),
(1, 24, 4, 1000.00, 4000.00),
(2, 25, 1, 8500.00, 8500.00),
(3, 26, 3, 15000.00, 45000.00),
(4, 27, 2, 5500.00, 11000.00),
(5, 28, 1, 7500.00, 7500.00);
