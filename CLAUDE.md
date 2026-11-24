# ComicAgent

This repo makes the **ChandRush** maths comic. All production work happens in `Tasks/`.

For any request about comic pages, chapters (including "I added chapter 4" or a new manuscript version: that is the chapter-setup agent), samples, backgrounds, panel art, fixes, colours or feedback (e.g. "generate page 69", "make a text heavy sample"):
you are the **master agent**. Read `Tasks/CLAUDE.md` once if it is not already in your context, print your part of `Tasks/LESSONS.md` with the command at its top (role `master`), then load the `comic-master` skill and follow it. Work from `Tasks/`; paths in those files are relative to it.

Subagents: `Tasks/CLAUDE.md` is auto-loaded for you; never re-read it. Read only your own `LESSONS.md` sections.

Never make an immediate (non-batch) image call unless the user says so in this conversation. Never edit `Tasks/Reference/` or `Tasks/Charactors/`.
