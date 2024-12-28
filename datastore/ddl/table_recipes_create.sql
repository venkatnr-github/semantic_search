CREATE TABLE public.recipes(
    rid integer NOT NULL,
    recipe_name text,
    prep_time text,
    cook_time text,
    total_time text,
    servings integer,
    yield text,
    ingredients text,
    directions text,
    rating real,
    url text,
    cuisine_path text,
    nutrition text,
    timing text,
    img_src text,
    PRIMARY KEY (rid)
);


