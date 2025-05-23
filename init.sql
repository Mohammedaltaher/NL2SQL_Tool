-- SQL initialization script for PostgreSQL database
-- This script runs when the PostgreSQL container starts for the first time

-- Create tables
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2),
    stock_quantity INTEGER DEFAULT 0,
    description TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 1,
    price DECIMAL(10,2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- Insert sample data
-- Customers
INSERT INTO customers (name, email, city, state) VALUES
('John Smith', 'john.smith@email.com', 'New York', 'NY'),
('Jane Doe', 'jane.doe@email.com', 'Los Angeles', 'CA'),
('Bob Johnson', 'bob.johnson@email.com', 'Chicago', 'IL'),
('Alice Brown', 'alice.brown@email.com', 'Houston', 'TX'),
('Charlie Wilson', 'charlie.wilson@email.com', 'Phoenix', 'AZ'),
('David Garcia', 'david.garcia@email.com', 'Philadelphia', 'PA'),
('Eva Martinez', 'eva.martinez@email.com', 'San Antonio', 'TX'),
('Frank Rodriguez', 'frank.rodriguez@email.com', 'San Diego', 'CA'),
('Grace Kim', 'grace.kim@email.com', 'Dallas', 'TX'),
('Henry Nguyen', 'henry.nguyen@email.com', 'San Jose', 'CA')
ON CONFLICT (email) DO NOTHING;

-- Products
INSERT INTO products (name, category, price, stock_quantity, description) VALUES
('Laptop', 'Electronics', 999.99, 50, 'High-performance laptop'),
('Smartphone', 'Electronics', 599.99, 100, 'Latest smartphone model'),
('Coffee Mug', 'Kitchen', 12.99, 200, 'Ceramic coffee mug'),
('Desk Chair', 'Furniture', 249.99, 25, 'Ergonomic office chair'),
('Book', 'Education', 19.99, 75, 'Programming guide'),
('Headphones', 'Electronics', 149.99, 50, 'Wireless noise-cancelling headphones'),
('Water Bottle', 'Kitchen', 24.99, 150, 'Insulated stainless steel bottle'),
('Backpack', 'Accessories', 79.99, 40, 'Laptop backpack with USB charging port'),
('Fitness Tracker', 'Electronics', 89.99, 60, 'Smart fitness and health tracker'),
('Plant', 'Home', 34.99, 30, 'Indoor potted plant')
ON CONFLICT (id) DO NOTHING;

-- Orders
INSERT INTO orders (customer_id, product_name, quantity, price, order_date) VALUES
(1, 'Laptop', 1, 999.99, NOW() - INTERVAL '30 days'),
(2, 'Smartphone', 2, 599.99, NOW() - INTERVAL '25 days'),
(3, 'Coffee Mug', 3, 12.99, NOW() - INTERVAL '20 days'),
(1, 'Desk Chair', 1, 249.99, NOW() - INTERVAL '15 days'),
(4, 'Book', 2, 19.99, NOW() - INTERVAL '10 days'),
(5, 'Smartphone', 1, 599.99, NOW() - INTERVAL '5 days'),
(2, 'Coffee Mug', 5, 12.99, NOW() - INTERVAL '2 days'),
(6, 'Headphones', 1, 149.99, NOW() - INTERVAL '8 days'),
(7, 'Water Bottle', 3, 24.99, NOW() - INTERVAL '12 days'),
(8, 'Backpack', 1, 79.99, NOW() - INTERVAL '18 days'),
(9, 'Fitness Tracker', 2, 89.99, NOW() - INTERVAL '22 days'),
(10, 'Plant', 2, 34.99, NOW() - INTERVAL '7 days'),
(3, 'Laptop', 1, 999.99, NOW() - INTERVAL '3 days'),
(5, 'Headphones', 1, 149.99, NOW() - INTERVAL '1 day'),
(7, 'Book', 1, 19.99, NOW())
ON CONFLICT (id) DO NOTHING;
