def get_config( default=False ):
    """
    Get configuration values as a list of strings which can be logged, stored, or evaluated.

    The default values (returned when default is True) are the configuration values after all config files have been evaluated but before the path values have been expanded using os.path.expanduser and os.path.abspath. Modules that use the command line to change config values may also not update the default values. User actions in a CASA session will also typically not change the default values.

    Parameters
       default (bool=False) - If True, return the default values.

    Returns
       list[str] - list of configuration strings
    """

    from .. import config as _config
    if not default :
        valsObj = _config
    else:
        valsObj = _config._config_defaults

    return list( map( lambda name: f'{name} = {repr(getattr(valsObj,name))}', _config.__defaults ) )
