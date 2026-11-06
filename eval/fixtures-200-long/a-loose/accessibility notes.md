accessibility notes

check contrast
alt text on every image
focus states

general approach

the idea underneath all of this is that access isn't a layer you add at the end. when it gets bolted on late it feels bolted on, and it costs way more effort to retrofit than to build in while the shapes are still loose. so while sketching, the question worth asking over and over is: who might be using this in a way i haven't pictured?

people turn up in all sorts of situations. lasting differences, sure, but also a bruised wrist, a cracked screen, bright glare on a train, a baby asleep in the crook of an arm, a patchy connection, a tired brain at the end of a long shift. designing for the edges usually makes the middle better too, which is a handy thing to remember when a client pushes back.

things to keep in mind

- readable type beats clever type. a quirky display face can be lovely for a headline, but body copy should be calm and generous, with room between lines and between paragraphs.
- let people resize text without the layout collapsing. test by pushing the browser settings around, not just by trusting the design file.
- don't rely on color alone to say something. if a state is shown by hue, add a shape, a label, or a pattern as well.
- motion can make people feel physically unwell. keep animation gentle, give it a purpose, and respect the system setting that asks for less movement.
- links should say where they go. "click here" tells nobody anything, especially when links get read out as a list.
- headings are navigation, not decoration. choose them for structure, then style them afterward.
- forms deserve extra love. visible labels rather than placeholder hints that vanish as soon as you type. error messages that say what went wrong and how to fix it, in plain words, right next to the field that caused it.
- hit areas for buttons and links should be generous. small targets are miserable on a small screen and worse with shaky hands.
- anything with audio needs a way to follow along without sound. captions and transcripts are the obvious route.
- nothing should start playing by itself. surprise noise is hostile.
- if a page expires while a person is reading or typing, that's a trap. think about how to warn them and how to let them recover what they entered.
- icons without labels are guessing games. icon-only buttons need a name that software can read, and sighted people often benefit from a visible word too.
- tooltips that only appear on hover are invisible to touch and to people who can't point precisely.

how the work goes

start from plain structure before any styling. if the page makes sense as a bare outline, it'll make sense to software that reads it aloud, and it'll probably make sense to a stressed human too.

read the layout top to bottom as if you could only hear it. does the order still hold up? sometimes the visual arrangement and the underlying order drift apart, and nobody notices until a person using a screen reader runs into the mess.

try the thing with the trackpad unplugged. try it zoomed way in. try it squinting, try it with the brightness turned down low. cheap experiments, surprising findings.

keep a running list of things that tripped me up on other people's sites. real annoyances are a better teacher than any guideline document.

guidelines are a floor, not a ceiling. passing an automated checker only catches the easy stuff, and a page can pass everything and still be exhausting to use.

involve real people when possible. no simulation replaces a person who relies on assistive technology telling you what feels awkward and why.

when a request would hurt usability, explain it in terms of who gets shut out and what that does to the project, not as a moral lecture. people hear practical reasons more easily than sermons.

put the reasoning behind choices into words so future me doesn't undo them by accident, and so a collaborator can understand why something looks plainer than expected.

language and voice

plain language is part of this. short words, active voice, a line that carries an idea and then stops. avoid jargon unless the audience truly expects it. dense legalese in a cookie banner is its own kind of barrier.

declare the page language in the markup so voice software pronounces things properly. be careful with abbreviations, and spell out anything that isn't obvious when it appears early on.

error and success messages should sound like a calm, friendly person, not a machine scolding you. blame the system, not the user.

empty states, loading states, and failure states are part of the design too. they're where people feel most lost, so they deserve real thought.

mindset

try not to treat any of this as a chore. the moment it becomes a box-ticking exercise the quality drops, because the point is empathy, not compliance. approach it like any other craft problem: constraints that sharpen the work.

assume people are smarter than the interface gives them credit for, and also that they're tired. both are true at the same time. clarity is a form of respect.

expect to get things wrong. every project reveals a gap in what i thought i understood, and that's fine as long as the gap gets written down and used. nobody has a complete picture, and the people affected know more than any designer does.

be wary of overlays and quick-fix widgets that promise to make a site accessible automatically. they rarely help and sometimes get in the way of the tools people already use.

open-ended ideas

- a little checklist card that lives next to the sketchbook, put in my own words rather than copied from a standards document, so it actually gets looked at.
- a library of patterns that are already well behaved: a disclosure panel, a menu, a dialog, a tab set. start from those rather than reinventing them every time.
- a short plain-language statement on the studio site about how the work gets made accessible and how to flag a problem. worth thinking about what voice it should have so it doesn't read like a legal shield.
- a stress-test session: pick a finished project and use it badly on purpose. tired, distracted, with only a thumb, in harsh light, on a bad connection. see what survives.
- what would a calmer, quieter version of an interface look like? reduced density, a reading mode, a low-stimulation theme. maybe those are good for everybody, not just for people who ask.
- print and physical work deserve the same questions. signage, packaging, and printed forms are met by people with limited vision or limited reach, and nobody can pinch-zoom a poster.
- collect short stories about moments where a design choice made life easier for a particular person. could be a nice way to explain the value to clients without leaning on statistics.
- stay curious about how people customize their devices: bigger text, inverted displays, voice control, switch devices, custom style rules. their setups are clever, and designs should bend with them instead of fighting them.
- explore how to prototype with real constraints earlier, so the awkward discoveries come while changes are still cheap.
- wonder how much of good design is simply kindness plus craft.

handoff and care

when work leaves the studio, the notes about structure, labels, and behavior should travel with it. a beautiful design that gets rebuilt carelessly loses all of this, so the documentation matters nearly as much as the visuals. leave comments for the next developer in plain language, and explain what the odd-looking choices are protecting.

after launch, things drift. new material gets added by people who weren't in the room, and good habits fade. worth thinking about a gentle guide for whoever maintains the site, written kindly, with examples of what good looks like rather than a list of prohibitions.
