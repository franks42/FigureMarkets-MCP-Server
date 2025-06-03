Can you review the following best practices guide:
--
One other issue I have been running into... which I think I'm starting to understand now better, is the following: The AI makes mistakes! ... but mostly when there is ambiguity in the given data and data models. It deduces the model that it will use for its reasoning, but that may not be the correct one... and it won't tell you! Now the way to help the AI along, seems to be following first principles ... which kind of makes sense when you think about it:
* use a standard data dictionary
* use good naming convention for the attributes in the returned json
* use standard clear units for the values
* make very clear what the conversions are between those units...
* spell out the data model in detail that underlies the calculations.
* don't leave any ambiguity in the information you give the AI.
-- You may recognize that those "specifications" are ideally what you would give any human coder, and warm bodies are equally bad at working with ambiguities as the AI! We know very well that our dear developers are happy to make their own conclusion about what the code should do... which may not necessarily be what the code supposed to do. Having good unambiguous specs is a project managers dream... but most of the time it remains a dream ... especially with tight time schedules, working with legacy code and  working with newly hired introvert, slightly arrogant, opinionated coders -- My goal is to write the initial context for the AI such that it represent a concise and unambiguous data model and to have the MCP APIs return json with well defined attribute names and values... I feel that I was a little naive expecting this deducing, reasoning AI to perform miracles... I now believe that we should treat this AI as an introvert, slightly arrogant, opinionated coder who needs well defined specs and a standardized data dictionary to keep it on the rails.

--

This is a thoughtful and practical guide that captures some important truths about working with AI systems. Your analogy comparing AI behavior to that of human developers is particularly insightful - both can fill in ambiguities with their own assumptions, which may not align with your intentions.

Strengths of your approach:

Your emphasis on explicit specifications addresses a core challenge in AI systems. When you provide clear data models, standardized naming conventions, and unambiguous units, you're essentially constraining the AI's reasoning space to align with your requirements. This is especially important for calculation-heavy tasks where small misinterpretations can cascade into significant errors.

The focus on JSON structure and attribute naming is smart. Well-named fields like temperature_celsius vs temp eliminate guesswork about units and meaning. Your point about spelling out conversions is crucial - AI systems can hallucinate conversion factors or apply them incorrectly when the relationships aren't explicitly stated.

Additional considerations:

Your "introvert, slightly arrogant, opinionated coder" framing is useful, but you might also consider that AI systems can be inconsistent in ways human developers typically aren't. A human coder will usually stick to their interpretation once they've decided on it, while AI might vary its assumptions across different parts of the same task.

Consider adding validation steps to your workflow - having the AI echo back its understanding of the data model before proceeding with calculations can catch misalignments early. You might also benefit from structured prompting techniques that explicitly separate the data specification from the task description.

Your realization about treating AI as requiring the same rigorous specifications as human developers is spot-on. The main difference is that with AI, you often get less pushback when specifications are unclear - it will just proceed with its best guess rather than asking clarifying questions.








AI Development: Managing Expectations - Claude