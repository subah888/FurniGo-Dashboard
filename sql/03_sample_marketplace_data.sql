-- SAMPLE marketplace data. These rows are made up for the demo.
-- They are NOT real customers or real sales.
-- Scenario: the February to March 2027 moving season.

INSERT INTO areas (area_id, city, neighborhood) VALUES
 (1, 'Kawagoe', 'Kasumigaseki'),
 (2, 'Kawagoe', 'Kawagoe Station'),
 (3, 'Sakado',  'Sakado Station'),
 (4, 'Fujimi',  'Tsuruse'),
 (5, 'Tokyo',   'Ikebukuro'),
 (6, 'Tokyo',   'Takadanobaba');

INSERT INTO users (user_id, university_id, display_name, user_role, verification_status, created_at) VALUES
 (1,  1, 'Mina T.',  'seller', 'verified', '2027-01-10'),
 (2,  1, 'Arif H.',  'seller', 'verified', '2027-01-12'),
 (3,  2, 'Yuki S.',  'seller', 'verified', '2027-01-15'),
 (4,  3, 'Linh N.',  'seller', 'verified', '2027-01-20'),
 (5,  5, 'Omar K.',  'seller', 'pending',  '2027-01-22'),
 (6,  1, 'Sara P.',  'both',   'verified', '2027-01-25'),
 (7,  2, 'Kenta T.', 'buyer',  'verified', '2027-02-01'),
 (8,  1, 'Rafi A.',  'buyer',  'verified', '2027-02-03'),
 (9,  1, 'Emma L.',  'buyer',  'verified', '2027-02-05'),
 (10, 3, 'Chen W.',  'buyer',  'verified', '2027-02-08'),
 (11, 4, 'Nadia R.', 'buyer',  'pending',  '2027-02-10'),
 (12, 5, 'Leo M.',   'buyer',  'verified', '2027-02-12');

INSERT INTO listings (listing_id, seller_id, category_id, title, item_condition, original_price, price,
                      pickup_area_id, delivery_available, available_from, available_until, status, created_at) VALUES
 (1,  1, 1, 'Study desk with drawers', 'good',     5000,  3500, 1, TRUE,  '2027-03-23', '2027-03-25', 'available', '2027-03-01'),
 (2,  1, 2, 'Wooden chair',            'good',     2000,  1600, 1, FALSE, '2027-03-22', '2027-03-25', 'available', '2027-03-01'),
 (3,  1, 3, 'Bookshelf, 3 levels',     'good',     2400,  2400, 1, TRUE,  '2027-03-20', '2027-03-25', 'available', '2027-03-01'),
 (4,  2, 5, 'Mini fridge 90L',         'good',     6000,  4800, 1, TRUE,  '2027-03-18', '2027-03-28', 'available', '2027-03-02'),
 (5,  2, 4, 'Rice cooker, 3 cup',      'like_new', 3000,  2500, 2, FALSE, '2027-03-15', '2027-03-28', 'sold',      '2027-03-02'),
 (6,  3, 1, 'Folding desk',            'fair',     2500,  1500, 2, FALSE, '2027-03-10', '2027-03-20', 'sold',      '2027-02-25'),
 (7,  3, 2, 'Office chair',            'good',     4000,  3000, 2, TRUE,  '2027-03-12', '2027-03-22', 'available', '2027-02-25'),
 (8,  4, 6, 'Single futon set',        'good',     5000,  4000, 3, TRUE,  '2027-03-20', '2027-03-30', 'available', '2027-03-05'),
 (9,  4, 7, 'Floor lamp',              'good',     1500,     0, 3, FALSE, '2027-03-25', '2027-03-30', 'available', '2027-03-05'),
 (10, 5, 1, 'Standing desk',           'like_new', 12000, 9000, 6, TRUE,  '2027-03-01', '2027-03-15', 'sold',      '2027-02-15'),
 (11, 5, 5, 'Washing machine 5kg',     'good',     9000,  7000, 6, TRUE,  '2027-03-05', '2027-03-18', 'sold',      '2027-02-15'),
 (12, 6, 8, 'Pots and pans set',       'good',     2000,  1200, 4, FALSE, '2027-03-14', '2027-03-24', 'sold',      '2027-03-03'),
 (13, 6, 4, 'Microwave',               'good',     4000,  3200, 4, TRUE,  '2027-03-16', '2027-03-26', 'available', '2027-03-03'),
 (14, 2, 3, 'Storage rack',            'fair',     1800,  1000, 1, FALSE, '2027-02-20', '2027-02-28', 'sold',      '2027-02-10'),
 (15, 3, 2, 'Dining chair pair',       'good',     3000,  2400, 2, FALSE, '2027-02-18', '2027-02-27', 'sold',      '2027-02-08'),
 (16, 4, 4, 'Electric kettle',         'good',     1500,   800, 3, FALSE, '2027-03-08', '2027-03-19', 'withdrawn', '2027-02-28');

INSERT INTO buyer_requests (request_id, buyer_id, category_id, max_budget, target_area_id, needed_from, needed_until, status) VALUES
 (1,  8,  1, 4000, 1, '2027-03-23', '2027-03-26', 'open'),
 (2,  8,  2, 2000, 1, '2027-03-23', '2027-03-26', 'open'),
 (3,  9,  3, 3000, 1, '2027-03-21', '2027-03-24', 'open'),
 (4,  9,  5, 5000, 1, '2027-03-24', '2027-03-30', 'open'),
 (5,  7,  2, 3500, 2, '2027-03-15', '2027-03-20', 'open'),
 (6,  10, 6, 4500, 3, '2027-03-28', '2027-04-02', 'open'),
 (7,  11, 5, 4000, 5, '2027-04-01', '2027-04-05', 'open'),
 (8,  12, 1, 5000, 6, '2027-04-01', '2027-04-07', 'open'),
 (9,  11, 4, 2000, 5, '2027-04-01', '2027-04-05', 'open'),
 (10, 7,  1, 2000, 2, '2027-03-10', '2027-03-15', 'fulfilled');

-- Save the current matches, using the matching rule in the view.
INSERT INTO matches (listing_id, request_id, match_score, created_at)
SELECT listing_id, request_id, match_score, '2027-03-06'
FROM v_listing_matches;

INSERT INTO transactions (transaction_id, listing_id, buyer_id, sale_price, status, completed_at) VALUES
 (1, 14, 8,  1000, 'completed', '2027-02-26'),
 (2, 15, 7,  2400, 'completed', '2027-02-25'),
 (3, 6,  7,  1500, 'completed', '2027-03-12'),
 (4, 10, 12, 9000, 'completed', '2027-03-10'),
 (5, 11, 12, 7000, 'completed', '2027-03-14'),
 (6, 5,  9,  2500, 'completed', '2027-03-20'),
 (7, 12, 10, 1200, 'completed', '2027-03-18'),
 (8, 16, 10,  800, 'cancelled', NULL);

INSERT INTO pickup_bookings (pickup_id, transaction_id, pickup_date, delivery_option, delivery_fee, status) VALUES
 (1, 1, '2027-02-26', 'campus_pickup',    0,   'done'),
 (2, 2, '2027-02-25', 'campus_pickup',    0,   'done'),
 (3, 3, '2027-03-12', 'campus_pickup',    0,   'done'),
 (4, 4, '2027-03-10', 'delivery_partner', 500, 'done'),
 (5, 5, '2027-03-14', 'delivery_partner', 500, 'done'),
 (6, 6, '2027-03-20', 'campus_pickup',    0,   'done'),
 (7, 7, '2027-03-18', 'delivery_partner', 500, 'done'),
 (8, 8, '2027-03-19', 'campus_pickup',    0,   'cancelled');

INSERT INTO reviews (review_id, transaction_id, rating, as_described_rating, on_time_rating, comment) VALUES
 (1, 1, 5, 5, 5, 'Quick campus pickup.'),
 (2, 2, 4, 4, 5, 'Chairs had small marks, but fair price.'),
 (3, 3, 5, 5, 4, 'Desk looked just like the photos.'),
 (4, 4, 5, 5, 5, 'Delivery came on time.'),
 (5, 5, 4, 5, 4, 'Works well. Delivery was a little late.'),
 (6, 6, 5, 5, 5, 'Almost new. Very happy.'),
 (7, 7, 4, 4, 4, 'Good set for the price.');

SELECT setval(pg_get_serial_sequence('areas', 'area_id'), 6);
SELECT setval(pg_get_serial_sequence('users', 'user_id'), 12);
SELECT setval(pg_get_serial_sequence('listings', 'listing_id'), 16);
SELECT setval(pg_get_serial_sequence('buyer_requests', 'request_id'), 10);
SELECT setval(pg_get_serial_sequence('transactions', 'transaction_id'), 8);
SELECT setval(pg_get_serial_sequence('pickup_bookings', 'pickup_id'), 8);
SELECT setval(pg_get_serial_sequence('reviews', 'review_id'), 7);
