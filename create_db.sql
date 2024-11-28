CREATE TABLE "historical_data" (
	"id"	INTEGER,
	"spot_pair"	TEXT,
	"filled_value"	REAL,
	"filled_price"	REAL,
	"direction"	TEXT,
	"timestamp"	INTEGER,
	"transaction_id" UNIQUE ON CONFLICT IGNORE,
	PRIMARY KEY("id") ON CONFLICT FAIL
);