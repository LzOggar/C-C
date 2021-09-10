try:
    import enum
except ImportError as err:
    print(err)

class Env(enum.Enum):
    CMDS_PATH = 'settings/commands.json'
