-- Pagila Schema for QueryPilot MCP
-- Standard PostgreSQL DVD Rental Sample Database Schema

CREATE TABLE language (
    language_id SERIAL PRIMARY KEY,
    name CHARACTER(20) NOT NULL,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name CHARACTER VARYING(25) NOT NULL,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE actor (
    actor_id SERIAL PRIMARY KEY,
    first_name CHARACTER VARYING(45) NOT NULL,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    last_name CHARACTER VARYING(45) NOT NULL
);

CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    country CHARACTER VARYING(50) NOT NULL,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE city (
    city_id SERIAL PRIMARY KEY,
    city CHARACTER VARYING(50) NOT NULL,
    country_id SMALLINT NOT NULL REFERENCES country(country_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE address (
    address_id SERIAL PRIMARY KEY,
    address CHARACTER VARYING(50) NOT NULL,
    address2 CHARACTER VARYING(50),
    district CHARACTER VARYING(20) NOT NULL,
    city_id SMALLINT NOT NULL REFERENCES city(city_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    postal_code CHARACTER VARYING(10),
    phone CHARACTER VARYING(20) NOT NULL,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE film (
    film_id SERIAL PRIMARY KEY,
    title CHARACTER VARYING(255) NOT NULL,
    description TEXT,
    release_year INTEGER,
    language_id SMALLINT NOT NULL REFERENCES language(language_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    rental_duration SMALLINT DEFAULT 3 NOT NULL,
    rental_rate NUMERIC(4,2) DEFAULT 4.99 NOT NULL,
    length SMALLINT,
    replacement_cost NUMERIC(5,2) DEFAULT 19.99 NOT NULL,
    rating VARCHAR(10) DEFAULT 'G',
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    special_features TEXT[]
);

CREATE TABLE film_actor (
    actor_id SMALLINT NOT NULL REFERENCES actor(actor_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    film_id SMALLINT NOT NULL REFERENCES film(film_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (actor_id, film_id)
);

CREATE TABLE film_category (
    film_id SMALLINT NOT NULL REFERENCES film(film_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    category_id SMALLINT NOT NULL REFERENCES category(category_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (film_id, category_id)
);

CREATE TABLE store (
    store_id SERIAL PRIMARY KEY,
    manager_staff_id SMALLINT,
    address_id SMALLINT NOT NULL REFERENCES address(address_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE staff (
    staff_id SERIAL PRIMARY KEY,
    first_name CHARACTER VARYING(45) NOT NULL,
    last_name CHARACTER VARYING(45) NOT NULL,
    address_id SMALLINT NOT NULL REFERENCES address(address_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    email CHARACTER VARYING(50),
    store_id SMALLINT NOT NULL REFERENCES store(store_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    active BOOLEAN DEFAULT true NOT NULL,
    username CHARACTER VARYING(16) NOT NULL,
    password CHARACTER VARYING(40),
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    store_id SMALLINT NOT NULL REFERENCES store(store_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    first_name CHARACTER VARYING(45) NOT NULL,
    last_name CHARACTER VARYING(45) NOT NULL,
    email CHARACTER VARYING(50),
    address_id SMALLINT NOT NULL REFERENCES address(address_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    activebool BOOLEAN DEFAULT true NOT NULL,
    create_date DATE DEFAULT ('now'::text)::date NOT NULL,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    active INTEGER DEFAULT 1
);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    film_id SMALLINT NOT NULL REFERENCES film(film_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    store_id SMALLINT NOT NULL REFERENCES store(store_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE rental (
    rental_id SERIAL PRIMARY KEY,
    rental_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    inventory_id INTEGER NOT NULL REFERENCES inventory(inventory_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    customer_id SMALLINT NOT NULL REFERENCES customer(customer_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    return_date TIMESTAMP WITHOUT TIME ZONE,
    staff_id SMALLINT NOT NULL REFERENCES staff(staff_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    last_update TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE payment (
    payment_id SERIAL PRIMARY KEY,
    customer_id SMALLINT NOT NULL REFERENCES customer(customer_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    staff_id SMALLINT NOT NULL REFERENCES staff(staff_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    rental_id INTEGER REFERENCES rental(rental_id) ON UPDATE CASCADE ON DELETE SET NULL,
    amount NUMERIC(5,2) NOT NULL,
    payment_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

-- Indexes for performance and analytical lookups
CREATE INDEX idx_film_title ON film(title);
CREATE INDEX idx_film_actor_film_id ON film_actor(film_id);
CREATE INDEX idx_customer_last_name ON customer(last_name);
CREATE INDEX idx_rental_customer_id ON rental(customer_id);
CREATE INDEX idx_payment_customer_id ON payment(customer_id);
