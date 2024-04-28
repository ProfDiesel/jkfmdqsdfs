.load vss0

CREATE TABLE IF NOT EXISTS ${TABLE} (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    payload BLOB,
    embedding BLOB
);

CREATE VIRTUAL TABLE IF NOT EXISTS vss_${TABLE} USING vss0 (
    embedding(${DIMENSIONALITY})
);

CREATE TRIGGER IF NOT EXISTS embed_text 
AFTER INSERT ON ${TABLE}
BEGIN
    INSERT INTO vss_${TABLE}(rowid, embedding)
    VALUES (new.rowid, new.embedding);
END;

