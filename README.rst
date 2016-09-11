##################
Graphics Chip Plot
##################

The graphics card manufactured by AMD and NVIDIA have certain consumer names
like “GeForce GTX 960” or “Radeon R9 380”. These follow some loose scheme. The
first digit is a *series*, the remaining digits are what I call a *level*.
There 9 is awesome, 1 is not so good. Taking a trailing zero, one has a level
from 10 to 90 or perhaps 95.

Then on the other hand, the chips used in the graphics card are more or less
decoupled from this. With AMD, the 380 has the same chip as the 285, it seems
to be a mere relabeling. NVIDIA has the 9800 GTX which has the same chip as the
GTS 250.

I wondered how the various chips travel through the graphics cards; how the
technical names coincide with the marketing names.

First I need a way to normalize the marketing names. With a bunch of regular
expressions I could get those down to *epoch*, *series*, *level* and *mobile*.
Since NVIDIA has an “9800 GTX” and a “GTX 980” I use the same “epoch” that are
used in Linux distributions when the version numbering scheme has changed. With
that I could make a simple normalization:

- “9800 GTX” becomes ``(1, 9, 80, False)``
- “GTX 980” becomes ``(2, 9, 80, False)``
- ”GTX 1080” becomes ``(3, 0, 80, False)``

With this, I could add a new number which simply is ``epoch * 10 + series``.
This would be the name for the card if the manufacturer would have just had one
more leading digit.

Wikipedia has nice detailed tables which contain the marketing names and the
chips that are used in them. Those are HTML and probably really hard to parse.
Parsing the Mediawiki syntax might have been a bit easier but it would still be
cumbersome. Luckily the Noveau developers have a list__ which is easier to
parse. With a bit of Python I could actually parse most of it.

__ https://nouveau.freedesktop.org/wiki/CodeNames/
