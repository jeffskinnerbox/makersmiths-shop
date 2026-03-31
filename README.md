<!--
Maintainer:   jeffskinnerbox@yahoo.com / www.jeffskinnerbox.me
Version:      0.0.0
-->

<div align="center">
<img src="https://raw.githubusercontent.com/jeffskinnerbox/blog/main/content/images/banners-bkgrds/work-in-progress.jpg"
    title="These materials require additional work and are not ready for general use." align="center" width=420px height=219px>
</div>


---------------

* [How to Use Claude AI in Slack - Complete Setup Guide (2026)](https://www.youtube.com/watch?v=VOAXzliSW64)
* [Autonomous Slack AI Agent with Claude](https://www.youtube.com/watch?v=jUDl-rO-cvA)
* [Full Tutorial: Connect Claude Code to Google, Slack, and Reddit in 40 Min (Skills + MCPs)](https://www.youtube.com/watch?v=1B3Ffo8snfY)
* [Claude Cowork Slack integration: A complete guide for teams in 2026](https://www.eesel.ai/blog/claude-cowork-slack-integration)




# README
It is generally believed that our current process for recording volunteer hours of our Makersmiths members
presents too much friction to our member.
So the over arching objective here is to make it easier for Makersmiths members to record their volunteer hours.
We intent to address this in the following way:

1. Establish any easy to maintain methodology for our stewards to record what tasks they need help with from membership volunteers.

## YAML File Format
YAML (which stands for "**YAML Ain't Markup Language**")
is simply a way to represent structured data in plain text that is both human-readable and machine-readable.
It's trying to capture relationships between data — specifically:

* **Hierarchy** — what belongs to what (a task belongs to a location, a volunteer belongs to a task)
* **Collections** — groups of similar things (a list of tasks, a list of locations)
* **Key-value Pairs** — named properties and their values (task name, frequency, date)

The goal is to store that information in a format that:

* A human can read and edit with just a text editor
* A computer program can parse and use (a website, an app, a database, etc.)

 So YAML sits somewhere between a spreadsheet (which also captures structured data) and a full database,
 but with no special software required to write or read it.

Part of the beauty of YAML is it simplicity.
It only takes these four elements to capture data — indentation, colons, dash, and the three dashes.
That is all you really need to represent almost any data structure.

Here are meanings of the YAML elements:
* **Indentation (2 spaces)** defines the data hierarchy.
  The child data is indented under its parent. The number of spaces must be consistent (2 is convention),
  and tabs are not allowed. If something is indented under another thing, it belongs to that thing.
* **Colon `:`** defines a key-value pair.
  Whatever is to the left is the key (aka label), whatever is to the right is the value.
* **Dash `-`** at the beginning of a line indicates a list item.
  A list containing multiple items. Each `-` marks the start of a new entry in that list.
* **Triple dash `---`** in YAML is called a document separator (or document start marker).
  After this marker, you can start defining an entirely new data structure.

## The Data Model
The over arching objective is make it easy for Makersmiths members to record their volunteer hours.

```text
Data Model
   shop -----------> area -----------> location ----------> work_tasks --------> task

Examples
    LMS, PMS     Main Floor,       Leatherworking Shop,   Dust & Wipe Down Machines
                 Basement,         Downstairs Bathroom,
                 Outside, etc.     Garden Area, etc.
```

---------------

```bash
# yaml linter to spot syntax errors
yamllint task-list.yaml

# format task-list.yaml into a markdown file
python3 parse-task.py task-list.yaml task-list.md

# convert markdown file to MS Word .docx
pandoc -f gfm task-list.md -o task-list.docx

# convert yaml format to json format
python yaml-to-json.py task-list.yaml | jq -C '.'
```

---------------

## Use Cases & Features
A **use case** is a written description or diagram detailing how a user (actor)
interacts with a system or product to achieve a specific goal.
It outlines the step-by-step actions, including both successful paths and potential errors,
to help developers understand, test, and improve product functionality.

A software **feature** is a distinct, user-visible capability, functionality, or characteristic
of a software application designed to satisfy specific user needs, solve problems, or add value.
It acts as a, often autonomous, component of the system that enhances the product's overall utility.

