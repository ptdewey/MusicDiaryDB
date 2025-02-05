-- User table
CREATE TABLE "User" (
    "UserID" SERIAL PRIMARY KEY,
    "Username" VARCHAR(255) NOT NULL UNIQUE,
    "Visibility" VARCHAR(255) NOT NULL,
    "Password" VARCHAR(255) NOT NULL,
    "IsAdmin" boolean DEFAULT FALSE
);

-- Artist table
CREATE TABLE "Artist" (
    "ArtistID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255) NOT NULL UNIQUE
);

-- StreamingPlatform table
CREATE TABLE "StreamingPlatform" (
    "StreamingPlatformID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255) NOT NULL UNIQUE
);

-- Album table
CREATE TABLE "Album" (
    "AlbumID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255) NOT NULL,
    "ArtistID" INT NOT NULL,
    FOREIGN KEY ("ArtistID") REFERENCES "Artist" ("ArtistID") ON DELETE CASCADE,
    CONSTRAINT unique_album_artist UNIQUE ("ArtistID", "Name")
);

-- Song table
CREATE TABLE "Song" (
    "SongID" SERIAL PRIMARY KEY,
    "Name" TEXT NOT NULL,
    "AlbumID" INT,
    FOREIGN KEY ("AlbumID") REFERENCES "Album" ("AlbumID") ON DELETE CASCADE,
    CONSTRAINT unique_song_album UNIQUE ("AlbumID", "Name")
);


-- DiaryEntry table
CREATE TABLE "DiaryEntry" (
    "EntryID" SERIAL PRIMARY KEY,
    "Date" DATE NOT NULL,
    "Description" TEXT,
    "Visibility" VARCHAR(255) NOT NULL,
    "UserID" INT NOT NULL,
    "SongID" INT NOT NULL,
    FOREIGN KEY ("UserID") REFERENCES "User" ("UserID") ON DELETE CASCADE,
    FOREIGN KEY ("SongID") REFERENCES "Song" ("SongID") ON DELETE CASCADE,
    CONSTRAINT unique_user_song UNIQUE ("UserID", "SongID")
);

-- DiaryReport table
CREATE TABLE "DiaryReport" (
    "ReportID" SERIAL PRIMARY KEY,
    "Date" DATE NOT NULL,
    "Visibility" VARCHAR(255) NOT NULL,
    "Description" TEXT,
    "UserID" INT NOT NULL,
    FOREIGN KEY ("UserID") REFERENCES "User" ("UserID") ON DELETE SET NULL
);

-- Review table
CREATE TABLE "Review" (
    "ReviewID" SERIAL PRIMARY KEY,
    "Contents" TEXT,
    "Visibility" VARCHAR(255) NOT NULL,
    "SongID" INT NOT NULL,
    "UserID" INT NOT NULL,
    FOREIGN KEY ("SongID") REFERENCES "Song" ("SongID") ON DELETE CASCADE,
    FOREIGN KEY ("UserID") REFERENCES "User" ("UserID") ON DELETE CASCADE
);

-- ReportEntries table
CREATE TABLE "ReportEntries" (
    "ReportID" INT NOT NULL,
    "EntryID" INT NOT NULL,
    PRIMARY KEY ("ReportID", "EntryID"),
    FOREIGN KEY ("ReportID") REFERENCES "DiaryReport" ("ReportID") ON DELETE CASCADE,
    FOREIGN KEY ("EntryID") REFERENCES "DiaryEntry" ("EntryID") ON DELETE CASCADE
);

-- UserFriends table (fixed comma issue)
CREATE TABLE "UserFriends" (
    "UserID" INT NOT NULL,
    "FriendUserID" INT NOT NULL,
    PRIMARY KEY ("UserID", "FriendUserID"),
    FOREIGN KEY ("UserID") REFERENCES "User" ("UserID") ON DELETE CASCADE,
    FOREIGN KEY ("FriendUserID") REFERENCES "User" ("UserID") ON DELETE CASCADE
);

-- StreamingPlatformSongs table
CREATE TABLE "StreamingPlatformSongs" (
    "StreamingPlatformID" INT NOT NULL,
    "SongID" INT NOT NULL,
    PRIMARY KEY ("StreamingPlatformID", "SongID"),
    FOREIGN KEY ("StreamingPlatformID") REFERENCES "StreamingPlatform" ("StreamingPlatformID") ON DELETE CASCADE,
    FOREIGN KEY ("SongID") REFERENCES "Song" ("SongID") ON DELETE CASCADE
);
