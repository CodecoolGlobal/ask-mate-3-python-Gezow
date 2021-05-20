DROP TABLE IF EXISTS public.profile;
create table users
(
    id         serial not null
        constraint users_pk
            primary key,
    email      text   not null,
    password   text   not null,
    username   text   not null,
    reputation integer,
    image      text
);

 INSERT INTO profile (email, password, username, reputation, image) VALUES('example@user.co.uk',
                                                                         'XYZ',
                                                                         'big_daddy',
                                                                         0,
                                                                         '0.jpg');