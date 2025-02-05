from flask import Blueprint, jsonify
from helpers import execute_query

bp = Blueprint("aggregate", __name__)

# ============================
#  AGGREGATE REPORT ROUTES
# ============================


@bp.route("/report/total_users", methods=["GET"])
def total_users_reports():
    query = 'SELECT COUNT(*) AS total_users FROM "User";'
    result = execute_query(query, fetch_one=True)
    return jsonify(result)


@bp.route("/report/avg_num_entries", methods=["GET"])
def avg_num_entries_report():
    query = """
    SELECT AVG(entry_count) AS avg_entries_per_user
    FROM (
        SELECT COUNT(*) AS entry_count
        FROM "DiaryEntry"
        GROUP BY "UserID"
    ) AS user_entries;
    """
    result = execute_query(query, fetch_one=True)
    return jsonify(result)


@bp.route("/report/reviews_per_song", methods=["GET"])
def reviews_per_song_report():
    query = """
    SELECT \"SongID\", COUNT(*) AS total_reviews, AVG(CASE WHEN \"Visibility\" = 'public' THEN 1 ELSE 0 END) AS avg_rating
    FROM \"Review\"
    GROUP BY \"SongID\";
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/entries_by_date", methods=["GET"])
def entries_by_date_report():
    query = """
    SELECT "Date", COUNT(*) AS entry_count
    FROM "DiaryEntry"
    GROUP BY "Date"
    ORDER BY "Date";
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/friend_counts", methods=["GET"])
def friend_counts_report():
    query = """
    SELECT "UserID", COUNT("FriendUserID") AS friend_count
    FROM "UserFriends"
    GROUP BY "UserID"
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/visibilty_count_entries", methods=["GET"])
def visibility_count_entries_report():
    query = """
    SELECT "Visibility", COUNT(*) AS count
    FROM "DiaryEntry"
    GROUP BY "Visibility";
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/avg_rating_per_song", methods=["GET"])
def avg_rating_per_song_report():
    query = """
    SELECT "SongID", AVG(CASE WHEN "Visibility" = 'public' THEN 1 ELSE 0 END) AS avg_rating
    FROM "Review"
    GROUP BY "SongID"
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/most_reviewed_songs", methods=["GET"])
def most_reviewed_songs_report():
    query = """
    SELECT "SongID", COUNT(*) AS review_count
    FROM "Review"
    GROUP BY "SongID"
    ORDER BY review_count DESC
    LIMIT 5;
    """
    result = execute_query(query)
    return jsonify(result)


# ============================
#  AGGREGATE REPORT ROUTES
#  WITH SUBQUERIES AND JOINS
# ============================


@bp.route("/report/songs_released_by_artist", methods=["GET"])
def songs_released_by_artist_report():
    query = """
    SELECT a."ArtistID", a."Name",
    (SELECT COUNT(*) FROM "Song" s WHERE s."AlbumID" IN
    (SELECT "AlbumID" FROM "Album" WHERE "ArtistID" = a."ArtistID")) AS total_songs
    FROM "Artist" a;
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/avg_review_score_multiple_reviews", methods=["GET"])
def avg_review_score_multiple_reviews_report():
    query = """
    SELECT "SongID", AVG("Rating") AS avg_rating
    FROM "Review"
    WHERE "SongID" IN (SELECT "SongID" FROM "Review" GROUP BY "SongID" HAVING COUNT(*) > 1)
    GROUP BY "SongID";
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/users_with_most_entries", methods=["GET"])
def users_with_most_entries_report():
    query = """
    SELECT u."UserID", u."Username", COUNT(d."EntryID") AS total_entries
    FROM "User" u
    INNER JOIN "DiaryEntry" d ON u."UserID" = d."UserID"
    GROUP BY u."UserID", u."Username"
    ORDER BY total_entries DESC;
    """
    result = execute_query(query)
    return jsonify(result)


@bp.route("/report/min_entries_per_report/<int:user_id>", methods=["GET"])
def min_entries_per_report(user_id):
    query = """
    SELECT MIN(entry_count) AS min_entries
    FROM (
        SELECT COUNT(re."EntryID") AS entry_count
        FROM "ReportEntries" re
        INNER JOIN "DiaryReport" dr ON re."ReportID" = dr."ReportID"
        WHERE dr."UserID" = %s
        GROUP BY re."ReportID"
    ) AS entry_counts;
    """
    result = execute_query(query, (user_id,), fetch_one=True)
    return jsonify(result)


@bp.route("/report/max_entries_per_report/<int:user_id>", methods=["GET"])
def max_entries_per_report(user_id):
    query = """
    SELECT MAX(entry_count) AS max_entries
    FROM (
        SELECT COUNT(re."EntryID") AS entry_count
        FROM "ReportEntries" re
        INNER JOIN "DiaryReport" dr ON re."ReportID" = dr."ReportID"
        WHERE dr."UserID" = %s
        GROUP BY re."ReportID"
    ) AS entry_counts;
    """
    result = execute_query(query, (user_id,), fetch_one=True)
    return jsonify(result)


@bp.route("/report/avg_entries_per_report/<int:user_id>", methods=["GET"])
def avg_entries_per_report(user_id):
    query = """
    SELECT AVG(entry_count) AS avg_entries
    FROM (
        SELECT COUNT(re."EntryID") AS entry_count
        FROM "ReportEntries" re
        INNER JOIN "DiaryReport" dr ON re."ReportID" = dr."ReportID"
        WHERE dr."UserID" = %s
        GROUP BY re."ReportID"
    ) AS entry_counts;
    """
    result = execute_query(query, (user_id,), fetch_one=True)
    return jsonify(result)

@bp.route("/report/total_entries_and_reports/<int:user_id>", methods=["GET"])
def total_entries_and_reports(user_id):
    query = """
    SELECT 
        SUM(CASE WHEN "UserID" = %s THEN 1 ELSE 0 END) AS total_entries_reports
    FROM (
        SELECT "UserID" FROM "DiaryEntry"
        UNION ALL
        SELECT "UserID" FROM "DiaryReport"
    ) AS combined_entries_reports
    WHERE "UserID" = %s;
    """
    result = execute_query(query, (user_id, user_id), fetch_one=True)
    return jsonify(result)


# ============================
#  GRAPH FUNCTIONALITY ROUTES
# ============================


@bp.route("/report/user_count_by_visibility", methods=["GET"])
def user_count_by_visibility_report():
    query = """
    SELECT "Visibility", COUNT(DISTINCT "UserID") AS user_count
    FROM "User"
    GROUP BY "Visibility";
    """
    result = execute_query(query)
    print(result)
    return jsonify(result)
