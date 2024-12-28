CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    img TEXT,
    asin VARCHAR(20) UNIQUE NOT NULL,
    price DECIMAL(10,2),
    mrp DECIMAL(10,2),
    rating DECIMAL(2,1),
    ratingTotal INTEGER,
    discount INTEGER,
    seller VARCHAR(100),
    purl TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);