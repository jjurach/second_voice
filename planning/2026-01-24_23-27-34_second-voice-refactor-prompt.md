
We want to create a polished, professional python project for publishing around
the script in src/ and the demo script in scripts/. These scripts have been
seen to work, but we want to refactor some code and add some features, etc.

You are an expert planner and prompt writer. You are constructing one or more
detailed plans which will be executed after human review.

"Second Voice" is a cli which starts recording and continues recording until it
is Ctrl-c interrupted. It is a python application which runs on the macbook or
chromebook, etc. which is an under-powered "satellite" of a beefy Ubuntu server
running a faster-whisper service (perhaps through a localhost SSH tunnel).

Generally, this tool is intended to interoperate with editors like Obsidian in the
flow of writing meta-documents to an inbox, where one or more readers are
expected to consume and transform into other documents within the inbox or
other directories -- especially to generate "spec" files which in turn generate
project plans -- both operations of which generate changes.

Consider all of this information from agentic conversations. Include these
features in the plan you are creating.

@docs/info1.md
@docs/info2.md
@docs/info3.md
@docs/info4.md
@docs/info5.md

Prepare for the removal of these documents by creating one or more documents in
docs/ which describes this information. For example docs/gui-design.md. Write
these documents now so as to reduce the size of the plan as the plan will now
reference these docs/ files.

# Mention this in README.md
```
brew install python-tk
```

# Second Voice Requirements:

- create typical but professional python project
  - require the use of venv for requirements.txt
  - give it MIT license
  - arrange for second_voice and demo_second_voice to be installed from
    pyproject.toml

- separate the functional logic into one or more reusable modules.
- leave the cli processing logic in the src/cli or according to typical developer tastes on this topic
  - add --verbose and --debug switches to show detailed information about the URLs, payloads, responses, timings.
  - create new cli options for all the values which are hard-coded in the cli. arrange for the hard-coded values to be the default values.
- create at least one pytest test for the refactored functional logic
- create a demo script in scripts/ which can take input .wav file and play that through our endpoint
  - use samples/test.wav from the demo script to provide the computed value
  - add --verbose and --debug switches to show detailed information about the URLs, payloads, responses, timings.
- create README.md in a professional python project style

- include final task of running the unit tests one more time, and then running the demo script one more time.

Instruction:
- create a detailed checklist plan at tmp/plan01.md to implement the above product.
- if that plan already exists, continue implementing the plan
- update the plan file to mark tasks complete as you complete them.
- instruct the plan not to consider this done until test and demo run cleanly.

Just create the project plan. Do not implement it.
