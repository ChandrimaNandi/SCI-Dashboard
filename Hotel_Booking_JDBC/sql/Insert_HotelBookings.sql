-- Inserting data into customer_info table
INSERT INTO customer_info (customer_id, name, phone_no, email)
VALUES 
    (1, 'John Doe', '9876543210', 'john@example.com'),
    (2, 'Jane Smith', '9988776655', 'jane@example.com'),
    (3, 'Alice Sharma', '9876541230', 'alice@example.com'),
    (4, 'Michael Brown', '9876543211', 'michael@example.com'),
    (5, 'Emily Johnson', '9988776656', 'emily@example.com'),
    (6, 'David Wilson', '9876541231', 'david@example.com'),
    (7, 'Sophia Anderson', '9876543212', 'sophia@example.com'),
    (8, 'Daniel Martinez', '9988776657', 'daniel@example.com'),
    (9, 'Olivia Taylor', '9876541232', 'olivia@example.com'),
    (10, 'James Garcia', '9876543213', 'james@example.com'),
    (11, 'Linda Rodriguez', '9988776658', 'linda@example.com');

-- Inserting data into room_info table
INSERT INTO room_info (room_no, price_per_night, is_available)
VALUES 
    ('S11', 2000.00, TRUE),
    ('S12', 2500.00, TRUE),
    ('S13', 3000.00, TRUE),
    ('S14', 2200.00, FALSE),
    ('S15', 2700.00, FALSE),
    ('S16', 3200.00, TRUE),
    ('S17', 3200.00, TRUE),
    ('S18', 3500.00, TRUE),
    ('S19', 4000.00, TRUE),
    ('S20', 4500.00, TRUE),
    ('D21', 3000.00, FALSE),
    ('D22', 3500.00, TRUE),
    ('D23', 4000.00, FALSE),
    ('D24', 4200.00, FALSE),
    ('D25', 4500.00, FALSE),
    ('D26', 5000.00, TRUE),
    ('D27', 5000.00, TRUE),
    ('D28', 5500.00, TRUE),
    ('D29', 6000.00, TRUE),
    ('D30', 6500.00, TRUE);

-- Inserting data into booking_info table
INSERT INTO booking_info (booking_id, checkin_date, checkout_date, room_no)
VALUES 
    (101, '2024-06-01', '2024-06-05', 'S11'),
    (104, '2024-07-20', '2024-07-25', 'S14'),
    (105, '2024-08-01', '2024-08-05', 'S15'),
    (106, '2024-08-15', '2024-08-20', 'S16'),
    (108, '2024-09-01', '2024-09-01', 'D21'),
    (109, '2024-09-05', '2024-09-16', 'D23'),
    (110, '2024-09-15', '2024-09-25', 'D24'),
    (111, '2024-10-06', '2024-10-06', 'D25');


-- Inserting data into booking_status table
INSERT INTO booking_status (customer_id, booking_id, paid)
VALUES 
    (1, 101, TRUE),
    (4, 104, FALSE),
    (5, 105, FALSE),
    (6, 106, TRUE),
    (8, 108, FALSE),
    (9, 109, FALSE),
    (10, 110, FALSE),
    (11, 111, FALSE);



-- Inserting data into payment_info table
INSERT INTO payment_info (payment_id, booking_id, payment_mode, amount)
VALUES 
    (1, 101, 'CreditCard', 10000.00),
    (6, 106, 'CreditCard', 19200.00); 
