from typing import Any
from flask import Blueprint, jsonify, request, session
import psycopg2
from helpers import (
    create_user_resource,
    get_resource,
    handle_request,
    execute_query,
    delete_resource_with_multiple_keys,
    update_resource,
    admin_required,
)
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("user", __name__)


# ============================
#         USER ROUTES
# ============================


@bp.route("/user/", methods=["POST"])
def create_user() -> Any:
    # Extracting User Details from request
    user_data = request.form
    if not user_data:
        return jsonify({"error": "Invalid JSON data"}), 400

    # Extracting individual fields
    username = user_data.get("username")
    password = user_data.get("password")
    visibility = user_data.get("visibility")
    is_admin = user_data.get("isAdmin", False)

    # Validate required fields
    missing_fields = []
    if not username:
        missing_fields.append("username")
    if not password:
        missing_fields.append("password")
    if not visibility:
        missing_fields.append("visibility")

    if missing_fields:
        return jsonify({"error": f'Missing fields: {", ".join(missing_fields)}'}), 400

    # Hashing password first for security
    hashed_pass = generate_password_hash(password, method="pbkdf2:sha256")
    user_data = {
        "username": username,
        "password": hashed_pass,
        "visibility": visibility,
        "isAdmin": is_admin,
    }

    # Create User in the Database
    response, status_code = create_user_resource("User", user_data)
    return jsonify(response), status_code



@bp.route("/login", methods=["POST"])
def login_user() -> Any:
    # Extracting User Details from Request
    user_data = request.form
    if not user_data:
        return jsonify({"error": "Invalid JSON data"}), 400

    # Extracting Individual Fields
    username = user_data.get("username")
    password = user_data.get("password")

    # Checking for Missing Fields
    missing_fields = []
    if not username:
        missing_fields.append("username")
    if not password:
        missing_fields.append("password")

    if missing_fields:
        return jsonify({"error": f'Missing fields: {", ".join(missing_fields)}'}), 400

    # Fetching User from Database
    retrieved_user = get_resource("User", username, "Username")
    if not retrieved_user:
        return jsonify({"error": "Invalid Username"}), 401

    # Password Verification
    stored_password_hash = retrieved_user.get("Password")
    if not check_password_hash(stored_password_hash, password):
        return jsonify({"error": "Invalid Password"}), 401

    # Successful Login, Create Session
    session["user_id"] = retrieved_user.get("UserID")
    session["is_admin"] = retrieved_user.get("IsAdmin")

    return jsonify({
    "message": "Successfully Logged In",
    "user_id": retrieved_user.get("UserID"),
    "is_admin": retrieved_user.get("IsAdmin")
}), 200


@bp.route("/user/<int:user_id>/update-password", methods=["PUT"])
def update_password(user_id: int) -> Any:
    # Check if user is authenticated
    if "user_id" not in session:
        return jsonify({"error": "Authentication required"}), 401

    if session["user_id"] != user_id:
        return jsonify({"error": "Unauthorized user"}), 403

    user_data = request.form
    if not user_data:
        return jsonify({"error": "Invalid JSON data"}), 400

    old_password = user_data.get("old_password")
    new_password = user_data.get("new_password")

    # Checking for Missing Fields
    if not old_password or not new_password:
        return jsonify({"error": "Both old and new passwords are required"}), 400

    # Retrieving the current user from the database
    retrieved_user = get_resource("User", user_id, "UserID")
    if not retrieved_user:
        return jsonify({"error": "User not found."}), 404

    # Verifying old password
    stored_password_hash = retrieved_user.get("Password")
    if not check_password_hash(stored_password_hash, old_password):
        return jsonify({"error": "Incorrect old password"}), 401

    # Hashing the new password and updating
    hashed_new_password = generate_password_hash(new_password, method="pbkdf2:sha256")
    update_data = {"password": hashed_new_password}
    update_result = update_resource("User", update_data, user_id, "UserID")

    if update_result:
        return jsonify({"message": "Password updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to update password"}), 500





@bp.route("/logout", methods=["POST"])
def logout() -> Any:
    # Ensure the user is logged in
    if "user_id" not in session:
        return jsonify({"error": "No active user(s) logged in."}), 400

    # Clear the session
    session.clear()
    return jsonify({"message": "Successfully logged out"}), 200


@bp.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id) -> Any:
    if user_id == "all":
        return handle_request("User", "get", [], "*", "all")
    return handle_request("User", "get", [], "UserID", user_id)


@bp.route("/user/<string:username>", methods=["GET"])
def get_user_by_username(username) -> Any:
    return handle_request("User", "get", [], "Username", username)


@bp.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id) -> Any:
    return handle_request(
        "User",
        "update",
        ["username", "visibility", "password", "isAdmin"],
        "UserID",
        user_id,
    )


@bp.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id) -> Any:
    return handle_request("User", "delete", [], "UserID", user_id)


# ============================
#     USER FRIENDS ROUTES
# ============================


@bp.route("/user_friend/", methods=["POST"])
def create_user_friend() -> Any:
    return handle_request("UserFriends", "create", ["userId", "friendUserId"], None)


@bp.route("/user_friend/<int:user_id>/<int:friend_user_id>", methods=["GET"])
def get_user_friend(user_id, friend_user_id) -> Any:
    return handle_request(
        "UserFriends", "get", [], ["UserID", "FriendUserID"], (user_id, friend_user_id)
    )


@bp.route("/user_friends/<int:user_id>", methods=["GET"])
def get_user_friends(user_id) -> Any:
    print(f"UserID from URL: {user_id}")

    query = f'SELECT u."UserID", u."Username" FROM "User" u JOIN "UserFriends" uf ON u."UserID" = uf."FriendUserID" WHERE uf."UserID" = {user_id};'
    return execute_query(query)


@bp.route("/user_friend/<int:user_id>/<int:friend_user_id>", methods=["DELETE"])
def delete_user_friend(user_id, friend_user_id) -> Any:
    return delete_resource_with_multiple_keys(
        "UserFriends", ["UserID", "FriendUserID"], (user_id, friend_user_id)
    )

@bp.route("/<int:user_id>/add_friend", methods=["POST"])
def add_friend(user_id):
    # This ended up being wack, sorry
    user_query = f'SELECT "UserID" FROM "User" WHERE "UserID" = %s'
    user_exists = execute_query(user_query, (user_id,))
    if not user_exists:
        return jsonify({"error": "User not found"}), 404

    # Extract request data
    data = request.json
    friend_username = data.get("friendUsername")
    if not friend_username:
        return jsonify({"error": "Missing friend username"}), 400

    # Get friend's UserID
    friend_query = f'SELECT "UserID" FROM "User" WHERE "Username" = %s'
    friend_result = execute_query(friend_query, (friend_username,))
    if not friend_result:
        return jsonify({"error": "Friend not found"}), 404

    friend_id = friend_result[0]["UserID"]

    # Prevent duplicate entries
    check_existing_query = '''
        SELECT * FROM "UserFriends"
        WHERE ("UserID" = %s AND "FriendUserID" = %s)
           OR ("UserID" = %s AND "FriendUserID" = %s)
    '''
    existing_result = execute_query(check_existing_query, (user_id, friend_id, friend_id, user_id))
    if existing_result:
        return jsonify({"error": "Friendship already exists"}), 409

    # Add friendship in both directions
    insert_query = '''
        INSERT INTO "UserFriends" ("UserID", "FriendUserID")
        VALUES (%s, %s), (%s, %s)
    '''
    execute_query(insert_query, (user_id, friend_id, friend_id, user_id))

    return jsonify({"message": "Friend added successfully"}), 200