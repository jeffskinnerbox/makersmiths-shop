
# My Vision for Makersmiths Volunteer Program
I'm a member of a makerspace call [Makersmiths][01]
All members are expected to volunteer 2 hours per month to perform work tasks
for the care, up-keep, and expansion of the makerspace.

## Current Process
What follows is called the "task volunteering process".
Work tasks are posted on 8.5 x 11 inch sign-up sheet (landscape orientation) posted around the makerspace
and members are expected to voluntarily take one or more of these task and complete them.
When completed, they will sign their name & date to the sign-up sheet for the work task they completed.
With the help of other members of the makerspace,
all the work tasks are expected to be completed.
At random times, these sign-up sheets will be refreshed/replaced with work tasks.

The physical layout of the makerspace is as follows:
* A "shop" is a rented space where the makerspace is physically located.
  Makersmiths has two shops: Makersmiths Leesburg (MSL) and Makesmiths Purcellville (MSP).
  It is unclear at this time if the task volunteering process of MSL and MSP will be the same.
* An "area" is a subsection of a shop and can cover a large part of a shop, such as a floor or building exterior.
* A "location" is a subsection of an area and the location supports a single Makersmiths craft.
  Crafts are things like Laser Cutter, a Wood Shop, Multi-Axis Metal CNC, etc.
  and other spaces like meeting rooms, bathrooms, storage area, and the outside of the building.

These are the actors in the task volunteering process:
* A "member" is the makerspace member that is performing the work tasks, within the task volunteering process.
* A "steward" is a makerspace member that is responsible for the design, maintenance & member training of a location.
  They are also responsible for identifying the required work task to help maintain the safety and proper operation of the location.
* A "shop steward" monitors all activities in the shop.

## Shortcoming of Current Process
The current task volunteering process has several weaknesses we wish to eliminate or diminish:
* After performing a work task, members will often not record their name, or date, or the fact the work task was completed.
* Cumulative recorded keeping of the work tasks are not being maintained for future reference.
  At a minimum, this record keeping maybe required for the makerspace keeping its federal 501(c)(3) tax-exempt status.
* Stewards are ultimately responsible for the work tasks but they have no tools to help monitor the completion of work tasks.
* Some work tasks should be done on a periodically schedule but there no records so this can be monitored.
* Member's who regularly volunteer for work task should be periodically thanked
  for there contribution but there are no records to support this.

## Future Process
It is very important the future task volunteering process be as frictionless as possible.
The effort a members & stewards put into the task volunteering process
must be primarily doing the task and not the "book keeping" for the task.
It important that there are easily managed tools provided for the creating of the sign-up sheets,
simple methods to populating or remove work tasks from the sign-up sheets,
collection of the data on the sheets, easy tools for members to record & monitor their completion of work tasks,
the loading of the sheet data into a storage repository,
and the creation of reports from the stored data.

In the future process, there is a new actor:
* A "shop sergeant" is a member who manages and monitors the task volunteering process itself,
  and they assure the process is engineered to meet its success criteria (aka [KPIs][02]).

Things the shop sergeant will consider to make the process automated and with minimal friction are:
1. Use of QR codes on the sign-up sheets to pop-up a data entry form on the mobile phone.
   The goal would be  1 or 2 clicks on the mobile device to complete the recording of a work task.
1. Use of mobile phone to capture picture of the sign-up sheet and OCR processing of those picture for data entry into Google Sheets.
1. Use of scripts to perform required data processing and notifications.
   Such things as reminding members about task that are over due,
   reminding members of work events, generating period reports, etc.
1. This could potentially be further automated via [Claude in Slack][03].
   This could allow a member to dialog via Slack with an AI agent monitoring the task volunteering process.
   For example, letting a steward add/delete/update a work task
   or request a reminder be sent about work tasks they see are falling behind
   via a special Slack channel.

The new task volunteering process will contain the following sub-processes (aka pipelines):
* Task Database Pipeline
  * An Excel/Google Sheet will be used to record all current and historical work tasks data
    The Excel/Google Sheet is considered the "source of truth" for all work task status.
  * Python/Bash scripts will be used to make add/delete/update to the Excel/Google Sheet.
  * Only Stewards, Shop Stewards, and Shop Sergeant can use the Python/Bash scripts
  * The Slack channel will notify the shop sergeant when add/delete/update are made to the Excel/Google Sheet.
* Task Sheet Pipeline
  * The Excel/Google Sheet can be read and transformed into a work task sign-up sheet via Python/Bash scripts
  * Only Stewards, Shop Stewards, and Shop Sergeant can create work tasks sign-up sheet
  * The Slack channel will periodical notify the shop steward and the shop sergeant that
    significant changes have been made to work tasks and request new sign-up sheets to be printed
  * The Slack channel will notify the shop sergeant when new sign-up sheets is printed
* Task Capture Pipeline
  * A members Android or iPhone mobile phone will be used to capture data when a work task are completed.
    Several capture methods will be considered/prototyped but only one is expected to be implemented:
    1. capture-method-1: captures an image of the sign-up sheet for [OCR][04] reading.
    1. capture-method-2: a QR-Code, located on the task sheets row for the task, will be scanned to record a task completion.
    1. capture-method-3: a single QR-Code, for the whole sign-up sheet, will open a website to record data for a task completion.
  * The capture-method will trigger the execution of a Python/Bash scripts to make
    the appropriate update to the Excel/Google Sheet
  * The Slack channel will notify the shop sergeant when a capture-method has been executed
* Task Reporting Pipeline
  * The Excel/Google Sheet will be used to create reports concerning work task completion progress.
  * Reports will be requested via a Slack channel.
  * Several report types will be available covering individual or group status.
  * All members will have access to these reports and they will contain reports for a member, a location, or the full shop.
  * The Slack channel will notify the shop sergeant when a report is generated



[01]:https://makersmiths.org/
[02]:https://www.kpi.org/kpi-basics/
[03]:https://code.claude.com/docs/en/slack
[04]:https://en.wikipedia.org/wiki/Optical_character_recognition



