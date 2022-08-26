### This file defines the search functions

### Imports
import re
import requests
from bs4 import BeautifulSoup

### Class definition
class search_functions:
    def __init__(self): # Self class defined
        self.headers = {'User-Agent': 'Chrome/88.0.4324.150'}
        self.url = 'https://thunderskill.com/en/stat/' # The website we are scraping
        self.airvehicles = '#type=aviation&role=all&country=all'
        self.groundvehicles = '#type=army&role=all&country=all'

    # Function to search for the general stats of a player
    def search_general_stats(self, search_name): 
        response = requests.get(str(self.url) + str(search_name)) 
        content = response.content
        soup = BeautifulSoup(content, 'html.parser') # Webscrape the page needed and use bs4 to turn it into html "soup"
        tag = soup.select('.squad_name') # Select the squadron
        if tag == []: # If there is no squadron, then there is no tag, otherwise the squadron is the tag
            clan_tag = ''
        else:
            extractor = []
            for elem in tag:
                extractor.append(elem.getText().strip()) # Gets the text from the html, then strips any unneccessary garbage that we don't need from the tag
            clan_tag = str(extractor[0])
        efficiency_values = soup.select('.kpd_value') # Select the "big" efficiency numbers at the top of the game mode stats
        scores = soup.select('.badge') # Select all the "small" numbers in each game mode
        last_update = soup.select('.stat_dt') # Selects the last update time
        extractor = [] # Empties out the extractor array
        for item in efficiency_values: # Append all the values to the extractor
            extractor.append(item.text)
        efficiency = []
        numbers = []
        for item in scores[2:]: # Except the first 2 numbers, append the scores to the numbers array
            numbers.append(item.text)
        del numbers[9:11], numbers[18:20]
        del numbers[2:4], numbers[3:5], numbers[7:9], numbers[8:10]
        del numbers[12:14], numbers[13:15] # Filtration of numbers we don't need (need to find a better way of doing this, but I could not figure out a formula for the sequences I needed deleted)
        i = 0
        j = 0
        for item in numbers: # For each number in numbers
            if i == 4 or i == 9 or i == 14: # Check the 4th, 9th, and 14 number. If they are N/A or less than 10, then don't append the overall efficiency. If not, then append
                if numbers[i] == 'N/A' or int(numbers[i]) <= 10:
                    efficiency.append('0%')
                if numbers[i] != 'N/A' and int(numbers[i]) >= 10:
                    efficiency.append(extractor[j])
                    j = j + 1
            i = i + 1
        numbers = numbers + efficiency # Combine the efficiencies and the statistics
        extractor = []
        for item in last_update:
            extractor.append(item.text) # Append the last update time
        return numbers, extractor, clan_tag # Return all of the numbers, the update time, and the squadron tag

    # Searching for more detailed stats of a player, gamemode specific
    def search_gamemode_stats(self, search_name, game_mode):
        response = requests.get(str(self.url) + str(search_name))
        content = response.content
        soup = BeautifulSoup(content, 'html.parser') # Webscrape, soup, etc
        efficiency_values = soup.select('.kpd_value')
        scores = soup.select('.badge')
        tag = soup.select('.squad_name') # Same process here as in the general search
        if tag == []:
            clan_tag = ''
        else:
            extractor = []
            for elem in tag:
                extractor.append(elem.getText().strip())
            clan_tag = str(extractor[0])
        extractor = []
        for item in efficiency_values:
            extractor.append(item.text)
        numbers = []
        k = 0
        if game_mode == 'AB': # Since we got all of the numbers regardless of gamemode, we filter the numbers we need based on their positions within the array
            for item in scores[:11]:
                numbers.append(item.text)
            if numbers[10] == 'N/A' or int(numbers[10]) <= 10: # Check if the number associated with "battles" is N/A or less than 10 and determine whether or not to append the efficiency (also associated by position in its respective array)
                numbers.append('0%')
            elif numbers[10] != 'N/A' and int(numbers[10]) >= 10:
                numbers.append(extractor[0])
                k = 1
            game_mode = '/vehicles/a' # Swap game_mode to a string for the website so we can find favorite vehicle
        if game_mode == 'RB':
            for item in scores[11:22]:
                numbers.append(item.text)
            if numbers[10] == 'N/A' or int(numbers[10]) <= 10:
                numbers.append('0%')
                k = 1
            elif numbers[10] != 'N/A' and int(numbers[10]) >= 10:
                numbers.append(extractor[1])
            game_mode = '/vehicles/r' # Swap game_mode to a string for the website so we can find favorite vehicle
        if game_mode == 'SB':
            for item in scores[22:]:
                numbers.append(item.text)
            if numbers[10] == 'N/A' or int(numbers[10]) <= 10:
                numbers.append('0%')
                k = 1
            elif numbers[10] != 'N/A' and int(numbers[10]) >= 10:
                numbers.append(extractor[2])
            game_mode = '/vehicles/s' # Swap game_mode to a string for the website so we can find favorite vehicle
        if k == 1:
            vehicle = ''
            stats = ''
            return numbers, stats, clan_tag, vehicle  #Return game mode numbers and empty stats for unplayed modes
        response = requests.get(str(self.url) + str(search_name) + str(game_mode))
        content = response.content
        soup = BeautifulSoup(content, 'html.parser') # Webscrape for soup again
        [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        text_str = soup.getText()
        lines = (line.strip() for line in text_str.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = text.split('\n')
        text = [item.replace('\xa0',' ') for item in text] # Extract all the text on the site, remove any special characters
        battleindex = []
        battlenumber = []
        for item in text:
            if (str('General statistics for') in str(item)): # Filter out to avoid duplicates
                del text[text.index(item)]
        for item in text: 
            if (str('+') in str(item)):
                split_string = item.split('+', 1)
                text[text.index(item)] = split_string[0] # Guard against numbers used to denote updates in the statistics
        for item in text: 
            if 'Battles' in item:
                if 'Battles0' not in item: # If battles is in the item, and if battles is not 0, then append the number and its index
                    battlenumber.append(re.sub("[^.0-9]","", item))
                    battleindex.append(text.index(item))
        for item in battlenumber: # Clean the indexes and the numbers from any empty items
            if item == '':
                del battleindex[battlenumber.index(item)]
                del battlenumber[battlenumber.index(item)]
        del battleindex[0:3] 
        del battlenumber[0:3] # Remove first 3 from each array because it gives numbers we do not need
        most_battles = max([int(i) for i in battlenumber]) # Find largest amount of battles
        number_index = battlenumber.index(str(most_battles)) # Find its index
        index = battleindex[number_index]
        vehicle = text[index - 1] # Decrement the index by 1 to find the vehicle associated with the largest number of battles
        extractor = []
        stats = []
        i = 0
        for item in text:
            if vehicle in item: # Find the vehicle, append its stats
                while i <= 10:
                    extractor.append(text[index + i])
                    i = i + 1
                i = 0
        i = 0
        k = 0
        while i <= 4:
            stats.append(int(re.sub("[^0-9]", "", extractor[i]))) # Append the first four stats
            i = i + 1
        for item in extractor:
            if 'Overall' in item:
                stats.append((int(re.sub("[^0-9]", "", item)))) # Find the overall air frags and overall ground frags
        if stats[-3] == 0: # If deaths is 0, then we make it 1 for the purposes of our calculations
            stats[-3] = 1
            k = 1
        del stats[1] # Delete respawn stat that we don't need
        kda = float(stats[-2]/stats[-3])
        kda = round(kda, 2)
        kba = float(stats[-2]/stats[-6])
        kba = round(kba, 2)
        kdg = float(stats[-1]/stats[-3])
        kdg = round(kdg, 2)
        kbg = float(stats[-1]/stats[-6]) # Calculate kills/deaths for air and ground
        kbg = round(kbg, 2)
        if k == 1: # Set deaths back to 0
            stats[-3] = 0
            k = 0
        winrate = float((stats[-5]/stats[-6]) * 100)
        winrate = round(winrate, 2) # Calculate winrate
        stats.append(kda), stats.append(kba), stats.append(kdg), stats.append(kbg), stats.append(winrate) # Append all the numbers we need
        return numbers, stats, clan_tag, vehicle # Return game mode numbers, vehicle stats, squadron, and the vehicle itself

    # Searching the stats of the last session the player had
    def search_session(self, search_name):
        custom_url = (str(self.url) + str(search_name) + str('/session'))
        response = requests.get(custom_url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        text_str = soup.getText()
        lines = (line.strip() for line in text_str.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = text.split('\n')
        tag = soup.select('.squad_name')
        if tag == []:
            clan_tag = ''
        else:
            extractor = []
            for elem in tag:
                extractor.append(elem.getText().strip())
            clan_tag = str(extractor[0]) #All same as before
        extractor = []
        gametype = []
        i = 0
        for item in text:
            if 'nickname' in item:
                return extractor, gametype, clan_tag, custom_url 
            if str('Arcade Battles') in str(item) or str('Realistic Battles') in str(item) or str('Simulator Battles') in str(item): #If game mode found, append the items associated by position after it
                gametype.append(item)
                while i <= 14:
                    extractor.append(re.sub("[^.0-9]","", text[text.index(item) + i]))
                    i = i + 1
                i = 0
        for item in extractor:
            if str(item) == str(''):
                del extractor[extractor.index(item)]
        for item in extractor:
            if str(item) == str(''):
                del extractor[extractor.index(item)] # Delete all empty strings, don't know why 2 are needed but it is what it is
        return extractor, gametype, clan_tag, custom_url # Return stats, gamemodes, squadron, url

    # Searching fpr the player's used vehicles in their last session
    def search_session_vehicles(self, search_name, game_mode):
        if game_mode == 'AB':
            game_mode = '/vehicles/a'
        if game_mode == 'RB':
            game_mode = '/vehicles/r'
        if game_mode == 'SB':
            game_mode = '/vehicles/s' # Set strings to the gamemode that the message sender searched for
        custom_url = (str(self.url) + str(search_name) + str(game_mode))
        response = requests.get(custom_url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        tag = soup.select('.squad_name')
        if tag == []:
            clan_tag = ''
        else:
            extractor = []
            for elem in tag:
                extractor.append(elem.getText().strip())
            clan_tag = str(extractor[0]) # All same as before
        extractor = []
        filteredtext = []
        differences = soup.select('.diff')
        for item in differences:
            if '%' in item.text:
                extractor.append(item)
        for item in extractor:
            parent1 = item.parent
            parent2 = parent1.parent
            text_str = parent2.text
            lines = (line.strip() for line in text_str.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text = text.split('\n')
            text = [item.replace('\xa0',' ') for item in text]
            filteredtext.append(text)
        for arr in filteredtext:
            del arr[0]
            i = 6
            while i < len(arr):
                if 'Overall' not in arr[i]:
                    del arr[i]
                else:
                    i = i + 1
            del arr[2]
        session_stats = []
        for arr in filteredtext:
            i = 1
            session_stats.append(arr[0])
            while i < 7:
                if '+' in arr[i]:
                    split = arr[i].split('+')
                    session_stats.append(int(split[1])) 
                else:
                    session_stats.append(0)
                i = i + 1
            winrate = float((session_stats[-5]/session_stats[-6]) * 100)
            winrate = round(winrate, 2) # Calculate winrate
            session_stats.append(winrate)
        vehicles = []
        i = 0
        while i < len(session_stats):
            if i % 8 == 0:
                vehicles.append(session_stats[i])
            i = i + 1
        for item in vehicles:
            if item in session_stats:
                session_stats.remove(item)
        return session_stats, clan_tag, vehicles, custom_url

    # Searching for the vehicle requested by the user
    def search_vehicles(self, search_name, game_mode, search_vehicle):
        if game_mode == 'AB':
            game_mode = '/vehicles/a'
        if game_mode == 'RB':
            game_mode = '/vehicles/r'
        if game_mode == 'SB':
            game_mode = '/vehicles/s' #Set strings to the gamemode that the message sender searched for
        custom_url = (str(self.url) + str(search_name) + str(game_mode))
        response = requests.get(custom_url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        text_str = soup.getText()
        lines = (line.strip() for line in text_str.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = text.split('\n')
        text = [item.replace('\xa0',' ') for item in text]
        tag = soup.select('.squad_name')
        if tag == []:
            clan_tag = ''
        else:
            extractor = []
            for elem in tag:
                extractor.append(elem.getText().strip())
            clan_tag = str(extractor[0]) #All same as before
        extractor = []
        indexes = []
        for item in text:
            if search_vehicle in str(item):
                indexes.append(text.index(item)) #Append the index of the item where the search critera is found
        for item in indexes:
            if (str('General statistics for') in str(text[item])): #Delete duplicates
                del indexes[indexes.index(item)]
        temp_index = []
        for item in indexes:
            if item not in temp_index:
                temp_index.append(item)
        indexes = temp_index
        temp_index = []
        for item in indexes:
            if ('Battles0' not in text[item + 1]):
                temp_index.append(item)
        indexes = temp_index
        i = 0
        for item in indexes: #Append the 11 statistics after the vehicle
            while i <= 11:
                extractor.append(text[item + i])
                i = i + 1
            i = 0
        for item in extractor:
            if (str('General statistics for') in str(item)): #Guard against duplicates
                del extractor[extractor.index(item)]
            if (str('+') in str(item)): #Guard against numbers denoting an update in the stats
                split_string = str(extractor[extractor.index(item)]).split('+', 1)
                extractor[extractor.index(item)] = split_string[0]
        vehicles = []
        stats = []
        i = 1
        j = 0
        k = 0
        for item in extractor: 
            if search_vehicle in str(item): #Append the first 5 numbers in the extractor array
                vehicles.append(extractor[extractor.index(item)])
                while i <= 5:
                    if 'Respawns' in extractor[extractor.index(item) + i]: #Ignore respawn statistic
                        i = i + 1
                    else:
                        stats.append(int((re.sub("[^.0-9]", "", extractor[extractor.index(item) + i])))) 
                        i = i + 1
                i = 1
            if 'Overall air frags' in item or 'Overall ground frags' in item: #Find overall air frags and ground frags
                stats.append(int((re.sub("[^.0-9]", "", extractor[extractor.index(item)]))))
                j = j + 1
            if j == 2: 
                if stats[-3] == 0: #Set deaths to 1 if it is 0
                    stats[-3] = 1
                    k = 1
                kda = float(stats[-2]/stats[-3])
                kda = round(kda, 2)
                kba = float(stats[-2]/stats[-6])
                kba = round(kba, 2)
                kdg = float(stats[-1]/stats[-3])
                kdg = round(kdg, 2)
                kbg = float(stats[-1]/stats[-6]) 
                kbg = round(kbg, 2) #Calculate kd, kb
                if k == 1: #Set deaths back to 0
                    stats[-3] = 0
                    k = 0
                winrate = float((stats[-5]/stats[-6]) * 100) 
                winrate = round(winrate, 2) #Calculate winrate
                stats.append(kda), stats.append(kba), stats.append(kdg), stats.append(kbg), stats.append(winrate) #Append all the stats
                j = 0
        return stats, vehicles, clan_tag, custom_url #Return the stats, the vehicles played, squadron, and url