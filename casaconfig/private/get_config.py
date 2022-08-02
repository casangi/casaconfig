def get_config( expanded=False ):
    """
    Get configuration values as strings which can be logged, stored or evaluated.

    Parameters
       expanded (bool=False) - If True, return the configuration values with all path values expanded using expanduser and abspath from the os.path module.

    Returns
       list[str] - list of configuration strings
    """

    from .. import config as _config
    if expanded :
        valsObj = _config
    else:
        valsObj = _config._config_defaults

    return list( map( lambda name: f'{name} = {repr(getattr(valsObj,name))}', _config.__defaults ) )
