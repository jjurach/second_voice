Create a project plan to add support for Cline CLI

Find all files which reference aider:
```
git ls-files | xargs grep -li aider
```

Then, everywhere the Aider product is mentioned or everywhere a provider module
exists for it, etc., do the same for Cline-CLI. When are listing out supported
providers, we need to do all the things so we can say we support cline, too.
