# Claude Code Prompts
These prompts where used to create portions of this solution.

## 1st Prompt
I'm giving a presentation to team members and the topic within the @docs/requirements.md.
It a technical audience and I'm looking for their critical review & recommendations
to improve the solution and make that solution the best fit possible for the problem we are addressing.

I plan to use [Slidev](https://sli.dev/) and [Excalidraw](https://docs.excalidraw.com/) tools to create and display my presentation.
I want to use Slidev to capture a summary of each section of the @docs/requirements.md.
As part of this summary, the diagrams used include content via [Excalidraw](https://docs.excalidraw.com/).
You should uses the excalidraw-diagram skill and the slidev skill.

1. First, create the documents diagrams the excalidraw-diagram skill:
* Read the @docs/requirements.md document and create the missing Excalidraw files referenced in the document
* Make sure the Excalidraw files you create includes all the actors and triggers defined in the @docs/requirement.md document.
  There is potentially one exception, that being the "Pipeline Overview" diagram which should simplified but complete picture.
* All human actors should have the same shape and the system actors another shape.
* All actors should have a unique color.
* Show the trigger event that puts the pipeline in motion
* All diagram titles need to be colored black, using bold fonts, and centered
* Place the .excalidraw files you create in @presentations/requirements-review/diagrams/
  and the .png / .svg files you create in @presentations/requirements-review/assets/

2. Second step is to use the slidev skill to create a summary of all sections of the document:
* Read the @docs/requirements.md document and create a presentation that reviews all the section in the document.
* Place the files you create in @presentations/requirements-review/slides.md.
* Make sure to display the diagrams in the document using links to their .svg instances

Don't make assumption about this presentation, but instead,
as ask many question as required, using your grill-me skill, to get a clear picture of your task.

---


