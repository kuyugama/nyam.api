from src.scheme import define_error_category

_define_error = define_error_category("teams")

not_found = _define_error("not-found", "Team not found", 404)
not_member = _define_error("not-member", "You're not a member of the team", 403)
permission_denied = _define_error(
    "permission-denied",
    "Permission denied: required permissions: {permissions}",
    403,
)
nothing_to_update = _define_error(
    "nothing-to-update", "No difference between current details and new details", 400
)

join_not_found = _define_error("join-not-found", "Join request not found", 404)

provided_not_member = _define_error(
    "provided-not-member", "Provided member not a member of the team", 400
)
role_not_found = _define_error("role-not-found", "Role not found", 404)
role_invalid = _define_error("role-invalid", "Role of invalid type specified", 400)

join_already_requested = _define_error("join-already-requested", "Join already requested", 404)

cannot_kick_highest_role = _define_error(
    "kick-highest-role", "Can't kick member with the highest role", 403
)
