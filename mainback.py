#Amir Alaj & Kristi Luu; 
#This program uses the requests library to read in the html file from a website
#('https://www.bls.gov/ooh/computer-and-information-technology/home.htm') and grabs the URLs within
#in order to grab data about jobs that relate in computers. This information is stored into a nested 
#dictionary and writes it all to a JSON file. This JSON file is then read in and the information is
#put into three different tables wihtin an SQL database.
import urllib.request as ur
import requests
from bs4 import BeautifulSoup 
import time
import json
import re
import sqlite3
"""
def main():
    jobList, urlList = getURL()
    dataDict = createDictionary(jobList, urlList)  
    createJSON(dataDict)

def getURL():
    #This function reads in the first link to create a list of the urls in the page
    #and also creates another list with the text from the urls which are the names of
    #the jobs. Returns both lists.
    jobList = []
    urlList = []
    try:
        page = requests.get('https://www.bls.gov/ooh/computer-and-information-technology/home.htm')
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "lxml")
        for tag in soup.find_all('h4'):
            urlList.append(tag.a['href'])
            mainKey = " ".join(str(tag.a.text).split())
            jobList.append(mainKey)    
        return jobList, urlList
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", str(e))
    except requests.exceptions.ConnectionError as e:
        print("Connection Error:", str(e))
    except requests.exceptions.Timeout as e:
        print("Timeout Error:", str(e))
    except requests.exceptions.RequestException as e:
        ("Request Exception:", str(e))

def createDictionary(jobList, urlList):
    #Uses the url list and job title list to read in each page with the information
    #of the specific jobs. Creates two lists with the categories and values of the data
    #in these links, all information is zipped to a nested dictionaty and is returned.
    dataDict = {}
    keyList = []
    dataList = []  
    try:
        for i in range(len(urlList)):
            page = requests.get('https://www.bls.gov' + str(urlList[i]))
            page.raise_for_status()
            soup = BeautifulSoup(page.content, "lxml")
            soup = soup.find(id = "quickfacts")
            for tag in soup.find_all('th'):
                if not "Quick Facts" in str(tag.text):
                    key = " ".join(str(tag.text).split())
                    keyList.append(key)
            for tag in soup.find_all('td'):
                value = re.sub(' +', ' ', tag.text.strip())
                if "See How to Become" in value:
                    value = "Certification"
                dataList.append(value)
                
            for j in range(len(dataList)):
                if not "years" in str(dataList[j]):
                    m = re.search("(-*\d+),*(-*\d*),*(-*\d*)", str(dataList[j]))
                    if m:
                        if not m.group(2):
                            dataList[j] = int(m.group(1))
                        elif not m.group(3):
                            dataList[j] = int(m.group(1) +m.group(2))
                        else:
                            dataList[j] = int(m.group(1) + m.group(2) + m.group(3))
            dataDict[jobList[i]] = dict(zip(keyList, dataList))
        return dataDict
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", str(e))
    except requests.exceptions.ConnectionError as e:
        print("Connection Error:", str(e))
    except requests.exceptions.Timeout as e:
        print("Timeout Error:", str(e))
    except requests.exceptions.RequestException as e:
        ("Request Exception:", str(e))    
        
def createJSON(dataDict):
    #Writes the dictionary of all the data to a JSON file.
    with open('occupationInfo.json', 'w') as fh:
        json.dump(dataDict, fh, indent = 3)    
    
main()
"""
def main():
    with open('occupationInfo.json', 'r') as fh:         
        dataDict = json.load(fh)
        
    conn = sqlite3.connect('occupation.db')
    cur = conn.cursor()    
    
    fieldList = createFieldsTable(dataDict, cur)
    createJobDataTable(dataDict, cur, fieldList)
    
    conn.commit()
    conn.close()    
        
def createFieldsTable(dataDict, cur):
    #This function creates a list of the data categories and puts it into a one
    #row SQL table with all categories, returns the list of categories.
    fieldList = []
    for field in dataDict["Computer and Information Research Scientists"]:
        fieldList.append(field)
    
    cur.execute('''DROP TABLE IF EXISTS OccupationFields''')
    cur.execute('''CREATE TABLE OccupationFields ("{}" TEXT);'''.format(str(fieldList[0])))
    
    for i in range(1, len(fieldList)):
        cur.execute('''ALTER TABLE OccupationFields ADD COLUMN "{}" TEXT'''.format(str(fieldList[i])))
    cur.execute('''DROP TABLE IF EXISTS Majors''')
    cur.execute('''CREATE TABLE Majors 
               (majorLevel INTEGER NOT NULL PRIMARY KEY,
               majorType TEXT UNIQUE ON CONFLICT IGNORE)''')
    cur.execute('''INSERT INTO OccupationFields 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', (fieldList[0], fieldList[1], fieldList[2], fieldList[3], fieldList[4], fieldList[5], fieldList[6]))    
    return fieldList

def createJobDataTable(dataDict, cur, fieldList):
    #This function uses the dicitonary of data and the category list to create two
    #tables for the SQL database. First is a table of required majors for the jobs, and
    #gives them a unique id. Then the large table of data is made with 9 columns and 10 
    #rows, the education column is replaced with the id for the majors.
    cur.execute('''DROP TABLE IF EXISTS Majors''')          
    cur.execute('''CREATE TABLE Majors(             
                   id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                   major TEXT UNIQUE ON CONFLICT IGNORE)''')  

    cur.execute('''DROP TABLE IF EXISTS JobData''')
    cur.execute('''CREATE TABLE JobData (
                   id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                   Job_Title TEXT,
                   Median_Pay INTEGER,
                   Education TEXT,
                   Experience TEXT,
                   Training TEXT,
                   Num_Of_Jobs INTEGER,
                   Growth_Rate INTEGER,
                   Change INTEGER)''')

    for jobTitle in dataDict:
        cur.execute('''INSERT INTO Majors (major) VALUES(?)''', (dataDict[jobTitle][fieldList[1]], ))
        cur.execute('SELECT id FROM Majors WHERE major = ? ', (dataDict[jobTitle][fieldList[1]], ))
        major_id = cur.fetchone()[0]
        
        cur.execute('''INSERT INTO JobData (Job_Title, Median_Pay, Education, Experience, Training, Num_Of_Jobs, Growth_Rate, Change)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                        , (jobTitle, dataDict[jobTitle][fieldList[0]], major_id, dataDict[jobTitle][fieldList[2]], dataDict[jobTitle][fieldList[3]], 
                           dataDict[jobTitle][fieldList[4]], dataDict[jobTitle][fieldList[5]], dataDict[jobTitle][fieldList[6]]))
        
main()


    



                                            


         
            
                



     
   

            
