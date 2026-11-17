USE gasolineras_db;

CREATE TABLE Provincia (
    id_provincia INT PRIMARY KEY,
    nombre_provincia VARCHAR(100) NOT NULL
);

CREATE TABLE Municipio (
    id_municipio INT PRIMARY KEY,
    nombre_municipio VARCHAR(150) NOT NULL,
    id_provincia INT,
    FOREIGN KEY (id_provincia) REFERENCES Provincia(id_provincia)
);

CREATE TABLE Localidad (
    id_localidad INT PRIMARY KEY,
    nombre_localidad VARCHAR(150) NOT NULL,
    id_municipio INT,
    FOREIGN KEY (id_municipio) REFERENCES Municipio(id_municipio)
);

CREATE TABLE Empresa (
    id_empresa INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL
);

CREATE TABLE Estacion (
    id_estacion INT PRIMARY KEY,
    tipo_estacion VARCHAR(50), 
    direccion VARCHAR(255),
    codigo_postal VARCHAR(10),
    latitud DECIMAL(10, 6),
    longitud DECIMAL(10, 6),
    margen VARCHAR(5),
    horario VARCHAR(255),
    id_localidad INT,
    id_empresa INT,
    FOREIGN KEY (id_localidad) REFERENCES Localidad(id_localidad),
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
);

CREATE TABLE Combustible (
    id_combustible INT PRIMARY KEY AUTO_INCREMENT,
    tipo_combustible VARCHAR(100) NOT NULL
);

CREATE TABLE Precio_Historico (
    id_estacion INT,
    id_combustible INT,
    precio DECIMAL(6, 3),
    fecha_actualizacion VARCHAR(50), 
    PRIMARY KEY (id_estacion, id_combustible),
    FOREIGN KEY (id_estacion) REFERENCES Estacion(id_estacion),
    FOREIGN KEY (id_combustible) REFERENCES Combustible(id_combustible)
);