from src.util.permissions_util import Permission, parse_schema, generate_permissions

content_variant_permission_schema = """
content-variant.*
content-variant.create
content-variant.delete
content-variant.update
volume.*
volume.create
volume.delete
volume.update
chapter.*
chapter.create
chapter.delete
chapter.update
page.*.create
page.*.update
page.*.delete
page.*.*
page.text.*
page.text.create
page.text.delete
page.text.update
page.image.*
page.image.create
page.image.delete
page.image.update
"""

team_member_permission_schema = """
team.update
team.disband
join.list
join.accept
join.reject
member.manage-roles
member.manage-permissions
member.manage-pseudonym
member.kick
"""
team_member_permission_schema += content_variant_permission_schema

permissions_schema = """
*
user.*
user.own.*
user.own.update-info
user.permission-management
user.role-management
user.update-info
content.*.publish
content.*.delete
content.*.update
content.*.*
content.manga.*
content.manga.delete
content.manga.publish
content.manga.update
content.manhwa.*
content.manhwa.delete
content.manhwa.publish
content.manhwa.update
content.manihwa.*
content.manihwa.delete
content.manihwa.publish
content.manihwa.update
content.ranobe.*
content.ranobe.delete
content.ranobe.publish
content.ranobe.update
override-author
team.create
team.verify
"""


permissions = Permission(schema=parse_schema(permissions_schema))
team_permissions = Permission(schema=parse_schema(team_member_permission_schema))


permission_registry = generate_permissions(permissions.schema).splitlines()
team_permission_registry = generate_permissions(team_permissions.schema).splitlines()
