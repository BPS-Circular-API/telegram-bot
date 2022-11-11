-- for /data/data.db

CREATE TABLE if not exists "notify" (
	"id"	INTEGER NOT NULL UNIQUE
);

CREATE TABLE if not exists "cache"  (
	"title"	BLOB UNIQUE,
	"data"	BLOB
);

INSERT INTO "cache" ("title", "data") VALUES ("list", "{}");
INSERT INTO "cache" ("title", "data") VALUES ("circular", "{}");
