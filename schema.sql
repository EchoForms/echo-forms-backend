-- schema.sql
-- SQL schema for initializing the EchoForms database

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    subscription VARCHAR(255) NOT NULL DEFAULT 'free',
    status VARCHAR(255) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New forms table
CREATE TABLE IF NOT EXISTS forms (
    id SERIAL PRIMARY KEY,
    form_unique_id VARCHAR(36) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to update 'updated_at' on row modification for users
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS set_updated_at ON users;
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for forms table
DROP TRIGGER IF EXISTS set_updated_at_forms ON forms;
CREATE TRIGGER set_updated_at_forms
BEFORE UPDATE ON forms
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column(); 

CREATE TABLE IF NOT EXISTS form_fields (
    id SERIAL PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    required BOOLEAN DEFAULT FALSE,
    form_id INTEGER NOT NULL REFERENCES forms(id) ON DELETE CASCADE,
    options JSON,
    question_number INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 