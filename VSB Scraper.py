from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.keys import Keys
import csv

def initialize():
    # Instantiate options
    opts = Options()
    opts.add_argument(" — headless") # Uncomment if the headless version needed
    opts.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    # Set the location of the webdriver
    # chrome_driver = os.getcwd() + "/Users/zephir/Downloads/chromedriver"
    chrome_driver = "/Users/zephir/Downloads/chromedriver"
    
    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)
    return driver


def getSeats_byCourseCode(driver, courseCode):
    # Load the HTML page
    driver.get("https://vsb.mcgill.ca/vsb/criteria.jsp?access=0&lang=en&tip=1&page=results&scratch=0&term=202109&sort=none&filters=iiiiiiiii&bbs=&ds=&cams=Distance_Downtown_Macdonald_Off-Campus&locs=any&isrts=")
    
    time.sleep(0.5)
    crnsInput = driver.find_element_by_id("code_number")
    crnsInput.send_keys(courseCode)
    crnsInput.send_keys(Keys.ENTER)
    time.sleep(1)
    

    courseData = set() # (crns;seatNumbers;waitingLists) - a set is used to avoid duplicates
    
    pageNumber =  int(driver.find_element_by_class_name("resultMax").get_attribute("innerHTML")) # When multiple sections are on different pages
    
    for i in range (pageNumber):
        pageData = getElementsOnPage(driver)
        courseData = courseData.union(pageData)
        time.sleep(0.2)
        driver.find_element_by_xpath('//*[@id="page_results"]/div[5]/div[3]/div[3]/div[1]/table/tbody/tr[1]/td[4]/a').click()
    
            
    return courseData



def getElementsOnPage(driver):
    sectionData = set()
    crns = []
    seatNumbers = []
    waitingLists = []
    
    try:
        seatNumberElements = driver.find_elements_by_class_name("seatText")
    except:
        print("sleepmore")
        time.sleep(1)
        seatNumberElements = driver.find_elements_by_class_name("seatText")

    finally:
        seatNumberElements = driver.find_elements_by_class_name("seatText")
        crnElements = driver.find_elements_by_class_name("crn_value")
        # waitingListElements = TODO
        for seatNumber in seatNumberElements:
            seatNumbers.append(seatNumber.get_attribute("innerHTML"))
        for crn in crnElements:
            crns.append(crn.get_attribute("innerHTML"))
            waitingLists.append(-1)
        # for waitingList in waitingListElements:
        #     waitingLists.append(waitingList.get_attribute("innerHTML"))
            
        
        
        for i in range (len(crns)):
            sectionDataTuple = tuple([ crns[i], seatNumbers[i], waitingLists[i] ]) # Needs to be converted into a tuple to be in a set 
            sectionData.add(sectionDataTuple)
    
    
    return sectionData



def iterateThroughComp(driver, file):
    with open("COMP_output.csv", mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(['Course Subject', 'Course ID', 'Course Name', 'crn', 'Seats Available','Waitlist','HTML Box','Extra Info'])
        
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                
                # else:
                elif line_count <= 4: # For debugging
                    line_count += 1
                    courseData = getSeats_byCourseCode(driver, (row[0]+" "+row[1]))
                    for sectionData in courseData:
                        print(f'\t{row[0]} {row[1]} ({row[2]}) with crn {sectionData[0]} has {sectionData[1]} seats available, with {sectionData[2]} seats available on the waitlist.')
                        output_writer.writerow([row[0], row[1], row[2], sectionData[0], sectionData[1],sectionData[2],'',''])

if __name__ == "__main__":
    driver = initialize()
    # getSeats_byCourseCode(driver, "COMP 302")
    iterateThroughComp(driver, "COMP_input.csv")
    # getSeatsFromCRN(driver, "2749")
