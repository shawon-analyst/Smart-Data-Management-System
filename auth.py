"""
auth.py — Authentication helpers: login, signup, logout, persistent session via cookie.
Uses extra_streamlit_components.CookieManager so that login survives a page refresh
or the browser being closed and reopened (within the session validity window).
"""

import streamlit as st
import extra_streamlit_components as stx
import db
import os
from dotenv import load_dotenv

load_dotenv()

COOKIE_NAME = "sdms_auth_token"

ADMIN_USERNAME = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS")


def get_cookie_manager():
    if "cookie_manager" not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager(key="sdms_cookie_mgr")
    return st.session_state.cookie_manager


def _set_login_state(user: dict, token: str | None = None):
    st.session_state.logged_in = True
    st.session_state.user = user
    st.session_state.is_admin = user.get("role") == "admin"
    if token:
        st.session_state.auth_token = token


def _clear_login_state():
    for key in ["logged_in", "user", "is_admin", "auth_token"]:
        st.session_state.pop(key, None)


def try_restore_session():
    if st.session_state.get("logged_in"):
        return

    cm = get_cookie_manager()
    token = cm.get(COOKIE_NAME)
    if not token:
        return

    if token == "ADMIN_SESSION":
        _set_login_state({"id": 0, "username": ADMIN_USERNAME, "role": "admin", "full_name": "Administrator"}, token)
        return

    user = db.get_user_by_session(token)
    if user:
        _set_login_state(user, token)


def login(username: str, password: str, remember: bool = True) -> tuple[bool, str]:
    if username.strip() == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        _set_login_state({"id": 0, "username": ADMIN_USERNAME, "role": "admin", "full_name": "Administrator"}, "ADMIN_SESSION")
        if remember:
            cm = get_cookie_manager()
            cm.set(COOKIE_NAME, "ADMIN_SESSION", key="set_admin_cookie")
        db.log_activity(None, ADMIN_USERNAME, "login", "Admin logged in")
        return True, "Login successful!"

    user = db.verify_user(username, password)
    if user is None:
        return False, "Invalid username or password."

    token = db.create_session(user["id"])
    _set_login_state(user, token)
    if remember:
        cm = get_cookie_manager()
        cm.set(COOKIE_NAME, token, key="set_user_cookie")
    db.log_activity(user["id"], user["username"], "login", "User logged in")
    return True, f"Welcome, {user.get('full_name') or user['username']}!"


def logout():
    token = st.session_state.get("auth_token")
    if token and token != "ADMIN_SESSION":
        db.delete_session(token)
    user = st.session_state.get("user")
    if user:
        db.log_activity(user.get("id"), user.get("username"), "logout", "User logged out")

    cm = get_cookie_manager()
    try:
        cm.delete(COOKIE_NAME, key="del_cookie")
    except KeyError:
        pass

    _clear_login_state()


def is_logged_in() -> bool:
    return bool(st.session_state.get("logged_in"))


def is_admin() -> bool:
    return bool(st.session_state.get("is_admin"))


def current_user() -> dict:
    return st.session_state.get("user", {})