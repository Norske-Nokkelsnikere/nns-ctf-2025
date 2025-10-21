create table if not exists users(
    id integer primary key autoincrement,
    username text not null,
    admin integer not null default false -- thanks sqlite
) strict;
create table if not exists notifications (
    id integer primary key autoincrement,
    user_id integer references users(id),
    content text not null
)