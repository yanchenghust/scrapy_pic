create table pics (
    id bigint AUTO_INCREMENT,
    title varchar(100) not null default '',
    extra text not null default '',
    uri varchar(100) not null,
    source_url varchar(1000) not null,
    source_url_md5 char(32) not null,
    create_time int not null,
    update_time int not null,
    status tinyint not null default 0,
    tag varchar(1000) not null default '',
    primary key (id),
    key create_time(create_time),
    unique key source_url_md5(source_url_md5)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;