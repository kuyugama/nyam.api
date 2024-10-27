from src.util.permissions_util import Permission


class UserOwn(Permission):
    update_info: str


class User(Permission):
    own: UserOwn
    update_info: str
    role_management: str
    permission_management: str


user = User()


class ContentEntry(Permission):
    publish: str
    delete: str


class Content(Permission):
    manga: ContentEntry
    manhwa: ContentEntry
    manihwa: ContentEntry
    ranobe: ContentEntry


content = Content()
