CREATE TABLE Users(
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255),
    role INTEGER,

    FOREIGN KEY (role) REFERENCES Role(id),
    PRIMARY KEY (username)
);

CREATE TABLE Roles(
    id INTEGER,
    title VARCHAR(64),

    PRIMARY KEY (id)
);
