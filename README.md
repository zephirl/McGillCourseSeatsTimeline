# McGillCourseSeatsTimeline
VSB Scraper to get seats available for a list of courses
--
Goal: create a historical chart with the rate at which different courses at McGill fill up to enable students to have an idea of how much in advance they should register for a course, if a course usually fills up, or if during add-drop period some seats get available, ect...
--
This is still in development:

DONE:
+ Iterate through all COMP FALL 2021 course and check the number of seats available (and waitlist if applicable) on VSB with Seleniunm web scraper
+ Save data to MangoDB with pyMango
+ Automated in Heroku : Implemented in a Heroku server so that it can automatically save course data multiple times per day

TODO:
+ Create .env for credentials
+ Add COMP WINTER 2021
+ Add ALL courses
+ Add data visulation
+ Create further documentation/tutorial
+ Misc
