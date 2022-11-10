-- for /data/data.db

CREATE TABLE if not exists "notify" (
	"id"	INTEGER NOT NULL UNIQUE
);

CREATE TABLE if not exists "cache"  (
	"title"	TEXT UNIQUE,
	"data"	TEXT
);

INSERT INTO "cache" ("title", "data") VALUES ("list", "{}");
INSERT INTO "cache" ("title", "data") VALUES ("circular", "{}");
