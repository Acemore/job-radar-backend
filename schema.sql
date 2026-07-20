CREATE TABLE vacancies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    salary INTEGER,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE vacancy_tags (
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    FOREIGN KEY (vacancy_id) REFERENCES vacancies(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
