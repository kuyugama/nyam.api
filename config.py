from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.yaml", ".secrets.yaml"],
)
