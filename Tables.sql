-- public.readings definition

-- Drop table

-- DROP TABLE public.readings;

CREATE TABLE public.readings (
	id serial4 NOT NULL,
	"time" timestamp NOT NULL,
	distance numeric(15, 5) NULL,
	max_temp numeric(10, 5) NULL,
	avg_temp numeric(10, 5) NULL,
	distance_roc numeric(7, 4) NULL,
	CONSTRAINT readings_pkey PRIMARY KEY (id)
);


-- public.temp_arrays definition

-- Drop table

-- DROP TABLE public.temp_arrays;

CREATE TABLE public.temp_arrays (
	row_index int4 NOT NULL,
	column_1 numeric(10, 6) NULL,
	column_2 numeric(10, 6) NULL,
	column_3 numeric(10, 6) NULL,
	column_4 numeric(10, 6) NULL,
	column_5 numeric(10, 6) NULL,
	column_6 numeric(10, 6) NULL,
	column_7 numeric(10, 6) NULL,
	column_8 numeric(10, 6) NULL,
	column_9 numeric(10, 6) NULL,
	column_10 numeric(10, 6) NULL,
	column_11 numeric(10, 6) NULL,
	column_12 numeric(10, 6) NULL,
	column_13 numeric(10, 6) NULL,
	column_14 numeric(10, 6) NULL,
	column_15 numeric(10, 6) NULL,
	column_16 numeric(10, 6) NULL,
	column_17 numeric(10, 6) NULL,
	column_18 numeric(10, 6) NULL,
	column_19 numeric(10, 6) NULL,
	column_20 numeric(10, 6) NULL,
	column_21 numeric(10, 6) NULL,
	column_22 numeric(10, 6) NULL,
	column_23 numeric(10, 6) NULL,
	column_24 numeric(10, 6) NULL,
	column_25 numeric(10, 6) NULL,
	column_26 numeric(10, 6) NULL,
	column_27 numeric(10, 6) NULL,
	column_28 numeric(10, 6) NULL,
	column_29 numeric(10, 6) NULL,
	column_30 numeric(10, 6) NULL,
	column_31 numeric(10, 6) NULL,
	column_32 numeric(10, 6) NULL,
	array_id serial4 NOT NULL,
	reading_id int4 NOT NULL,
	CONSTRAINT temp_arrays_pkey PRIMARY KEY (array_id),
	CONSTRAINT fk_reading FOREIGN KEY (reading_id) REFERENCES public.readings(id)
);
