from selenium import webdriver  # Web Scraping Library
from selenium.webdriver.chrome.options import Options
import pymongo  # To connect to MangoDB
import time
from datetime import datetime
from selenium.webdriver.common.keys import Keys
import csv
import re  # To search substrings



# Instantiates Chrome webdriver and Connect to MangoDB
# Returns webdriver and MangoDB collection
def initialize():
    # Instantiate Chrome options
    opts = Options()
    opts.add_argument(" — headless") # Uncomment if the headless version needed
    opts.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    # Set the location of the webdriver
    chrome_driver = "/Users/zephir/Downloads/chromedriver"

    # Instantiate a webdriver
    print("- Instantiating webdriver")
    driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)
    
    # Connect to MangoDB
    print("- Connecting to MangoDB client")
    client = pymongo.MongoClient("mongodb://<user>:<password>@<host>:<port>/<db_namespace>")
    print("- Connecting to database")
    db = client.McGillCourseSeatsTimeline
    print("- Connecting to collection")
    collection = db["COMP_FALL2021_Collection5"]
    
    return driver, collection



# Returns courseData as a set of sets:
# The outer set is the course set in the form of (course1Data,course2Data,...)
# Each inner courseXData data set is a set of course section the form (crn,seats,waitlist)
# For example: ( (2723,227,0), (2727,43,0) )
def getSeats_byCourseCode(driver, courseCode):
    # Load the HTML page
    print("+++++++++++ Loading HTML page for " + courseCode + " +++++++++++")
    driver.get("https://vsb.mcgill.ca/vsb/criteria.jsp?access=0&lang=en&tip=1&page=results&scratch=0&term=202109&sort=none&filters=iiiiiiiii&bbs=&ds=&cams=Distance_Downtown_Macdonald_Off-Campus&locs=any&isrts=")
    
    # Enter Course Code in bar
    time.sleep(1)
    crnsInput = driver.find_element_by_id("code_number")
    crnsInput.send_keys(courseCode)
    crnsInput.send_keys(Keys.ENTER)
    time.sleep(1)
    
    # (crns;seatNumbers;waitingLists) - a set is used to avoid duplicates
    courseData = set() 
    
    # Get the number of result page - When multiple sections are on different pages
    pageNumber =  int(driver.find_element_by_class_name("resultMax").get_attribute("innerHTML")) 
    
    for i in range (pageNumber):
        pageData = getElementsOnPage(driver) # Gets all course data from given page, there can be multiple sections
        courseData = courseData.union(pageData)
        time.sleep(0.5)
        driver.find_element_by_xpath('//*[@id="page_results"]/div[5]/div[3]/div[3]/div[1]/table/tbody/tr[1]/td[4]/a').click() # Load next page if available
    
            
    return courseData



# Gets all course data from given page, there can be multiple sections
# Returns courseData as a set of sets as in getSeats_byCourseCode
def getElementsOnPage(driver):
    sectionData = set()
    crns = []
    seatNumbers = []
    waitingLists = []
    print("getElementsOnPage")
    
    try:
        crnElements = driver.find_elements_by_class_name("crn_value")
    except:
        print("/!\ crnElements not found, trying again after 1 second to let the page load more...")
        time.sleep(1)
        crnElements = driver.find_elements_by_class_name("crn_value")
        
    finally:
        # Find elements containing seat number or full, needed as different class name between the 2
        # Add number of seats available and waitlist if applicable
        leftnclearElements = driver.find_elements_by_xpath("//*[contains(@class,'leftnclear')]")
        print("Found " + str(len(leftnclearElements)) + " leftnclearElements")
        
        trynumber = 0
        while (len(leftnclearElements) <= 5) and trynumber < 4:
            trynumber+=1
            print("/!\ There should be more than 5 leftnclearElements, trying again after 1 second to let the page load more...")
            time.sleep(1)
            leftnclearElements = driver.find_elements_by_xpath("//*[contains(@class,'leftnclear')]")
            print("Try #" + str(trynumber) + ": This time found " + str(len(leftnclearElements)) + " leftnclearElements")
        
        
        for i in range(len(leftnclearElements)):
            # time.sleep(0.1)
            leftnclear = leftnclearElements[i]
            innerLeftnclear = leftnclear.get_attribute("innerHTML")
            
            if "Seats: " in innerLeftnclear:
                print("Found seat tag:::: " + innerLeftnclear)
                
                # If no seats available add 0 as seatNumber
                if "Full" in innerLeftnclear:
                    seatNumbers.append(0)
                    nextLeftnclear = leftnclearElements[i+1]
                    innerNextLeftnclear = nextLeftnclear.get_attribute("innerHTML")
                    
                    # If there is a waitlist, add waitlist count
                    if "waitText" in innerNextLeftnclear:
                        waitlistGroup = re.search('<span title="There(.*)class="waitText">(.*)</span></span>', innerNextLeftnclear) # Extract waitlist fraction
                        waitlistFraction = waitlistGroup.group(2)
                        
                        waitlistFractionSeparator = re.search('(.*)/(.*)', waitlistFraction)
                        waitlistNumerator = int(waitlistFractionSeparator.group(1))
                        print("waitlistNumerator: " + str(waitlistNumerator))
                        waitlistDenominator = int(waitlistFractionSeparator.group(2))
                        print("waitlistDenominator: " + str(waitlistDenominator))
                        
                        waitlistRemaining = waitlistDenominator-waitlistNumerator
                        print("waitlistRemaining: " + str(waitlistRemaining))
                        waitingLists.append(waitlistRemaining)
                        
                        #TODO add waitlist cap entry
        
                        # waitingLists.append(str(waitlistFraction))
                
                # If some seats are available add their number
                else:
                    seatNumberGroup = re.search('Seats: <span class="seatText">(.*)</span>', innerLeftnclear) # Extract seat number
                    seatNumber = seatNumberGroup.group(1)
                    seatNumbers.append(seatNumber)
                    waitingLists.append(-4) # -4 indicates that there is no waitlist available for the moment
        
        
        crnElements = driver.find_elements_by_class_name("crn_value")
        for crn in crnElements:
            crns.append(crn.get_attribute("innerHTML"))
        
        # Save data as tuples in sets
        for i in range (len(crns)):
            try:
                sectionDataTuple = ( crns[i], seatNumbers[i], waitingLists[i] ) # Needs to be a tuple to be in a set 
            except IndexError:
                sectionDataTuple = ( -3, -3, -3 ) # -3 indicates an IndexError
            finally:
                sectionData.add(sectionDataTuple)
    
    
    return sectionData


# Iterate through all available COMP courses (listed in csv file) to scrape data and update MangoDB with new seat number and waitlist 
def iterateThroughComp(driver, collection, file):
    # Get current time and date
    now = datetime.now()
    nowFormatted = now.strftime("%d/%m/%Y - %H:%M:%S")
    nowFormatted_new = now.strftime("<%Y-%m-%d%H:%M:%S>")
    # nowDate = now.strftime("%d/%m/%Y")
    # nowTime = now.strftime("%H:%M:%S")
    
    seatFieldName = "Seats available - " + nowFormatted
    waitlistFieldName = "Waitlist - " + nowFormatted
    
    # Create new fields for scrape instance, with time of scraping, Initialize them with -2 for untouched
    newFieldResponse_seatFieldName = collection.update_many({}, {"$set": {seatFieldName: -2}}, upsert=False, array_filters=None)
    newFieldResponse_waitlistFieldName = collection.update_many({}, {"$set": {waitlistFieldName: -2}}, upsert=False, array_filters=None)
    
    # Add Date and Time data in both colomn for clarity
    query_DateAndTime = { "Course Subject": "DateAndTime" }
    value_DateAndTime_seatFieldName = { "$set": { seatFieldName: nowFormatted_new } }
    value_DateAndTime_waitlistFieldName = { "$set": { waitlistFieldName: nowFormatted_new } }
    
    value_DateAndTime_seatFieldName = collection.update_one(query_DateAndTime,value_DateAndTime_seatFieldName)
    value_DateAndTime_waitlistFieldName = collection.update_one(query_DateAndTime,value_DateAndTime_waitlistFieldName)
   
    
   
    
    # Gets all COMP courses available in Fall 2021 from csv file
    # Header is ['Course Subject', 'Course ID', 'Course Name']
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            
            else:
            ###### For debugging #######################################
            # elif line_count <= 1: 
                # line_count += 1
                # courseData = getSeats_byCourseCode(driver, "COMP 417")
            ############################################################
                courseData = getSeats_byCourseCode(driver, (row[0]+" "+row[1])) # row[0] is course abbreviation (ex: COMP) and row[1] is course code (ex: 202)
                for sectionData in courseData:
                    # now = datetime.now()
                    # nowFormattednowFormatted = now.strftime("%d/%m/%Y - %H:%M:%S")
                    print(f'\t{row[0]} {row[1]} ({row[2]}) with crn {sectionData[0]} has {sectionData[1]} seats available, with {sectionData[2]} seats available on the waitlist at date and time {nowFormatted}.')
       
        
                    # Update fields for crn instance
                    query = { "crn": int(sectionData[0]) }
                    seatValue = { "$set": { seatFieldName: int(sectionData[1]) } }
                    waitlistValue = { "$set": { waitlistFieldName: int(sectionData[2]) } }
                    
                    seatResponse = collection.update_one(query,seatValue)
                    waitlistResponse = collection.update_one(query,waitlistValue)
                    

if __name__ == "__main__":
    # Instantiates Chrome webdriver and Connect to MangoDB
    print("Initialisation...")
    driver, collection = initialize()
    print("Initialisation complete with [" + str(driver) + "] driver and [" + str(collection) + "] collection." + "\n ---------------------------"  )
    
    # Iterate through all available COMP courses (listed in csv file) to scrape data and update MangoDB with new seat number and waitlist 
    iterateThroughComp(driver, collection, "COMP_FALL2021_input.csv")
    
    driver.close()
