
# README
If you have no experience with Claude Code
* [5 Fun Projects Using Claude Code](https://www.kdnuggets.com/5-fun-projects-using-claude-code)

----

## `proto1` - CRUD for SQLite

----

## `proto2` - Build a Chatbot With Python
The Python ChatterBot library lets you build a self-learning command-line chatbot with just a few lines of code.
The objective is to learn the basic of interactive chatbot using Python’s ChatterBot.
Starting with an untrained chatbot and them move onto learn how you can train such a chatbot.

* [ChatterBot: Build a Chatbot With Python](https://realpython.com/build-a-chatbot-python-chatterbot/)
* [Building a Chatbot using Chatterbot in Python](https://www.datacamp.com/tutorial/building-a-chatbot-using-chatterbot)
* [AI Coding Agents Guide: A Map of the Four Workflow Types](https://realpython.com/ai-coding-agents-guide/)

----

## `proto3` - Slack Integration
What does the command `/install-slack-app` in Claude Code do?
It's a simple convenience command.
`/install-slack-app` opens the Slack Marketplace page for the Claude app in your browser,
making it easy to install Claude in your Slack workspace.
It takes no arguments, and internally it increments a `slackAppInstallCount` counter in your global config to track usage.

That's it — it's essentially a browser shortcut, not a configuration command.
If you want the actual Slack integration for routing coding tasks,
the relevant command is `/plugin` install slack (or `claude plugin install slack` from the shell),
which sets up the Slack MCP server.

* [How to Set Up Claude Code Channels Locally](https://www.kdnuggets.com/how-to-set-up-claude-code-channels-locally)

### Slack Integration
The Claude Code command `/install-slack-app` does substantially more.
It installs and configures the Slack MCP server for Claude Code.
Once the plugin loads, the Slack MCP server is automatically configured
and you're prompted to authenticate into your Slack workspace via OAuth.

Under the hood, it writes an MCP configuration to `.mcp.json` pointing at `https://mcp.slack.com/mcp` with OAuth credentials.
The practical result, per Slack's own docs:
it lets you connect to Slack for search, messaging, and document access.
It gives Claude Code context from your Slack workspace or the ability to post updates.
Think of it like mounting a network drive:
after running it, Claude Code gains Slack as a readable/writable data source within your session,
rather than just opening a browser page.

----

# protoX - Claude and n8n

* [Claude Code vs n8n? Wrong Question](https://www.youtube.com/watch?v=R8kSHT-JWSc)

----

# protoX - Build LLM From Scratch
A hands-on workshop where you write every piece of a GPT training pipeline yourself, understanding what each component does and why.

* [An LLM From “Scratch”](https://hackaday.com/2026/05/07/an-llm-from-scratch/)
* [Train Your Own LLM From Scratch](https://github.com/angelos-p/llm-from-scratch/tree/main)
* [An Animated Walkthrough Of How Large Language Models Work](https://hackaday.com/2024/11/20/an-animated-walkthrough-of-how-large-language-models-work/)
* [Learn AI Via Spreadsheet](https://hackaday.com/2024/03/18/learn-ai-via-spreadsheet/)

----

# protoX - Build Vector Search From Scratch
* [How to Build Vector Search From Scratch in Python](https://www.kdnuggets.com/how-to-build-vector-search-from-scratch-in-python)

----


