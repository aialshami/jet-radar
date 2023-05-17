-- Drop schemas if they exist (DEVELOPMENT)
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS production CASCADE;

-- Create schemas
CREATE SCHEMA staging;
CREATE SCHEMA production;

-- Select staging schema
SET search_path TO staging;

-- Build staging schema tables
CREATE TABLE "tracked_event"(
    "event_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "time_input" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    "flight_no" VARCHAR(10) NOT NULL,
    "aircraft_reg" VARCHAR(10) NOT NULL,
    "model" VARCHAR(10) NOT NULL,
    "borometric_alt" INTEGER NOT NULL,
    "geometric_alt" INTEGER NOT NULL,
    "ground_speed" FLOAT NOT NULL,
    "true_track" FLOAT NOT NULL,
    "barometric_alt_roc" FLOAT NOT NULL,
    "emergency" TEXT NOT NULL,
    "lat" FLOAT NOT NULL,
    "lon" FLOAT NOT NULL,
    PRIMARY KEY("event_id")
   );


-- Select production schema
SET search_path TO production;

-- Build production schema tables
CREATE TABLE IF NOT EXISTS "emergency"(
    "emergency_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "type" VARCHAR(20) NOT NULL UNIQUE,
    PRIMARY KEY("emergency_id")
);

CREATE TABLE IF NOT EXISTS "gender"(
    "gender_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY("gender_id")
);

CREATE TABLE IF NOT EXISTS "owner_role_link"(
    "owner_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "job_role_id" INTEGER NOT NULL UNIQUE,
    UNIQUE ("owner_id", "job_role_id")
);

CREATE TABLE IF NOT EXISTS "job_role"(
    "job_role_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY("job_role_id")
);

CREATE TABLE IF NOT EXISTS "country"(
    "country_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "code" VARCHAR(3) NOT NULL UNIQUE,
    "name" VARCHAR (50) NOT NULL UNIQUE,
    "continent_id" INTEGER NOT NULL,
    PRIMARY KEY("country_id")
);

CREATE TABLE IF NOT EXISTS "continent"(
    "continent_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "code" VARCHAR(2) NOT NULL UNIQUE,
    "name" VARCHAR (50) NOT NULL UNIQUE,
    PRIMARY KEY("continent_id")
);

CREATE TABLE IF NOT EXISTS "airport"(
    "airport_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(100) NOT NULL,
    "iata" VARCHAR(3) NOT NULL UNIQUE,
    "lat" FLOAT NOT NULL,
    "lon" FLOAT NOT NULL,
    "country_id" INTEGER NOT NULL,
    PRIMARY KEY("airport_id")
);

CREATE TABLE IF NOT EXISTS "flight"(
    "flight_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "flight_number" VARCHAR(10) NOT NULL,
    "dep_airport_id" INTEGER NOT NULL,
    "arr_airport_id" INTEGER NOT NULL,
    "dep_time" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "arr_time" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "aircraft_id" INTEGER NOT NULL,
    "emergency_id" INTEGER NOT NULL,
    PRIMARY KEY("flight_id")
);

CREATE TABLE IF NOT EXISTS "aircraft"(
    "aircraft_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "model_id" INTEGER NOT NULL,
    "owner_id" INTEGER NOT NULL,
    UNIQUE("aircraft_id", "model_id", "owner_id"),
    PRIMARY KEY("aircraft_id")
);

CREATE TABLE IF NOT EXISTS "owner"(
    "owner_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(60) NOT NULL,
    "gender_id" INTEGER NOT NULL,
    "est_net_worth" BIGINT NOT NULL,
    "birthdate" DATE NOT NULL,
    PRIMARY KEY("owner_id")
);

CREATE TABLE IF NOT EXISTS "model"(
    "model_id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(50) NOT NULL,
    "capacity" INTEGER NOT NULL,
    "fuel_efficiency" FLOAT NOT NULL,
    PRIMARY KEY("model_id")
);

ALTER TABLE
    "owner_role_link" ADD CONSTRAINT "owner_role_link_owner_id_foreign" FOREIGN KEY("owner_id") REFERENCES "owner"("owner_id");
ALTER TABLE
    "aircraft" ADD CONSTRAINT "aircraft_owner_id_foreign" FOREIGN KEY("owner_id") REFERENCES "owner"("owner_id");
ALTER TABLE
    "owner" ADD CONSTRAINT "owner_gender_id_foreign" FOREIGN KEY("gender_id") REFERENCES "gender"("gender_id");
ALTER TABLE
    "flight" ADD CONSTRAINT "flight_arr_airport_id_foreign" FOREIGN KEY("arr_airport_id") REFERENCES "airport"("airport_id");
ALTER TABLE
    "flight" ADD CONSTRAINT "flight_dep_airport_id_foreign" FOREIGN KEY("dep_airport_id") REFERENCES "airport"("airport_id");
ALTER TABLE
    "flight" ADD CONSTRAINT "flight_aircraft_id_foreign" FOREIGN KEY("aircraft_id") REFERENCES "aircraft"("aircraft_id");
ALTER TABLE
    "flight" ADD CONSTRAINT "flight_emergency_id_foreign" FOREIGN KEY("emergency_id") REFERENCES "emergency"("emergency_id");
ALTER TABLE
    "country" ADD CONSTRAINT "country_continent_id_foreign" FOREIGN KEY("continent_id") REFERENCES "continent"("continent_id");
ALTER TABLE
    "aircraft" ADD CONSTRAINT "aircraft_model_id_foreign" FOREIGN KEY("model_id") REFERENCES "model"("model_id");
ALTER TABLE
    "owner_role_link" ADD CONSTRAINT "owner_role_link_job_role_id_foreign" FOREIGN KEY("job_role_id") REFERENCES "job_role"("job_role_id");
ALTER TABLE
    "airport" ADD CONSTRAINT "airport_country_id_foreign" FOREIGN KEY("country_id") REFERENCES "country"("country_id");
