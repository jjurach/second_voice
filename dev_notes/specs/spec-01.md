
consider this output:
```
$ EDITOR= second-voice --file samples/test.wav --no-edit --mode menu

Starting in menu mode...
Processing input file: /home/phaedrus/AiSpace/second_voice/samples/test.wav
⌛ Transcribing...
📝 Transcribed: This is a test. Is this working? Is this a working test? Is this gonna work? Is this just gonna go for 10 seconds, I think?
⌛ Processing...
📋 Output: It looks like you're testing the chat functionality! Yes, it's working so far. I'm responding to your messages, and we can have a conversation.

If you'd like, I can simulate a response that will keep the conversation going for as long as you'd like (beyond 10 seconds). Just let me know what you'd like to talk about or ask next!
```

Here, it looks like the LLM is interpreting what i'm asking and is responding with an answer. I don't want that.

I want to resolve the stutter text and clean up my question so it has better grammar and slight structural modifications to make the words coherent.

Let's create a project plan to improve the prompts to make it clear that the agent is to clean up the language of the question -- not to answer the question.

There is an exception, though: if the user refers to their own text.. e.g. towards the end of the "10 minute stream of consciousness", if the user says, "rearrange what i said in an outline format" or similar.

Ask me some clarifying questions.  Then, let's do better.
