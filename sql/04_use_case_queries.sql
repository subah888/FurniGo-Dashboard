-- FurniGo use-case queries.
-- Part A uses the SAMPLE marketplace data (daily business operations).
-- Part B uses the REAL survey data (20 responses).

-- =====================================================================
-- PART A: Daily business operations (sample data)
-- =====================================================================

-- A1. Match listings to one buyer request.
-- Rule: same item type, same area, price within budget, dates overlap.
SELECT l.listing_id,
       l.title,
       l.price,
       r.max_budget,
       GREATEST(l.available_from, r.needed_from) AS pickup_from,
       LEAST(l.available_until, r.needed_until)  AS pickup_until
FROM listings l
JOIN buyer_requests r ON r.category_id = l.category_id
                     AND r.target_area_id = l.pickup_area_id
WHERE r.request_id = 1
  AND l.status = 'available'
  AND r.status = 'open'
  AND l.price <= r.max_budget
  AND l.available_from <= r.needed_until
  AND l.available_until >= r.needed_from;

-- A2. Leaving-soon deals: sellers who move out within 7 days of a date.
SELECT l.title,
       u.display_name AS seller,
       un.name        AS university,
       l.original_price,
       l.price,
       ROUND(100.0 * (l.original_price - l.price) / NULLIF(l.original_price, 0)) AS discount_pct,
       l.available_until - DATE '2027-03-20' AS days_left
FROM listings l
JOIN users u         ON u.user_id = l.seller_id
JOIN universities un ON un.university_id = u.university_id
WHERE l.status = 'available'
  AND l.available_until BETWEEN DATE '2027-03-20' AND DATE '2027-03-20' + 7
ORDER BY days_left, discount_pct DESC;

-- A3. Seller ratings from reviews.
SELECT u.display_name AS seller,
       un.name        AS university,
       COUNT(rv.review_id)                   AS reviews,
       ROUND(AVG(rv.rating), 1)              AS avg_rating,
       ROUND(AVG(rv.as_described_rating), 1) AS avg_as_described,
       ROUND(AVG(rv.on_time_rating), 1)      AS avg_on_time
FROM reviews rv
JOIN transactions t  ON t.transaction_id = rv.transaction_id
JOIN listings l      ON l.listing_id = t.listing_id
JOIN users u         ON u.user_id = l.seller_id
JOIN universities un ON un.university_id = u.university_id
WHERE t.status = 'completed'
GROUP BY u.display_name, un.name
ORDER BY avg_rating DESC, reviews DESC;

-- A4. Monthly sales and FurniGo revenue (8% commission plus delivery fees).
SELECT DATE_TRUNC('month', t.completed_at)::date AS sale_month,
       COUNT(*)                                  AS completed_orders,
       SUM(t.sale_price)                         AS gross_sales_yen,
       ROUND(SUM(t.sale_price) * 0.08)           AS commission_yen,
       SUM(COALESCE(p.delivery_fee, 0))          AS delivery_fees_yen
FROM transactions t
LEFT JOIN pickup_bookings p ON p.transaction_id = t.transaction_id
WHERE t.status = 'completed'
GROUP BY 1
ORDER BY 1;

-- A5. Unmet demand: open requests with no matching listing.
SELECT c.category_name,
       a.city || ', ' || a.neighborhood AS area,
       COUNT(*)                         AS unmatched_requests
FROM buyer_requests r
JOIN categories c ON c.category_id = r.category_id
JOIN areas a      ON a.area_id = r.target_area_id
WHERE r.status = 'open'
  AND NOT EXISTS (SELECT 1 FROM v_listing_matches m WHERE m.request_id = r.request_id)
GROUP BY c.category_name, area
ORDER BY unmatched_requests DESC, c.category_name;

-- =====================================================================
-- PART B: Survey insights (real data, 20 responses)
-- =====================================================================

-- B1. Which items would students buy secondhand?
SELECT answer AS item, COUNT(*) AS students
FROM survey_answers
WHERE question_code = 'secondhand_items'
GROUP BY answer
ORDER BY students DESC, item;

-- B2. The most students would pay, by item type.
SELECT c.category_name, pb.price_band, COUNT(*) AS students
FROM survey_price_limits spl
JOIN categories c   ON c.category_id = spl.category_id
JOIN price_bands pb ON pb.price_band = spl.price_band
GROUP BY c.category_name, pb.price_band, pb.sort_order
ORDER BY c.category_name, pb.sort_order;

-- B3. Biggest frustrations with current options (Mercari, Facebook, and so on).
SELECT answer AS frustration, COUNT(*) AS students
FROM survey_answers
WHERE question_code = 'frustrations'
GROUP BY answer
ORDER BY students DESC, frustration;

-- B4. Interest in FurniGo by university.
SELECT un.name                           AS university,
       COUNT(*)                          AS responses,
       ROUND(AVG(s.interest_score), 1)   AS avg_interest,
       ROUND(AVG(s.date_match_score), 1) AS avg_date_matching
FROM survey_responses s
JOIN universities un ON un.university_id = s.university_id
GROUP BY un.name
ORDER BY responses DESC, university;

-- B5. How much would students pay for delivery?
SELECT delivery_fee_willing, COUNT(*) AS students
FROM survey_responses
GROUP BY delivery_fee_willing
ORDER BY students DESC;

-- B6. What makes students feel safe when buying from another student?
SELECT answer AS safety_feature, COUNT(*) AS students
FROM survey_answers
WHERE question_code = 'safety_features'
GROUP BY answer
ORDER BY students DESC, safety_feature;
