Let's iterate on system-prompts again.

I want to make the "logs-first" workflow and details related dev_notes to be
optional, and I want different projects to be able to enable and disable these
features for different prompts.

For some projects like this current project, it is small and is already setup
to continue iterating on this workflow, so for a project like this, i want
implicit mention of a "project plan" to trigger these logs-first workflow
features.

For other projects which are much larger, concepts like "definition of done"
are less well-defined, and there are many other developers who are not familiar
and who would not want to engage in this workflow.

# implementation suggestion:

I think we can effect this like this:
- add docs/system-prompts/workflows/logs-first.md
  - (or i don't like this name -- maybe there is a different, better name for our spec->project_plan->changes pattern?).
- for projects which want this workflow expectation to be implicit, we have more and better instructions in AGENTS.md which automatically wires all those instructions into the prompt.
- for projects where this is optional, the developer can add @docs/system-prompts/workflows/logs-first.md to their prompt (or is there a shorter hook easier to type? -- maybe installed/maintained by bootstrap.py?

Research with google search to look for some ideas what other developers are doing to trigger alternative, cross-agentic workflows.

Create an initial plan.

Then summarize the plan to me and ask me clarifying questions. 
