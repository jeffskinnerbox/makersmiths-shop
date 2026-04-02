
# Claude Code Prompts
These prompts where used to create portions of this solution.

## My Vision for Makersmiths Volunteer Program
I'm a member of a makerspace call Makersmiths.
All members are expected to volunteer 2 hours per month to perform work tasks
for the care, up-keep, and expansion of the makerspace.

Work tasks are posted on 8.5 x 11 inch sign-up sheet posted around the makerspace
and members are expected to voluntarily take one or more of these task and complete them.
When completed, they will sign their name and date to the listed task on the sign-up sheet.
Once completed, other members will see it as completed and must pick other task to perform.

Periodically the data (task, member name, and date) on the sigh-up sheets
must be gathered and put in a Google Sheets log.
When this data is gathered, new sign-up sheets will be posted with additional uncompleted tasks.
Google sheets will be used to create reports
that will document what progress is being made within the makerspace.
The Google Sheet is considered the "source of truth" for task completion,
and so its timely & accurate update is important.

It very important the this task volunteering process be as frictionless as possible.
The effort a member puts in must be primarily doing the task and not the "book keeping" for the task.
It important that easily managed tools be provided for the creating of the sign-up sheets,
collection of the data on the sheets, the loading of the data into Google Sheets, and the creation of Google reports.

Things to consider to make the process automated and with minimal friction are:
1. Use of mobile phone to capture picture of the sign-up sheet and OCR processing of those picture for data entry into Google Sheets.
1. Use of QR codes on the sign-up sheets to pop-up a data entry form on the mobile phone
1. Use of Claude AI agents to perform required data processing and workflow.
1. Use of Claude in Slack so user can dialog with Claude to perform action to support the task management process.

Brainstorm on this topic and provide me some options.
For the most promising option, provide me some high-level specifications
and place your findings in @specifications.md.

----

## Modification to Plan
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

## Task List Formatting Tools
I need two Python program that will convert @metalshop-volunteer-opportunity.yaml
into a 8.5 x 11 inch sign-up sheet that can be posted in the makerspace.

The 1st Python program, called `@scripts/signup-sheet-template.py`,
will create the Jinja2 HTML template that capture the format of the sign-up sheet.
This program will use `argparse` module to capture the format of the sign-up sheet from the user.
The default format is expressed below and the command-line arguments will make modifications to the default format.

The 2nd Python program is called `@scripts/signup-sheet.py`.
This will also use `argparse` module for commandl-line options specifying a Jinja2 template
and a YAML file formated like `metalshop-volunteer-opportunity.yaml` or `tasks-list.yaml`
that will be parsed to inserted into the template to create the sign-up sheet.

The default output of `@scripts/signup-sheet-template.py` should look like this:
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

- Physical columns remain unchanged — members can sign with pen as before
- New **Log It** column adds a per-task QR code for digital logging

Think Hard about what must be done to create a robust tool.
I expect there will be some issues,
so use the AskUserQuestions tool for all things that require further clarification.

