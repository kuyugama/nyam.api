from src.util.permissions_util import Permission


class _UserOwn(Permission):
    update_info: str


class _User(Permission):
    own: _UserOwn
    update_info: str
    role_management: str
    permission_management: str


user = _User()


class _ContentEntry(Permission):
    publish: str
    delete: str
    update: str


class _Content(Permission):
    manga: _ContentEntry
    manhwa: _ContentEntry
    manihwa: _ContentEntry
    ranobe: _ContentEntry


content = _Content()


class _ContentVariant(Permission):
    create: str
    delete: str
    update: str


content_variant = _ContentVariant()


class _Volume(Permission):
    create: str
    delete: str
    update: str


volume = _Volume()


class _Chapter(Permission):
    create: str
    delete: str
    update: str


chapter = _Chapter()


class _Page(Permission):
    create: str
    delete: str
    update: str


page_text = _Page("page-text")
page_image = _Page("page-image")

override_author = Permission("override-author")
