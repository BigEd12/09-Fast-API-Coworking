from datetime import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M'

def convert_time(time: str):
    """
    Returns a datetime object
    
    Args:
        time (str): The time in string format to be converted. 
        
    Returns:
        datetime: A Datetime object   
    """
    
    return datetime.strptime(time.split('T')[0] + ' ' + time.split('T')[1][:-1], DATE_FORMAT)
    