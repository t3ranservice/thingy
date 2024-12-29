CREATE TABLE "transactions" (
	"id"	INTEGER,
	"spot_pair"	TEXT,
	"direction"	TEXT,
	"filled_value"	REAL,
	"filled_price"	REAL,
	"filled_quantity" REAL,
	"fee" REAL,
	"timestamp"	INTEGER,
	"transaction_id" UNIQUE ON CONFLICT IGNORE,
	PRIMARY KEY("id") ON CONFLICT FAIL
);