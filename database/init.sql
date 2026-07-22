CREATE DATABASE IF NOT EXISTS flashcards_db;
USE flashcards_db;

CREATE TABLE IF NOT EXISTS flashcards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    repetitions INT DEFAULT 0,
    ease_factor FLOAT DEFAULT 2.5,
    interval_days INT DEFAULT 1,
    next_review_date DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS review_log (
    review_date DATE PRIMARY KEY
);

-- Sample seed data so the app isn't empty on first run
INSERT INTO flashcards (question, answer, category, repetitions, ease_factor, interval_days, next_review_date)
VALUES
('What is Docker?', 'A platform to build, ship, and run applications inside lightweight containers.', 'DevOps', 0, 2.5, 1, NOW()),
('What does CI/CD stand for?', 'Continuous Integration and Continuous Deployment/Delivery.', 'DevOps', 0, 2.5, 1, NOW()),
('What is the capital of France?', 'Paris', 'Geography', 0, 2.5, 1, NOW());
