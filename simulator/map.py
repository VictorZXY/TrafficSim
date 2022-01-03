from simulator.road import Road
import random
import numpy

class map:
    """
    Generates map

    Attributes
    ----------
    map_input: a list of roads

    """
    map_input = []
    def generatemap(self, junction_num, max_road_length = 5):
        
        road_num = junction_num*2
        flag = numpy.zeros(junction_num)

        for i in range(97,97+road_num):
            j = i-97
            name = chr(i)
            Road.name = name
            exit_tmp = j//2
            Road.exit = exit_tmp   # every junction is exit for two roads
                                   # junction number starts from 0
            if not flag[exit_tmp]:
                Road.origin = exit_tmp+1 if exit_tmp<junction_num-1 else 0
            else:
                Road.origin = exit_tmp-1 if exit_tmp>1 else junction_num-1   # two roads starts from different origins end at exit_tmp

            flag[exit_tmp] += 1
            Road.length = random.randint(1,max_road_length)

            self.map_input.append(Road)

        return self.map_input