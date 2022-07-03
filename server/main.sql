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
-- Table structure for rooms
-- ----------------------------
DROP TABLE IF EXISTS "main"."rooms";
CREATE TABLE "rooms" (
"id"  INTEGER NOT NULL,
"room_name"  TEXT,
PRIMARY KEY ("id")
);

-- ----------------------------
-- Table structure for room_user
-- ----------------------------
DROP TABLE IF EXISTS "main"."room_user";
CREATE TABLE "room_user" (
"id"  INTEGER NOT NULL,
"room_id"  INTEGER,
"user_id"  INTEGER,
PRIMARY KEY ("id")
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
