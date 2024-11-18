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
    update: str


class Content(Permission):
    manga: ContentEntry
    manhwa: ContentEntry
    manihwa: ContentEntry
    ranobe: ContentEntry


content = Content()


class ContentVariant(Permission):
    create: str
    delete: str
    update: str


content_variant = ContentVariant()


class Volume(Permission):
    create: str
    delete: str
    update: str


volume = Volume()


class Chapter(Permission):
    create: str
    delete: str
    update: str


chapter = Chapter()


class Page(Permission):
    create: str
    delete: str
    update: str


page_text = Page("page-text")
page_image = Page("page-image")

override_author = Permission("override-author")
