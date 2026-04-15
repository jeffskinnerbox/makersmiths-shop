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
Read the @docs/requirements.md document and create the missing Excalidraw files referenced in the document
using the excalidraw-diagram skill. Place the files you create in @docs.

----









## 2nd Prompt
Brainstorm on this topic and provide me some options.
For the most promising option, provide me some high-level specifications
and place your findings in @docs/specifications.md.

----

## 2nd Prompt: Modification to Plan
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

## 3rd Prompt: Task List Formatting Tools
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

## 4th Prompt: MSL-volunteer-opportunities.yaml to `.xlsx` File
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

