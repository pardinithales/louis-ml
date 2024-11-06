CREATE TABLE IF NOT EXISTS syndromes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syndrome_name TEXT NOT NULL,
    signs TEXT NOT NULL,
    locals TEXT,
    arteries TEXT,
    notes TEXT,
    is_ipsilateral BOOLEAN,
    local_name TEXT,
    vessel_name TEXT
);

CREATE TABLE IF NOT EXISTS signs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sign TEXT NOT NULL UNIQUE
);
