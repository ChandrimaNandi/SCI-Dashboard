-- Create Customer Info table
CREATE TABLE customer_info (
    customer_id INT PRIMARY KEY,
    name VARCHAR(255),
    phone_no VARCHAR(20),
    email VARCHAR(255)
);
-- Create Room Info table
CREATE TABLE room_info (
    room_no VARCHAR(20) PRIMARY KEY,
    price_per_night DECIMAL(10, 2),
    is_available BOOLEAN DEFAULT TRUE
);

-- Create Booking Info table
CREATE TABLE booking_info (
    booking_id INT PRIMARY KEY,
    checkin_date DATE,
    checkout_date DATE,
    room_no VARCHAR(20),
    FOREIGN KEY (room_no) REFERENCES room_info(room_no) 
);
-- Create Booking Status table
CREATE TABLE booking_status (
    customer_id INT,
    booking_id INT PRIMARY KEY,
    paid BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customer_info(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES booking_info(booking_id) ON DELETE CASCADE
);



-- Create Payment Info table
CREATE TABLE payment_info (
    payment_id INT PRIMARY KEY,
    booking_id INT,
    payment_mode VARCHAR(50),
    amount DECIMAL(10, 2),
    FOREIGN KEY (booking_id) REFERENCES booking_info(booking_id) 
);
