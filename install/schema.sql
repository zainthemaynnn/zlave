CREATE TABLE users (id INTEGER PRIMARY KEY);
CREATE TABLE guilds (id INTEGER PRIMARY KEY, prefix TEXT NOT NULL, auto_response INTEGER NOT NULL);
CREATE TABLE funnypts (awarder INTEGER, awardee INTEGER, reason TEXT NOT NULL, operation INTEGER NOT NULL, date TIMESTAMP NOT NULL, FOREIGN KEY (awarder) REFERENCES users (id), FOREIGN KEY (awardee) REFERENCES users (id));
CREATE INDEX awarder_index ON funnypts (awarder);
CREATE INDEX awardee_index ON funnypts (awardee);