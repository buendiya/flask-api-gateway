drop table if exists user;
create table user(
  id integer primary key autoincrement,
  access_key text not null,
  secret_key text not null
);

drop table if exists route;
create table route(
  id integer primary key autoincrement,
  name text not null,
  url text not null,
  netloc text not null,
  limits text not null
);

drop table if exists user_route;
create table user_route(
  id integer primary key autoincrement,
  user integer,
  route integer,
  limits text not null,
  FOREIGN KEY(user) REFERENCES user(id),
  FOREIGN KEY(route) REFERENCES route(id)
);
