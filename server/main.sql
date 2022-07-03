PRAGMA foreign_keys = OFF;

-- ----------------------------
-- Table structure for chat_history
-- ----------------------------
DROP TABLE IF EXISTS "main"."chat_history";
CREATE TABLE "chat_history" (
"id"  INTEGER NOT NULL,
"user_id"  INTEGER,
"target_id"  INTEGER,
"target_type"  TEXT,
"data"  BLOB,
"sent"  INTEGER,
PRIMARY KEY ("id" ASC)
);

-- ----------------------------
-- Table structure for friends
-- ----------------------------
DROP TABLE IF EXISTS "main"."friends";
CREATE TABLE "friends" (
"from_user_id"  INTEGER NOT NULL,
"to_user_id"  INTEGER NOT NULL,
"accepted"  TEXT,
PRIMARY KEY ("from_user_id" ASC, "to_user_id")
);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "main"."users";
CREATE TABLE "users" (
"id"  INTEGER NOT NULL,
"username"  TEXT,
"password"  TEXT,
"email"  TEXT,
"ip"  TEXT,
"port" TEXT,
"sex"  TEXT,
"age"  TEXT,
"pk"  TEXT,
PRIMARY KEY ("id" ASC)
);
