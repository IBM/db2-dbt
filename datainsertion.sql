set catalog "sampledb";
set schema "sampleschema";

CREATE TABLE customers (
    id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50)
);

INSERT INTO customers (id, first_name, last_name)
SELECT 1, 'John', 'Doe' UNION
SELECT 2, 'Jane', 'Smith' UNION
SELECT 3, 'Emily', 'Johnson' UNION
SELECT 4, 'Michael', 'Brown' UNION
SELECT 5, 'Olivia', 'Williams' UNION
SELECT 6, 'Chris', 'Martin' UNION
SELECT 7, 'Alex', 'Taylor' UNION
SELECT 8, 'Jordan', 'Lee' UNION
SELECT 9, 'Morgan', 'King' UNION
SELECT 10, 'Taylor', 'Wright' UNION
SELECT 11, 'Avery', 'Harris' UNION
SELECT 12, 'Casey', 'Lewis' UNION
SELECT 13, 'Riley', 'Walker' UNION
SELECT 14, 'Cameron', 'Adams' UNION
SELECT 15, 'Jamie', 'Scott' UNION
SELECT 16, 'Bailey', 'Nelson' UNION
SELECT 17, 'Parker', 'Hill' UNION
SELECT 18, 'Quinn', 'Baker' UNION
SELECT 19, 'Sydney', 'Carter' UNION
SELECT 20, 'Rowan', 'Mitchell';


CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    order_date DATE,
    status VARCHAR(20)
);

INSERT INTO orders (id, user_id, order_date, status)
SELECT 1, 1, '2024-01-15', 'Completed' UNION
SELECT 2, 2, '2024-01-16', 'Pending' UNION
SELECT 3, 3, '2024-01-17', 'Completed' UNION
SELECT 4, 4, '2024-01-18', 'Cancelled' UNION
SELECT 5, 5, '2024-01-19', 'Completed' UNION
SELECT 6, 1, '2024-02-01', 'Shipped' UNION
SELECT 7, 2, '2024-02-05', 'Completed' UNION
SELECT 8, 3, '2024-02-10', 'Pending' UNION
SELECT 9, 4, '2024-02-15', 'Completed' UNION
SELECT 10, 5, '2024-02-20', 'Shipped' UNION
SELECT 11, 1, '2024-03-01', 'Completed' UNION
SELECT 12, 2, '2024-03-05', 'Pending' UNION
SELECT 13, 3, '2024-03-10', 'Completed' UNION
SELECT 14, 4, '2024-03-15', 'Cancelled' UNION
SELECT 15, 5, '2024-03-20', 'Completed' UNION
SELECT 16, 1, '2024-04-01', 'Shipped' UNION
SELECT 17, 2, '2024-04-05', 'Completed' UNION
SELECT 18, 3, '2024-04-10', 'Pending' UNION
SELECT 19, 4, '2024-04-15', 'Completed' UNION
SELECT 20, 5, '2024-04-20', 'Shipped';



CREATE TABLE payments (
    id INT PRIMARY KEY,
    order_id INT,
    payment_method varchar(20),
    amount INT
);

-- Insert data into the payments table with descriptive payment_method values
INSERT INTO payments (id, order_id, payment_method, amount)
SELECT 1, 1, 'credit_card', 200 UNION
SELECT 2, 2, 'coupon', 150 UNION
SELECT 3, 3, 'credit_card', 300 UNION
SELECT 4, 4, 'bank_transfer', 120 UNION
SELECT 5, 5, 'coupon', 180 UNION
SELECT 6, 6, 'credit_card', 250 UNION
SELECT 7, 7, 'coupon', 140 UNION
SELECT 8, 8, 'bank_transfer', 220 UNION
SELECT 9, 9, 'credit_card', 310 UNION
SELECT 10, 10, 'coupon', 190 UNION
SELECT 11, 11, 'bank_transfer', 200 UNION
SELECT 12, 12, 'credit_card', 240 UNION
SELECT 13, 13, 'coupon', 160 UNION
SELECT 14, 14, 'bank_transfer', 130 UNION
SELECT 15, 15, 'credit_card', 270 UNION
SELECT 16, 16, 'coupon', 210 UNION
SELECT 17, 17, 'bank_transfer', 180 UNION
SELECT 18, 18, 'credit_card', 320 UNION
SELECT 19, 19, 'coupon', 250 UNION
SELECT 20, 20, 'bank_transfer', 190;
