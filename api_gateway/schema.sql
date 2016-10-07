drop table if exists user;
create table user(
  id integer primary key autoincrement,
  access_key text not null,
  secret_key text not null
);

drop table if exists route;
create table route(
  id integer primary key autoincrement,
  path text not null,
  url text not null,
  netloc text not null,
  limits integer,
  seconds integer
);

drop table if exists user_route;
create table user_route(
  id integer primary key autoincrement,
  user_id integer,
  route_id integer,
  limits integer,
  seconds integer,
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(route_id) REFERENCES route(id)
);
