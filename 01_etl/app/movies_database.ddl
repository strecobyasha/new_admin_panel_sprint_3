CREATE SCHEMA IF NOT EXISTS content;

-- Таблица фильмов.
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- Таблица каких-то людей, которые затем станут...
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- ...актерами, режиссерами, кофеносильщиками (role) в конкретном фильме (film_work_id).
-- ВАЖНО: одна строка - одна роль. Для людей-оркестров нужно создавать несколько строк.
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone
);

-- Таблица жанров.
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- Таблица связей между жанрами и фильмами (одна строка - одна связь "жанр-фильм").
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    created timestamp with time zone
);

-- Индекс для фильтра по дате или по дате и рейтингу.
CREATE INDEX IF NOT EXISTS 
film_work_creation_rating_idx ON content.film_work
(creation_date, rating);
-- Уникальный индекс для связки "фильм-человек-роль".
CREATE UNIQUE INDEX IF NOT EXISTS 
film_work_person_role_idx ON content.person_film_work
(film_work_id, person_id, role);
-- Уникальный индекс для связки "фильм-жанр".
CREATE UNIQUE INDEX IF NOT EXISTS 
film_work_genre_idx ON content.genre_film_work
(film_work_id, genre_id);
