from src import permissions as module
from src.util.permissions_util import generate_pyi_file
from src.permissions import permissions, team_permissions

if __name__ == "__main__":
    generate_pyi_file(
        {
            "permissions": permissions.schema,
            "team_permissions": team_permissions.schema,
        },
        module.__file__ + "i",
    )
