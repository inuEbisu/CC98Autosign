#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional, Union

import requests


class CC98Error(Exception):
    """Base class for CC98 API related errors"""

    pass


class AuthenticationError(CC98Error):
    """Authentication related errors"""

    pass


class SignInError(CC98Error):
    """Sign-in related errors"""

    pass


class User:
    API_URL = "https://api.cc98.org/me/signin"
    LOGIN_URL = "https://openid.cc98.org/connect/token"
    CLIENT_ID = "9a1fd200-8687-44b1-4c20-08d50a96e5cd"
    CLIENT_SECRET = "8b53f727-08e2-4509-8857-e34bf92b27f2"

    def __init__(self, session: requests.Session = requests.Session()) -> None:
        self.token: Optional[str] = None
        self.session = session

    def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
    ) -> None:
        """
        Login to CC98 using username and password, or with a provided token.

        Args:
            username: Username for login
            password: Password for login
            token: Directly provided token

        Raises:
            AuthenticationError: Raised when authentication fails
        """
        # If token is provided, use it directly
        if token:
            self.token = token
            return

        # If username and password are provided, use them to login
        if username and password:
            data = {
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "grant_type": "password",
                "username": username,
                "password": password,
                "scope": "cc98-api openid offline_access",
            }

            try:
                resp = self.session.post(self.LOGIN_URL, data=data)
                resp.raise_for_status()
                self.token = resp.json()["access_token"]
            except requests.RequestException as e:
                raise AuthenticationError(f"Login failed: {str(e)}")
            return

        if not self.token:
            raise AuthenticationError("No valid authentication information provided")

    def sign_in(self) -> bool:
        """
        Perform sign-in operation.

        Returns:
            bool: Whether the sign-in was successful

        Raises:
            AuthenticationError: Raised when not logged in
            SignInError: Raised when sign-in fails
        """
        if not self.token:
            raise AuthenticationError("Please login first")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            resp = self.session.post(self.API_URL, headers=headers)
            if resp.status_code == 200:
                return True
            elif resp.text == "has_signed_in_today":
                return False
            else:
                resp.raise_for_status()
                return True
        except requests.RequestException as e:
            raise SignInError(e)

    def get_sign_info(self) -> Union[Dict[str, Any], Any]:
        """
        Get sign-in information.

        Returns:
            Union[Dict[str, Any], Any]: Sign-in information (if any) containing
                lastSignInTime (str), lastReward (int), lastSignInCount (int),
                and hasSignedInToday (bool)

        Raises:
            AuthenticationError: Raised when not logged in
            SignInError: Raised when getting information fails
        """
        if not self.token:
            raise AuthenticationError("Please login first")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            resp = self.session.get(self.API_URL, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise SignInError(e)
