# Claude Base

This is my Claude-Code base repository for central housekeeping of my
development rules. Feel free to suggest additions by filing issues or pull
request.

## Expected workflow

There is a dedicated (virtual) machine running a clanker or a bunch of them.
That machine should not have any write access anywhere outside itself, and
should be regularly backed up.

The operator (myself) logs into the virtual machine whenever handy, pulls the
git locally, does code review and merges, and pushes into public repo.

## Initialization

1. Fork this project
2. Clone your project into your clanker enclosure
3. Setup needed tools: `./clanker-setup`
```
