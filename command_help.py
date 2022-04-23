###This file outputs the formatted results for the discord embeds

import search

class command_help_functions:
    def __init__(self):
        self.headers = {'User-Agent': 'Chrome/88.0.4324.150'}
        self.url = 'https://thunderskill.com/en/stat/'
    
    def general_stats_format(self, result):
        outputAB = 'Efficiency: {result15}\n\
                    Win Rate: {result0}\n\
                    KDR: {result1}\n\
                    KB: {result2}\n\
                    Lifespan: {result3}\n\
                    Total Battles: {result4}'\
                    .format(result15 = result[15], result0 = result[0],result1 = result[1], result2 = result[2], result3 = result[3], result4 = result[4])
        outputRB = 'Efficiency: {result16}\n\
                    Win Rate: {result5}\n\
                    KDR: {result6}\n\
                    KB: {result7}\n\
                    Lifespan: {result8}\n\
                    Total Battles: {result9}'\
                    .format(result16 = result[16], result5 = result[5],result6 = result[6], result7 = result[7], result8 = result[8], result9 = result[9])
        outputSB = 'Efficiency: {result17}\n\
                    Win Rate: {result10}\n\
                    KDR: {result11}\n\
                    KB: {result12}\n\
                    Lifespan: {result13}\n\
                    Total Battles: {result14}'\
                    .format(result17 = result[17], result10 = result[10],result11 = result[11], result12 = result[12], result13 = result[13], result14 = result[14])
        return outputAB, outputRB, outputSB

    def detailed_stats_format(self, result):
        output = 'Efficiency : {result11}\n\
                    Win Rate: {result2}\n\
                    KDR: {result3}\n\
                    Ground Kills/Death: {result4}\n\
                    Air Kills/Death: {result5}\n\
                    KB: {result6}\n\
                    Ground Kills/Battle: {result7}\n\
                    Air Kills/Battle: {result8}\n\
                    Lifespan: {result9}\n\
                    Total Battles: {result10}\n\
                    Air Battles: {result0}\n\
                    Ground Battles: {result1}'\
                    .format(result11 = result[11], result2 = result[2], result3 = result[3], result4 = result[4], result5 = result[5], result6 = result[6], result7 = result[7], result8 = result[8], result9 = result[9], result10 = result[10], \
                    result0 = result[0], result1 = result[1])
        return output
    
    def last_session_format(self, result):
        output = 'Win Rate: {result0}%\n\
                    Battles: {result2}\n\
                    Victories: {result3}\n\
                    Defeats: {result4}\n\
                    Air Kills: {result5}\n\
                    Ground Kills: {result6}'\
                    .format(result0 = result[0], result2 = result[2], result3 = result[3], result4 = result[4], result5 = result[5], result6 = result[6])
        return output

    def search_vehicle_format(self, result):
        output = 'Battles: {result0}\n\
                    Victories: {result1}\n\
                    Defeats: {result2}\n\
                    Deaths: {result3}\n\
                    Air Kills: {result4}\n\
                    Ground Kills: {result5} \n\
                    Air Kills/Death: {result6}\n\
                    Air Kills/Battle: {result7}\n\
                    Ground Kills/Death: {result8}\n\
                    Ground Kills/Battle: {result9}\n\
                    Winrate: {result10}%'\
                    .format(result0 = result[0], result1 = result[1], result2 = result[2], result3 = result[3], result4 = result[4], result5 = result[5], \
                    result6 = result[6], result7 = result[7], result8 = result[8], result9 = result[9], result10 = result[10])
        return output