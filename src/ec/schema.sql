CREATE TABLE users (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       fbid BIGINT,
       fb_access_token TEXT,
       INDEX (fbid)
       );

CREATE TABLE exercise_types (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       name TEXT,
       description TEXT,
       );

CREATE TABLE measures (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       exercise_type_id INT NOT NULL,
       unit TEXT,
       FOREIGN KEY (exercise_type_id) REFERENCES exercise_types(id)
               ON DELETE CASCADE ON UPDATE CASCADE
       );

CREATE TABLE entries (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       user_id INT NOT NULL,
       date DATE NOT NULL,
       exercise_type INT NOT NULL,
       FOREIGN KEY (user_id) REFERENCES users(id)
               ON DELETE CASCADE ON UPDATE CASCADE,
       FOREIGN KEY (exercise_type) REFERENCES exercise_types(id)
               ON DELETE CASCADE ON UPDATE CASCADE,
       INDEX (date),
       INDEX (user_id),
       INDEX (exercise_type)
       );

CREATE TABLE data_points (
       id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       entry_id INT NOT NULL,
       measure_id INT NOT NULL,
       `value` TEXT,
       FOREIGN KEY (entry_id) REFERENCES entries(id)
               ON DELETE CASCADE ON UPDATE CASCADE,
       FOREIGN KEY (measure_id) REFERENCES measures(id)
               ON DELETE CASCADE ON UPDATE CASCADE
       );

CREATE TABLE cache (
       `key` VARCHAR(512) NOT NULL PRIMARY KEY,
       `value` TEXT NOT NULL,
       INDEX (`key`)
       );