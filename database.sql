-- ============================================================
-- AI SQL Query Generator & Database Assistant
-- Database Setup Script
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS ai_sales;
USE ai_sales;

-- ============================================================
-- TABLE: customers
-- ============================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    city VARCHAR(100),
    registration_date DATE
);

-- ============================================================
-- TABLE: products
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2)
);

-- ============================================================
-- TABLE: orders
-- ============================================================
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_date DATE,
    amount DECIMAL(10,2),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

-- ============================================================
-- SAMPLE DATA: customers (30 fictional customers)
-- ============================================================
INSERT INTO customers (name, email, city, registration_date) VALUES
('Aarav Sharma', 'aarav.sharma@email.com', 'Mumbai', '2023-01-15'),
('Priya Patel', 'priya.patel@email.com', 'Delhi', '2023-02-20'),
('Rohan Gupta', 'rohan.gupta@email.com', 'Bangalore', '2023-03-10'),
('Sneha Reddy', 'sneha.reddy@email.com', 'Hyderabad', '2023-01-25'),
('Vikram Singh', 'vikram.singh@email.com', 'Mumbai', '2023-04-05'),
('Ananya Iyer', 'ananya.iyer@email.com', 'Chennai', '2023-05-12'),
('Karan Mehta', 'karan.mehta@email.com', 'Pune', '2023-02-18'),
('Divya Nair', 'divya.nair@email.com', 'Bangalore', '2023-06-22'),
('Arjun Kapoor', 'arjun.kapoor@email.com', 'Delhi', '2023-03-30'),
('Meera Joshi', 'meera.joshi@email.com', 'Mumbai', '2023-07-14'),
('Rahul Verma', 'rahul.verma@email.com', 'Kolkata', '2023-04-09'),
('Pooja Desai', 'pooja.desai@email.com', 'Ahmedabad', '2023-08-01'),
('Siddharth Rao', 'siddharth.rao@email.com', 'Hyderabad', '2023-05-27'),
('Neha Kulkarni', 'neha.kulkarni@email.com', 'Pune', '2023-09-03'),
('Amit Bhatt', 'amit.bhatt@email.com', 'Chennai', '2023-06-16'),
('Ritu Agarwal', 'ritu.agarwal@email.com', 'Jaipur', '2023-10-11'),
('Deepak Tiwari', 'deepak.tiwari@email.com', 'Lucknow', '2023-07-29'),
('Kavita Saxena', 'kavita.saxena@email.com', 'Delhi', '2023-11-05'),
('Manish Chopra', 'manish.chopra@email.com', 'Chandigarh', '2023-08-20'),
('Swati Pandey', 'swati.pandey@email.com', 'Kolkata', '2023-12-15'),
('Nikhil Mishra', 'nikhil.mishra@email.com', 'Mumbai', '2024-01-08'),
('Anjali Bose', 'anjali.bose@email.com', 'Kolkata', '2024-02-14'),
('Rajesh Kumar', 'rajesh.kumar@email.com', 'Bangalore', '2024-03-01'),
('Tanvi Shah', 'tanvi.shah@email.com', 'Ahmedabad', '2024-01-22'),
('Varun Malhotra', 'varun.malhotra@email.com', 'Delhi', '2024-04-10'),
('Shreya Ghosh', 'shreya.ghosh@email.com', 'Kolkata', '2024-02-28'),
('Pranav Jain', 'pranav.jain@email.com', 'Jaipur', '2024-05-05'),
('Ishita Bansal', 'ishita.bansal@email.com', 'Chandigarh', '2024-03-18'),
('Gaurav Sinha', 'gaurav.sinha@email.com', 'Lucknow', '2024-06-12'),
('Nandini Menon', 'nandini.menon@email.com', 'Chennai', '2024-04-25');

-- ============================================================
-- SAMPLE DATA: products (20 products across 5 categories)
-- ============================================================
INSERT INTO products (product_name, category, price) VALUES
('Wireless Mouse', 'Electronics', 599.00),
('Mechanical Keyboard', 'Electronics', 2499.00),
('USB-C Hub', 'Electronics', 1299.00),
('Bluetooth Speaker', 'Electronics', 1899.00),
('Laptop Stand', 'Accessories', 999.00),
('Phone Case', 'Accessories', 299.00),
('Screen Protector', 'Accessories', 199.00),
('Webcam HD', 'Electronics', 2199.00),
('Desk Organizer', 'Office Supplies', 449.00),
('Notebook Set', 'Office Supplies', 349.00),
('Gel Pen Pack', 'Office Supplies', 149.00),
('Wireless Charger', 'Electronics', 899.00),
('Backpack', 'Accessories', 1499.00),
('Water Bottle', 'Lifestyle', 399.00),
('Coffee Mug', 'Lifestyle', 249.00),
('Mouse Pad XL', 'Accessories', 599.00),
('Monitor Light Bar', 'Electronics', 1799.00),
('Cable Management Kit', 'Office Supplies', 349.00),
('Fitness Band', 'Lifestyle', 1999.00),
('Portable SSD 500GB', 'Electronics', 3499.00);

-- ============================================================
-- SAMPLE DATA: orders (100 orders spread across 2023-2024)
-- ============================================================
INSERT INTO orders (customer_id, product_id, quantity, order_date, amount) VALUES
-- January 2023
(1, 1, 2, '2023-01-20', 1198.00),
(2, 3, 1, '2023-01-22', 1299.00),
(1, 5, 1, '2023-01-28', 999.00),
-- February 2023
(3, 2, 1, '2023-02-05', 2499.00),
(4, 8, 1, '2023-02-10', 2199.00),
(2, 10, 3, '2023-02-15', 1047.00),
(5, 4, 1, '2023-02-22', 1899.00),
-- March 2023
(6, 12, 2, '2023-03-01', 1798.00),
(7, 6, 3, '2023-03-08', 897.00),
(3, 13, 1, '2023-03-15', 1499.00),
(8, 1, 1, '2023-03-20', 599.00),
(9, 17, 1, '2023-03-28', 1799.00),
-- April 2023
(10, 20, 1, '2023-04-02', 3499.00),
(1, 4, 2, '2023-04-10', 3798.00),
(11, 9, 2, '2023-04-15', 898.00),
(4, 14, 3, '2023-04-20', 1197.00),
(5, 2, 1, '2023-04-25', 2499.00),
-- May 2023
(12, 7, 5, '2023-05-03', 995.00),
(6, 19, 1, '2023-05-10', 1999.00),
(13, 3, 2, '2023-05-15', 2598.00),
(2, 16, 1, '2023-05-22', 599.00),
(14, 11, 4, '2023-05-28', 596.00),
-- June 2023
(15, 15, 2, '2023-06-05', 498.00),
(7, 20, 1, '2023-06-12', 3499.00),
(3, 8, 1, '2023-06-18', 2199.00),
(16, 1, 3, '2023-06-22', 1797.00),
(8, 5, 2, '2023-06-28', 1998.00),
-- July 2023
(1, 17, 1, '2023-07-05', 1799.00),
(17, 13, 1, '2023-07-10', 1499.00),
(9, 4, 1, '2023-07-15', 1899.00),
(10, 6, 2, '2023-07-20', 598.00),
(18, 12, 1, '2023-07-25', 899.00),
-- August 2023
(11, 2, 1, '2023-08-02', 2499.00),
(19, 9, 1, '2023-08-08', 449.00),
(4, 18, 2, '2023-08-12', 698.00),
(20, 3, 1, '2023-08-18', 1299.00),
(5, 14, 2, '2023-08-22', 798.00),
(12, 10, 2, '2023-08-28', 698.00),
-- September 2023
(6, 20, 1, '2023-09-03', 3499.00),
(13, 1, 2, '2023-09-10', 1198.00),
(21, 5, 1, '2023-09-15', 999.00),
(7, 15, 3, '2023-09-20', 747.00),
(14, 4, 1, '2023-09-25', 1899.00),
-- October 2023
(1, 19, 1, '2023-10-02', 1999.00),
(22, 2, 2, '2023-10-08', 4998.00),
(8, 11, 3, '2023-10-12', 447.00),
(15, 17, 1, '2023-10-18', 1799.00),
(23, 8, 1, '2023-10-22', 2199.00),
(9, 13, 1, '2023-10-28', 1499.00),
-- November 2023
(3, 16, 2, '2023-11-05', 1198.00),
(24, 7, 4, '2023-11-10', 796.00),
(10, 3, 1, '2023-11-15', 1299.00),
(16, 19, 1, '2023-11-20', 1999.00),
(25, 1, 1, '2023-11-25', 599.00),
-- December 2023
(1, 20, 1, '2023-12-02', 3499.00),
(11, 4, 2, '2023-12-08', 3798.00),
(26, 12, 1, '2023-12-12', 899.00),
(2, 2, 1, '2023-12-18', 2499.00),
(17, 5, 1, '2023-12-22', 999.00),
(4, 9, 3, '2023-12-28', 1347.00),
-- January 2024
(27, 8, 1, '2024-01-05', 2199.00),
(12, 17, 1, '2024-01-10', 1799.00),
(5, 3, 2, '2024-01-15', 2598.00),
(28, 14, 1, '2024-01-20', 399.00),
(13, 6, 3, '2024-01-25', 897.00),
-- February 2024
(6, 2, 1, '2024-02-02', 2499.00),
(29, 10, 2, '2024-02-08', 698.00),
(14, 20, 1, '2024-02-12', 3499.00),
(3, 15, 2, '2024-02-18', 498.00),
(30, 1, 2, '2024-02-22', 1198.00),
-- March 2024
(7, 19, 1, '2024-03-03', 1999.00),
(15, 13, 1, '2024-03-08', 1499.00),
(1, 11, 5, '2024-03-12', 745.00),
(21, 4, 1, '2024-03-18', 1899.00),
(8, 18, 1, '2024-03-22', 349.00),
-- April 2024
(22, 9, 2, '2024-04-02', 898.00),
(16, 2, 1, '2024-04-08', 2499.00),
(9, 7, 2, '2024-04-12', 398.00),
(23, 12, 2, '2024-04-18', 1798.00),
(10, 5, 1, '2024-04-22', 999.00),
-- May 2024
(2, 20, 1, '2024-05-03', 3499.00),
(24, 17, 1, '2024-05-08', 1799.00),
(11, 1, 3, '2024-05-12', 1797.00),
(25, 3, 1, '2024-05-18', 1299.00),
(4, 8, 1, '2024-05-22', 2199.00),
-- June 2024
(13, 16, 2, '2024-06-02', 1198.00),
(26, 4, 1, '2024-06-08', 1899.00),
(5, 15, 1, '2024-06-12', 249.00),
(27, 19, 1, '2024-06-18', 1999.00),
(14, 2, 1, '2024-06-22', 2499.00),
-- July 2024
(6, 13, 1, '2024-07-03', 1499.00),
(28, 10, 3, '2024-07-08', 1047.00),
(15, 1, 1, '2024-07-12', 599.00),
(3, 20, 1, '2024-07-18', 3499.00),
(29, 5, 2, '2024-07-22', 1998.00),
-- August 2024
(1, 6, 4, '2024-08-02', 1196.00),
(7, 9, 1, '2024-08-08', 449.00),
(16, 18, 2, '2024-08-12', 698.00),
(30, 3, 1, '2024-08-18', 1299.00),
(8, 14, 2, '2024-08-22', 798.00);
