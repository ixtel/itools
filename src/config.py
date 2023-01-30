from .configure_default import ConfigDefault
from .configure_init import init_config_app

__all__ = ('ConfigBase', 'CONF', 'log')


class ConfigBase:
	APP_NAME = 'iTools'
	LOGER_SAVE = False
	LOGER_STACK = True


CONF, log = init_config_app(
	None,
	[ConfigDefault, ConfigBase]
)
