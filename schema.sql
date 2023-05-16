CREATE TABLE "gender"(
    "gender_id" INTEGER NOT NULL,
    "name" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "gender" ADD PRIMARY KEY("gender_id");
CREATE TABLE "owner_role_link"(
    "owner_id" INTEGER NOT NULL,
    "job_role_id" INTEGER NOT NULL
);
CREATE TABLE "job_role"(
    "job_role_id" INTEGER NOT NULL,
    "name" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "job_role" ADD PRIMARY KEY("job_role_id");
CREATE TABLE "country"(
    "country_id" INTEGER NOT NULL,
    "code" VARCHAR(255) NOT NULL,
    "continent_id" INTEGER NOT NULL
);
ALTER TABLE
    "country" ADD PRIMARY KEY("country_id");
CREATE TABLE "continent"(
    "continent_id" INTEGER NOT NULL,
    "code" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "continent" ADD PRIMARY KEY("continent_id");
CREATE TABLE "airport"(
    "airport_id" INTEGER NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "iata" VARCHAR(255) NOT NULL,
    "lat" DOUBLE PRECISION NOT NULL,
    "lon" DOUBLE PRECISION NOT NULL,
    "country_id" INTEGER NOT NULL
);
ALTER TABLE
    "airport" ADD PRIMARY KEY("airport_id");
CREATE TABLE "flights"(
    "flight_id" INTEGER NOT NULL,
    "flight_number" VARCHAR(255) NOT NULL,
    "dep_airport_id" INTEGER NOT NULL,
    "arr_airport_id" INTEGER NOT NULL,
    "dep_time" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "arr_time" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "aircraft_id" INTEGER NOT NULL
);
ALTER TABLE
    "flights" ADD PRIMARY KEY("flight_id");
CREATE TABLE "aircraft"(
    "aircraft_id" INTEGER NOT NULL,
    "model_id" INTEGER NOT NULL,
    "owner_id" INTEGER NOT NULL
);
ALTER TABLE
    "aircraft" ADD PRIMARY KEY("aircraft_id");
CREATE TABLE "owner"(
    "owner_id" INTEGER NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "gender_id" INTEGER NOT NULL,
    "est_net_worth" INTEGER NOT NULL,
    "birthdate" DATE NOT NULL
);
ALTER TABLE
    "owner" ADD PRIMARY KEY("owner_id");
CREATE TABLE "model"(
    "model_id" INTEGER NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "capacity" INTEGER NOT NULL,
    "fuel_efficiency" DOUBLE PRECISION NOT NULL
);
ALTER TABLE
    "model" ADD PRIMARY KEY("model_id");
ALTER TABLE
    "owner_role_link" ADD CONSTRAINT "owner_role_link_owner_id_foreign" FOREIGN KEY("owner_id") REFERENCES "owner"("owner_id");
ALTER TABLE
    "aircraft" ADD CONSTRAINT "aircraft_owner_id_foreign" FOREIGN KEY("owner_id") REFERENCES "owner"("owner_id");
ALTER TABLE
    "owner" ADD CONSTRAINT "owner_gender_id_foreign" FOREIGN KEY("gender_id") REFERENCES "gender"("gender_id");
ALTER TABLE
    "flights" ADD CONSTRAINT "flights_arr_airport_id_foreign" FOREIGN KEY("arr_airport_id") REFERENCES "airport"("airport_id");
ALTER TABLE
    "flights" ADD CONSTRAINT "flights_dep_airport_id_foreign" FOREIGN KEY("dep_airport_id") REFERENCES "airport"("airport_id");
ALTER TABLE
    "flights" ADD CONSTRAINT "flights_aircraft_id_foreign" FOREIGN KEY("aircraft_id") REFERENCES "aircraft"("aircraft_id");
ALTER TABLE
    "country" ADD CONSTRAINT "country_continent_id_foreign" FOREIGN KEY("continent_id") REFERENCES "continent"("continent_id");
ALTER TABLE
    "aircraft" ADD CONSTRAINT "aircraft_model_id_foreign" FOREIGN KEY("model_id") REFERENCES "model"("model_id");
ALTER TABLE
    "owner_role_link" ADD CONSTRAINT "owner_role_link_job_role_id_foreign" FOREIGN KEY("job_role_id") REFERENCES "job_role"("job_role_id");
ALTER TABLE
    "airport" ADD CONSTRAINT "airport_country_id_foreign" FOREIGN KEY("country_id") REFERENCES "country"("country_id");