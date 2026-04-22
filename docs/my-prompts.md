# Claude Code Prompts
These prompts where used to create portions of this solution.

## 1st Prompt
Read the document @docs/my-understanding.md, and do the following:

1. Improve the readability of this document and place the new version in @docs/requirements.md
1. Make better use of section title to help the readers understanding.  Reformat and expand as needed.
1. Be precise since this document will be used to create design specifications.
1. Make use of tables or process diagrams if that can help.
1. Put in one place a definition of all the actors, processes, etc. being discussed.
1. We anticipate that this solution will be using Agentic AI via [Claude in Slack][03] but very little is said about this.
   Say more about this to inform the reader and to help improve the future design specifications document.
1. When writing, consider the fact that the excalidraw-diagram skill will be used to create some visuals.
1. This is a key document, iterate on it if that can help.
1. Ask me questions to help clarify any issue you find.
   There should be no limit to the number and type of question you ask.

----

## 2nd Prompt
Read the @docs/requirements.md document and notice that the only Actors identified are human
(Member, Steward, Shop Steward, and Shop Sergeant).
There are no system actors explicitly identified in section "2.2 Actors" of the document.
System actors include: QR-Code, Mobile Phone, Slack, Google Sheets, Agentic Workers.
Think deeply about any other actors that might be missing and should also be included.

Here are very brief descriptions of what these system actors I identified do.
You should expand this description to fully clarify what the actor is, what it does, and why.
* Mobile Phone - used to read a QR-code and bring up a website on the phone or initiate an action in the process
* QR-Code - trigger to initiate a process activity like bring up a website on a mobile phone or communicating on Slack
  or initiating an action via an Agentic Worker
* Slack - this is the communications network used by human actors and Agentic Workers to support this process
* Google Sheets - single sources of truth for the state of the work task process
* Agentic Workers - communicate on their assigned Slack channels and performing actions,
  using tools provided, to support the work task process.

Here is what you need to do:
1. Include the system actors within @docs/requirements.md anywhere it help clarify the requirements
2. Similar to section "2.2 Actors", create a table for System Actors
3. Put in CLAUDE.md that all actors (human and system) need to be include in any diagrams that are created for this document.

----

## 3rd Prompt
Read the @docs/requirements.md document and create the missing Excalidraw files referenced in the document
using the excalidraw-diagram skill.
Make sure the Excalidraw files you create includes all the actors defined in the @docs/requirement.md document.
There is potentially one exception, that being the "Pipeline Overview" diagram.

* All human actors should have the same shape and the system actors another shape.
* All actors should have a unique color.
* All diagram titles need to be colored black, using bold fonts, and centered
* Place the files you create in @docs.

----

## 4th Prompt
Read the @docs/requirements.md document and create an appendix section title "Appendix: Things Worth Considering".
These are things that should be talked about for their potential value.
Format it as a bullet list with a bold short full sentence title, followed by a short paragraph describing the idea and its value.
First, and only entry at this time is "Should the mobile experience be a Progressive Web App (PWA)?"
Place this in the document and provide the missing description and value statement.

Additional entries for the appendix are:
* Within the "5.3 Task Capture Pipeline"" section of this document, Should Method 1 — OCR and Method 2 — Per-Task QR be dropped from consideration?
  * Why? Concerns about reading small QR-Code, reliability of OCR
* Any concerns about the section "7.3 Permission Model" being too open or too tight?
* Should additional additional functional prototyping be added to the section "4.3 Current State"?
* Should we drop the requirement in Sections 8.1
  that a fallback (writing on the paper sheet) must always remain available alongside the digital method?
* The goal for Members is 2 hr/wk of volunteer work but the process doesn't measure hours.
  * We should guestimate the hour of each task with a minimum of 15 minutes for a task. This will help set exceptions.

----

## 5th Prompt
I plan to be a regular user of Excalidraw within Claude Code to create slide presentations and diagrams for documents.
These presentations will often be outside of my home office and often with a audience joining via zoom or
other type of conferencing service.
I do not think the Excalidraw will be my best choose for me to present my slides.
I'm considering using [slidev](https://sli.dev/) as my presenting tool and create content via [Excalidraw](https://docs.excalidraw.com/).

Can I make this work, and if so, what would be the work flow?
What tools do I need to install and what are their installation procedures?
Show me your answer, we'll dialog if need, and then put this information in a markdown file.

Give me a script for preparing the Excalidraw files, and then including them into a slidev for presentation.
Make sure to put in your scripts a description of what the script is doing.

Put everything you create in the @presentations directory.

Think hard about this and give me options to select from if the exist.

----

## 6th Prompt
I have a requirements document for a AI enabled process.  For the most part, these requirements are
independent of technology platforms but with the exception that Claude, Slack, Google Sheets,
and mobile phone (Android and iPhone) technologies are referenced.

I'm in the process of getting the requirements reviewed and approved.
Once that is done, I would like to do some prototyping to further expose design & architecture considerations.
I also want to create specification, architecture, and implementation plan documents  to support this project.

What is the best order to d this work.
For example, should I do the architecture document prior to doing any prototyping?
Give me a roadmap of documentation & prototyping  and the justification for that plan.
Consider multiple approachable and look at the pros and cons of each approach.
Give me a markdown document that captures your work and  a Excalidraw diagram that illustrate your approach.

----

## 7th Prompt
Read @docs/requirements.md, and using the insight from that document,
update the files @ai_project_roadmap.md and @ai_project_roadmap.excalidraw.
Make the @ai_project_roadmap.* more specific in what will be accomplished.
Call the new plans @ai_project_roadmap_V2.md and @ai_project_roadmap_V2.excalidraw.

















## X Prompt
Brainstorm on this topic and provide me some options.
For the most promising option, provide me some high-level specifications
and place your findings in @docs/specifications.md.

----

## X Prompt: Modification to Plan
The first step of `@docs/implementation-plan.md` needs to be the creation of
the Python tools defined in `@input/my-prompts.md` file,
section titled "Task List Formatting Tools".
The sign-up sheet is a key human / machine information exchange point that must be trialed first.

The trial will be:
1. Review the sign-up form with both stewards and members.
1. Within the existing Makersmiths process, replace the existing sheets with the newly agreed to sign-up sheet.
1. Discuss with members how the form will eventually automated and get their feedback to factor
   into the specification and implementation plan.

Make required modifications to the documents in `@docs`.
Think Hard about what must be done to create a robust tool.
I expect there will be some issues,
so use the AskUserQuestions tool for all things that require further clarification.

When complete review all documents in `@docs` and `@input` for completeness and consistency.

----

## X Prompt: Task List Formatting Tools
I need two Python program that will convert `@metalshop-volunteer-opportunity.yaml`
into a 8.5 x 11 inch sign-up sheet that can be posted in the makerspace.

The 1st Python program, called `@scripts/generate-signup-sheet-template.py`,
will create the Jinja2 HTML template that capture the format of the sign-up sheet.
This program will use `argparse` module to capture the format of the sign-up sheet from the user.
The default format is expressed below and the command-line arguments will make modifications to the default format.

The 2nd Python program is called `@scripts/signup-sheet.py`.
This will also use `argparse` module for commandl-line options specifying a Jinja2 template
and a YAML file formated like `metalshop-volunteer-opportunity.yaml` or `MSL-volunteer-opportunities.yaml`
that will be parsed to inserted into the template to create the sign-up sheet.

The default output of `@scripts/generate-signup-sheet-template.py` should look like this:
1. The the 8.5x11 inch sign-up sheet should be printed in landscape format as a HTML template that can be used for all locations.
1. Each 8.5×11 sheet should cover only one location (e.g., Metal Shop, Leesburg).
1. Heading of the sign-up sheet should be formatted like this:

  ```text
  <formatted to the left><12pt Bold>Location: <name of location>
  <formatted to the left><10pt Bold>Steward: <name of steward>
  <formatted in the center><14pt bold red font>Volunteer Oppertunities
  <formatted to the right><Makersmaiths Logo>
  ```

1. Footer of the sign-up sheet should be formatted like this in bold 8pt font:

  ```text
  <formatted to the left>
  Question concerning the design & use of this form should be sent to Jeff Irland (xxx)
  ```

1. Body of the sign-up sheet should

| Task Name | Frequency | Member (sign) | Date | Log It (QR) |
|-----------|-----------|---------------|------|-------------|
| Clean welding tables | Weekly | _(sign here)_ | _(date)_ | [QR image] |

* Physical columns remain unchanged — members can sign with pen as before
* New **Log It** column adds a per-task QR code for digital logging

Think Hard about what must be done to create a robust tool.
I expect there will be some issues,
so use the AskUserQuestions tool for all things that require further clarification.

----

## X Prompt: MSL-volunteer-opportunities.yaml to `.xlsx` File
* Create Python script that takes the `@input/MSL-volunteer-opportunities.yaml` file
  and places its content in a Excel `.xlsx` file `@input/google-sheet.xlsx`.
* The Python script will be called `@scripts/yaml-to-sheets.py`
* There will be one row in the `.xlsx` file for each of the `task` key.
* The column headings of the `.xlsx` file will be:
  * area name
  * location name
  * steward
  * task
  * task_id
  * frequency
  * purpose
  * instructions
  * supervision
  * last_date
* The rows of the `.xlsx` file will be:
  * "area name" value
  * "location name" value
  * "steward" value
  * "task" value
  * "task_id" value
  * "frequency" value
  * "purpose" value
  * "instructions" value
  * "supervision" value
  * "last_date" value
* Like things (e.g. same area, same location) should be in adjacent rows in the `.xlsx` file
* make sure the "task_id" value is always present, and if not, stop and tell the user to fix it
* make sure the "task_id" value is always unique, and if not, stop and tell the user to fix it
* make sure there are no duplicate tasks for a location, and if so, stop and tell the user to fix it
* if the `@input/google-sheet.xlsx` doesn't exist, create it
* if the `@input/google-sheet.xlsx` already exist, create a backup call `@input/google-sheet.xlsx.bak`.
  Increment the backup if that already exists (ex. if `@input/google-sheet.xlsx.bak` exist, create a .bak1 or bak2 or etc.)

