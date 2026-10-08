-- Pagila Sample Data for QueryPilot MCP

INSERT INTO language (language_id, name) VALUES
(1, 'English'),
(2, 'Italian'),
(3, 'Japanese'),
(4, 'Mandarin'),
(5, 'French'),
(6, 'German');

INSERT INTO category (category_id, name) VALUES
(1, 'Action'),
(2, 'Animation'),
(3, 'Children'),
(4, 'Classics'),
(5, 'Comedy'),
(6, 'Documentary'),
(7, 'Drama'),
(8, 'Family'),
(9, 'Foreign'),
(10, 'Games'),
(11, 'Horror'),
(12, 'Music'),
(13, 'New'),
(14, 'Sci-Fi'),
(15, 'Sports'),
(16, 'Travel');

INSERT INTO country (country_id, country) VALUES
(1, 'United States'),
(2, 'Canada'),
(3, 'United Kingdom'),
(4, 'Australia'),
(5, 'Germany'),
(6, 'Japan');

INSERT INTO city (city_id, city, country_id) VALUES
(1, 'New York', 1),
(2, 'Los Angeles', 1),
(3, 'Toronto', 2),
(4, 'London', 3),
(5, 'Sydney', 4),
(6, 'Berlin', 5),
(7, 'Tokyo', 6);

INSERT INTO address (address_id, address, address2, district, city_id, postal_code, phone) VALUES
(1, '123 Main St', 'Apt 4B', 'California', 2, '90001', '555-0101'),
(2, '456 Broadway', NULL, 'New York', 1, '10001', '555-0102'),
(3, '789 Queen St', NULL, 'Ontario', 3, 'M5V2A8', '555-0103'),
(4, '10 Oxford St', NULL, 'England', 4, 'W1D1BS', '555-0104'),
(5, '25 George St', NULL, 'NSW', 5, '2000', '555-0105');

INSERT INTO store (store_id, manager_staff_id, address_id) VALUES
(1, 1, 1),
(2, 2, 2);

INSERT INTO staff (staff_id, first_name, last_name, address_id, email, store_id, active, username, password) VALUES
(1, 'Mike', 'Hillyer', 1, 'mike.hillyer@sakilastaff.com', 1, true, 'Mike', '8cb2237d0679ca88db6464eac60da96345513964'),
(2, 'Jon', 'Stephens', 2, 'jon.stephens@sakilastaff.com', 2, true, 'Jon', '8cb2237d0679ca88db6464eac60da96345513964');

INSERT INTO actor (actor_id, first_name, last_name) VALUES
(1, 'Penelope', 'Guiness'),
(2, 'Nick', 'Wahlberg'),
(3, 'Ed', 'Chase'),
(4, 'Jennifer', 'Davis'),
(5, 'Johnny', 'Lollobrigida'),
(6, 'Bette', 'Nicholson'),
(7, 'Grace', 'Mostel'),
(8, 'Matthew', 'Johansson'),
(9, 'Joe', 'Swank'),
(10, 'Christian', 'Gable');

INSERT INTO film (film_id, title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating, special_features) VALUES
(1, 'ACADEMY DINOSAUR', 'A Epic Drama of a Feminist And a Mad Scientist who must Battle a Teacher in The Canadian Rockies', 2006, 1, 6, 0.99, 86, 20.99, 'PG', ARRAY['Deleted Scenes', 'Behind the Scenes']),
(2, 'ACE GOLDFINGER', 'A Astounding Epistle of a Database Administrator And an Explorer who must Find a Car in Ancient China', 2006, 1, 3, 4.99, 48, 12.99, 'G', ARRAY['Trailers', 'Deleted Scenes']),
(3, 'ADAPTATION HOLES', 'A Astounding Reflection of a Lumberjack And a Car who must Sink a Lumberjack in A Baloon', 2006, 1, 7, 2.99, 50, 18.99, 'NC-17', ARRAY['Trailers', 'Commentaries']),
(4, 'AFFAIR PREJUDICE', 'A Fanciful Documentary of a Frisbee And a Lumberjack who must Chase a Monkey in A Shark Tank', 2006, 1, 5, 2.99, 117, 26.99, 'G', ARRAY['Commentaries', 'Behind the Scenes']),
(5, 'AFRICAN EGG', 'A Fast-Paced Documentary of a Pastry Chef And a Dentist who must Pursue a Forensic Psychologist in The Gulf of Mexico', 2006, 1, 6, 2.99, 130, 22.99, 'G', ARRAY['Deleted Scenes']),
(6, 'AGENT TRUMAN', 'A Intrepid Panorama of a Robot And a Boy who must Escape a Astronaut in The Sahara Desert', 2006, 1, 3, 2.99, 169, 17.99, 'PG', ARRAY['Trailers']),
(7, 'AIRPLANE SIERRA', 'A Touching Saga of a Hunter And a Butler who must Discover a Butler in A Jet Boat', 2006, 1, 6, 4.99, 62, 28.99, 'PG-13', ARRAY['Trailers', 'Deleted Scenes']),
(8, 'AIRPORT POLLOCK', 'A Epic Tale of a Moose And a Girl who must Confront a Monkey in Ancient India', 2006, 1, 6, 4.99, 54, 15.99, 'R', ARRAY['Trailers']),
(9, 'ALABAMA DEVIL', 'A Thoughtful Panorama of a Database Administrator And a Mad Scientist who must Outgun a Mad Scientist in A Volcano', 2006, 1, 3, 2.99, 114, 21.99, 'PG-13', ARRAY['Trailers', 'Deleted Scenes']),
(10, 'ALADDIN CALENDAR', 'A Action-Packed Tale of a Man And a Lumberjack who must Reach a Feminist in A Monastery', 2006, 1, 6, 4.99, 63, 24.99, 'NC-17', ARRAY['Trailers', 'Deleted Scenes']);

INSERT INTO film_actor (actor_id, film_id) VALUES
(1, 1), (1, 2), (2, 3), (3, 4), (4, 5),
(5, 6), (6, 7), (7, 8), (8, 9), (9, 10);

INSERT INTO film_category (film_id, category_id) VALUES
(1, 6), (2, 11), (3, 6), (4, 1), (5, 6),
(6, 1), (7, 5), (8, 11), (9, 1), (10, 15);

INSERT INTO customer (customer_id, store_id, first_name, last_name, email, address_id, activebool, active) VALUES
(1, 1, 'MARY', 'SMITH', 'MARY.SMITH@sakilacustomer.org', 1, true, 1),
(2, 1, 'PATRICIA', 'JOHNSON', 'PATRICIA.JOHNSON@sakilacustomer.org', 2, true, 1),
(3, 1, 'LINDA', 'WILLIAMS', 'LINDA.WILLIAMS@sakilacustomer.org', 3, true, 1),
(4, 2, 'BARBARA', 'JONES', 'BARBARA.JONES@sakilacustomer.org', 4, true, 1),
(5, 1, 'ELIZABETH', 'BROWN', 'ELIZABETH.BROWN@sakilacustomer.org', 5, true, 1),
(6, 2, 'JENNIFER', 'DAVIS', 'JENNIFER.DAVIS@sakilacustomer.org', 1, true, 1),
(7, 1, 'MARIA', 'MILLER', 'MARIA.MILLER@sakilacustomer.org', 2, true, 1),
(8, 2, 'SUSAN', 'WILSON', 'SUSAN.WILSON@sakilacustomer.org', 3, true, 1),
(9, 1, 'MARGARET', 'MOORE', 'MARGARET.MOORE@sakilacustomer.org', 4, true, 1),
(10, 2, 'DOROTHY', 'TAYLOR', 'DOROTHY.TAYLOR@sakilacustomer.org', 5, true, 1);

INSERT INTO inventory (inventory_id, film_id, store_id) VALUES
(1, 1, 1), (2, 1, 1), (3, 1, 2),
(4, 2, 1), (5, 2, 2),
(6, 3, 1), (7, 3, 2),
(8, 4, 1), (9, 5, 2), (10, 6, 1);

INSERT INTO rental (rental_id, rental_date, inventory_id, customer_id, return_date, staff_id) VALUES
(1, '2005-05-24 22:53:30', 1, 1, '2005-05-26 22:04:30', 1),
(2, '2005-05-24 22:54:33', 2, 2, '2005-05-28 19:40:33', 1),
(3, '2005-05-24 23:03:39', 3, 3, '2005-06-01 22:12:39', 1),
(4, '2005-05-24 23:04:41', 4, 4, '2005-06-03 01:43:41', 2),
(5, '2005-05-24 23:05:21', 5, 5, '2005-06-02 04:33:21', 1),
(6, '2005-05-24 23:08:07', 6, 1, '2005-05-27 01:32:07', 1),
(7, '2005-05-24 23:11:53', 7, 2, '2005-05-29 20:34:53', 2),
(8, '2005-05-24 23:31:46', 8, 3, '2005-05-27 23:33:46', 2),
(9, '2005-05-25 00:00:40', 9, 4, '2005-05-28 00:22:40', 1),
(10, '2005-05-25 00:02:21', 10, 5, '2005-05-31 22:44:21', 2);

INSERT INTO payment (payment_id, customer_id, staff_id, rental_id, amount, payment_date) VALUES
(1, 1, 1, 1, 2.99, '2005-05-25 11:30:37'),
(2, 1, 1, 6, 4.99, '2005-05-28 10:35:23'),
(3, 2, 1, 2, 0.99, '2005-05-27 13:24:00'),
(4, 2, 2, 7, 4.99, '2005-05-29 08:45:19'),
(5, 3, 1, 3, 5.99, '2005-05-30 15:10:45'),
(6, 3, 2, 8, 2.99, '2005-06-01 12:20:10'),
(7, 4, 2, 4, 7.99, '2005-06-02 18:30:22'),
(8, 4, 1, 9, 3.99, '2005-06-03 09:15:30'),
(9, 5, 1, 5, 9.99, '2005-06-04 14:05:50'),
(10, 5, 2, 10, 4.99, '2005-06-05 16:40:00');

-- Reset sequences so autoincrement starts cleanly after seed data
SELECT setval('language_language_id_seq', (SELECT MAX(language_id) FROM language));
SELECT setval('category_category_id_seq', (SELECT MAX(category_id) FROM category));
SELECT setval('actor_actor_id_seq', (SELECT MAX(actor_id) FROM actor));
SELECT setval('country_country_id_seq', (SELECT MAX(country_id) FROM country));
SELECT setval('city_city_id_seq', (SELECT MAX(city_id) FROM city));
SELECT setval('address_address_id_seq', (SELECT MAX(address_id) FROM address));
SELECT setval('store_store_id_seq', (SELECT MAX(store_id) FROM store));
SELECT setval('staff_staff_id_seq', (SELECT MAX(staff_id) FROM staff));
SELECT setval('film_film_id_seq', (SELECT MAX(film_id) FROM film));
SELECT setval('customer_customer_id_seq', (SELECT MAX(customer_id) FROM customer));
SELECT setval('inventory_inventory_id_seq', (SELECT MAX(inventory_id) FROM inventory));
SELECT setval('rental_rental_id_seq', (SELECT MAX(rental_id) FROM rental));
SELECT setval('payment_payment_id_seq', (SELECT MAX(payment_id) FROM payment));
