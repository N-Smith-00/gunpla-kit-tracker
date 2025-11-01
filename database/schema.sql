--- TABLES
CREATE TABLE IF NOT EXISTS Kit (
    kit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    scale TEXT NOT NULL,
    brand TEXT,
    grade TEXT,
    grade_key TEXT GENERATED ALWAYS AS (
        COALESCE(grade, "NO_GRADE")
    ) STORED,
    UNIQUE(name, scale, grade_key)
);

CREATE TABLE IF NOT EXISTS Store (
    store_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    street_addr TEXT,
    province TEXT,
    country TEXT
);

CREATE TABLE IF NOT EXISTS AccessoryType (
    type_name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Accessory (
    accessory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    kit_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    brand TEXT,
    type_name TEXT NOT NULL,
    FOREIGN KEY (kit_id) REFERENCES Kit(kit_id)
        ON DELETE CASCADE,
    FOREIGN KEY (type_name) REFERENCES AccessoryType(type_name)
        ON DELETE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS KitSoldBy (
    kit_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    price REAL NOT NULL,
    link TEXT NOT NULL,
    PRIMARY KEY (kit_id, store_id),
    FOREIGN KEY (kit_id) REFERENCES Kit(kit_id)
        ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES Store(store_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS AccSoldBy (
    accessory_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    price REAL NOT NULL,
    link TEXT NOT NULL,
    PRIMARY KEY (accessory_id, store_id),
    FOREIGN KEY (accessory_id) REFERENCES Accessory(accessory_id)
        ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES Store(store_id)
        ON DELETE CASCADE
);