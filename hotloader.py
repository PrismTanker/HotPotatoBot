import time
from typing import Callable, Any

class Hotloader:
    """
    Class that loads and maintains a data structure from an external source.
    If enough time has elapsed between updates, reading from a hotloader will
    update cache from the external source. 
    """

    def __init__(
            self, 
            source: str, 
            update_period: int, 
            data_processor: Callable = None
            ) -> None:
        """
        Initialise a new hotloader to read data from a specified source,
        To be updated after a given interval in seconds.

        Args:
            source (str): filepath of file to read data from
            update_period (int): Threshold between data updates, in seconds.
                    If data is read from and this time has elapsed since the 
                    last read, the data cache is updated before returning.
            data_processor (Callable, optional): Processing function applied 
                    to list of String lines read on update. Defaults to None.
        """            
        
        self._source = source
        self._update_period = update_period
        self._data_processor = data_processor
        self._last_update = 0
        self._data = None

        self.update()

    def get(self) -> Any:
        """
        'Read' from data source by returning cached information. Cached
        information is updated prior to read if enough time has passed.

        Returns:
            Any: Cached information held by hotloader instance. Typing entirely
                    Depends on the processing function passed on initialisation. 
                    If no processing function is passed then the default list of 
                    Strings is provided
        """         
        if time.time() > self._last_update + self._update_period:
            self.update()
        return self._data

    def update(self) -> None:
        """Update data from source file. Data is read line by line as a list of
        Strings. This list is then passed into the given data processor function
        if provided
        """        

        #read data from source as a list of strings
        try:
            with open(self._source) as f:
                #strip newlines and trailing whitespace
                new_data = [line.rstrip() for line in f]

        except IOError as e:
            print("Error updating from file, will try again next request.")
            print("Recieved:")
            print(e)
            return

        #Process data using provided processor
        if self._data_processor:
            self._data = self._data_processor(new_data)
        else:
            self._data = new_data

        self._last_update = time.time()
        