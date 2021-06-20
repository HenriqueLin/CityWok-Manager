from flask_babel import lazy_gettext as _l

LOGIN_SUCCESS = _l("Welcome {name}, you are logged in.")
LOGIN_FAIL = _l("Please check your username/password.")
LOGIN_TITLE = _l("Login")
REQUIRE_CONFIRMATION = _l("Your e-mail hasn't been confirmed.")
REQUIRE_LOGIN = _l("Please log in to access this page.")

INVITE_TITLE = _l("Invite")
EMAIL_SENT = _l("A invite e-mail has been sent to the envitee.")
INVALID_INVITE = _l("Invite link is invalid.")

LOGOUT_SUCCESS = _l("You have been logged out.")

REGISTE_SUCCESS = _l("A confirmation e-mail has been sent to {email}.")
REGISTE_TITLE = _l("Register")
REQUIRED_LOGOUT = _l("You are already logged in.")

ALREADY_CONFIRMED = _l("Your e-mail address has already been confirmed.")
CONFIRMATION_SUCCESS = _l("Your e-mail address is now confirmed.")

INVALID_CONFIRMATION = _l("Confirmation link is invalid.")

FORGET_SUCCESS = _l("A e-mail to reset the password has been sent to {email}.")
FORGET_TITLE = _l("Forget Password")

RESET_SUCCESS = _l("Your password has been reset.")
RESET_TITLE = _l("Reset Password")
INVALID_RESET = _l("Reset link is invalid.")
