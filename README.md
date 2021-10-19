# McGillCourseSeatsTimeline

Goal: create a historical chart with the rate at which different courses at McGill University fill up to enable students to have an idea of how much in advance they should register for a course, if a course usually fills up, or if during add-drop period some seats get available, ect...

To do so, it scrapes the McGill VSB website (https://vsb.mcgill.ca/vsb/welcome.jsp) multiple times a day.

--

This is still in development:

### DONE:
+ Iterate through all COMP FALL 2021 course and check the number of seats available (and waitlist if applicable) on VSB with Seleniunm web scraper
+ Save data to MangoDB with pyMango
+ Automated in Heroku : Implemented in a Heroku server so that it can automatically save course data multiple times per day

### TODO:
+ Create .env for credentials
+ Add COMP WINTER 2021
+ Add ALL courses
+ Add data visulation
+ Create further documentation/tutorial
+ Misc

## Snapshot of scraped data :
Here is the snapshot of the first 2 scrapes for a portion of CS courses, right after course registration started.
The "-4" for waitlist indicates there is no waitlist available for this course at the moment.
<img width="1231" alt="Mango DB snapshot" src="https://user-images.githubusercontent.com/10205873/137929805-768eda81-1167-4f77-9529-5437a04d6876.png">

