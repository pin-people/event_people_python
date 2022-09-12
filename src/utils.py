
def adjust_name_event(name):
    """_summary_

    Args:
        name (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """    
    if not name or len(name.split('.')) < 3:
            raise ValueError("pattern argument error in event's name")

    return f'{name}.all' if  3 <= len(name.split('.')) < 4 else name