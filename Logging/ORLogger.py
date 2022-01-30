

import numpy as np
import pandas as pd
from Logging.logger import Logger



class ORLogger(Logger):
    def __init__(self, OR_simulation, **kwargs):
        super().__init__(OR_simulation, **kwargs)

        self.simulation = OR_simulation
    

    def get_dataframe(self):
        from net.sf.openrocket.simulation import FlightDataType # type: ignore

        sim = self.simulation
        
        data = []

        for t in FlightDataType.ALL_TYPES:
            data.append(sim.getSimulatedData().getBranch(0).get(t))
        
        header_names = 

        data = [list(column) for column in data if column]
        df = pd.DataFrame(data, columns=FlightDataType.ALL_TYPES)

        try:
            # Rather than using the index (0, 1, 2, 3, 4...), I will index the rows by the time the row is recorded at
            df.set_index('time', inplace=True)
        except KeyError as e:
            print("Attempted to create dataframe, but there was no time index. Likely, the simulation did not make it past one frame, and no time was ever logged.")
        
        return df
    
    def update_saved_state(self):
        # FIXME
        print("Trying to do the preset object thing but cannot.")
    
