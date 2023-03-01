drop database if exists photoshare;
create database if not exists photoshare;
use photoshare;
drop table if exists registeredUser cascade;
drop table if exists albums cascade;
drop table if exists photo_in_album cascade;
drop table if exists comments cascade;
drop table if exists tags cascade;

create table registeredUser(
userID int not null auto_increment,
fName varchar(20) not null,
lName varchar(20) not null,
fullName varchar(40) not null,
email varchar(255) UNIQUE,
password varchar(255),
gender char(6),
DOB DATE,
hometown varchar(20),
contributionScore int default 0,
primary key(userID)
);



create table albums(
albumName char(20),
DOC datetime default current_timestamp,
albumID int not null auto_increment,
ownerID int,
primary key (albumID),
foreign key (ownerID) references registeredUser(userID)
);

create table album_belongs_to(
userID int,
albumID int,
primary key(userID, albumID),
foreign key (userID) references registeredUser(userID),
foreign key (albumID) references albums(albumID)
);

create table friendship(
userID int,
friendID int,
check(userID <> friendID),
primary key(userID, friendID),
foreign key(userID) references registeredUser(userID),
foreign key(friendID) references registeredUser(userID)
);
 
 create table photo_in_album(
 pID int auto_increment not null,
 albumID int,
 caption text,
 photoBinary blob,
 userID int,
 likes INTEGER default 0,
 primary key(pID),
 foreign key (userID) references registeredUser(userID),
  foreign key (albumID) references albums(albumID) on delete Cascade
 );
 
 create table comments(
 commentID int not null auto_increment,
 contents text not null,
 commentOwner varchar(40),
 commentDate datetime default current_timestamp,
 primary key(commentID)
 );
 
 create table comment_under_photo(
 commentID int,
 pID int ,
 primary key(pID, commentID),
 foreign key (pID) references photo_in_album(pID) on delete cascade,
 foreign key (commentID) references comments(commentID)
 );
 
 create table tags(
tagTitle varchar(20) not null,
primary key(tagTitle)
 );
 
 create table hasTag(
pID int,
tagTitle varchar(20) not null,
primary key (pID, tagTitle),
foreign key (pID) references photo_in_album(pID) on delete cascade,
foreign key (tagTitle) references tags(tagTitle)
 );
 
 create table likesPhoto(
pID int,
userID int,
primary key(pID, userID),
foreign key(pID) references photo_in_album(pID) on delete cascade,
foreign key(userID) references registeredUser(userID)
);

create table userUploadPhoto(
pID int,
userID int,
primary key(pID, userID),
foreign key(pID) references photo_in_album(pID) on delete cascade,
foreign key(userID) references registeredUser(userID)
);

create table userLeftComment(
userID int,
commentID int,
primary key (userID, commentID),
foreign key (userID) references registeredUser(userID),
foreign key (commentID) references comments(commentID)
);

delimiter $$
CREATE TRIGGER Comment_Constraint_Trigger
BEFORE INSERT ON Comments
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM comments C, registeredUser U where (U.fullName = C.commentOwner)) then
	signal sqlstate '45000' set message_text = 'user cannot comment under own photo';
    end if;
end $$

delimiter ;    
