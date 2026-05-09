from datetime import datetime, timedelta
from typing import List, Tuple


def timeslice(start:datetime, end:datetime, time_window:int) -> List[Tuple[datetime, datetime]]:
    step = timedelta(hours=time_window)
    partitions = []
    current_start = start
    while current_start < end:
        current_end = current_start + step
        
        if current_end > end:
            current_end = end
        
        partitions.append((current_start, current_end))
        current_start = current_end
    
    return partitions