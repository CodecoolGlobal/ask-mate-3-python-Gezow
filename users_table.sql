DROP TABLE IF EXISTS public.users;
CREATE TABLE IF NOT EXISTS users (
    id serial NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    username TEXT NOT NULL,
    reputation INTEGER,
    image TEXT
 );

 INSERT INTO users (email, password, username, reputation, image) VALUES('example@user.co.uk',
                                                                         'XYZ',
                                                                         'big_daddy',
                                                                         0,
                                                                         '0.jpg');