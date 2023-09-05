DO $$ BEGIN
  CREATE EXTENSION IF NOT EXISTS "pg_trgm";
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_tables WHERE tablename='documents') THEN
    CREATE TABLE documents (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      date DATE NOT NULL,
      pdf_data BYTEA NOT NULL
    );
  END IF;

  IF NOT EXISTS (SELECT FROM pg_catalog.pg_tables WHERE tablename='embeddings') THEN
    CREATE TABLE embeddings (
      id SERIAL PRIMARY KEY,
      document_id INTEGER REFERENCES documents(id),
      text_embedding TEXT NOT NULL
    );
  END IF;

  IF NOT EXISTS (SELECT FROM pg_catalog.pg_tables WHERE tablename='users') THEN
    CREATE TABLE users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(255) UNIQUE NOT NULL,
      email VARCHAR(255) UNIQUE NOT NULL,
      hashed_password VARCHAR(255) NOT NULL
    );
  END IF;
END $$;

