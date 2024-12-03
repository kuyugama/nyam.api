from src import permissions as module
from src.permissions import permissions
from src.util.permissions_util import generate_pyi_file

if __name__ == "__main__":
    generate_pyi_file(permissions.schema, module.__file__ + "i")
