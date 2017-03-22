##############################################################################
#                                                                            #
#                                                                            #
#                 Temper_Temp_Sensor class                                   #
#                                                                            #
#                                                                            #
##############################################################################

import local_config 

class Temper_Temp_Sensor:
    def get_temp(self):
        s = subprocess.check_output(["temper-poll", "-f"])
        n = float(s) + local_config.TEMPER_CAL
        return n


