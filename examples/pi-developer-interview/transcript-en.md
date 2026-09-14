# Pi Developer Interview — English Transcript

Source: https://x.com/pidotdev/status/2099045420496486415

This is an AI-assisted transcript. Some proper nouns or model names may still be misrecognized.

[00:00] **Mario:** Aber du darfst nicht laut sein.

[00:01] **Child:** Leise mit den Schwertern spielen.

[00:03] **Mario:** Leise mit den Schwertern spielen.

[00:08] **Mario:** Code is less important than it used to be, obviously. But the question is, how good can your agent deal with a shit ton of code given its limitations with respect to context window?

[00:20] **Mario:** So the agent is ultimately hurting itself by generating too much code.

[00:26] **Mario:** Is the code as important as it used to be? No, definitely not. Um, but I would say that it is still important in... Astra is cool and all, just like Fable, but they're still slop machines. And I would say there is a lot of code where you don't need to know what it does and how it works. Um, but there's also a lot of very important infrastructure code where you still want to know what it does.

[00:49] **Mario:** Um, I think ultimately it comes down to control. I personally like controlling interfaces and types, and as long as I have control of that, the LLM is kind of limited in how much damage it can do.

[01:02] **Mario:** Yes, the models can shit out immense amounts of code now, but by doing so, they're hurting themselves because ultimately they still have a limited context window and, um, if it doesn't fit, you get more slop.

[01:13] **Armin:** What I found interesting with the Astra release is that I for the first time felt like less and less desire to actually look at the code that it produces because it's so hard to see. And not, I mean, it's hard to look at. It is, it is incredibly compressed in situations where it shouldn't be, even when it actually uses code generation for writing code, but it's particularly unreadable when it uses code to call tools.

[01:39] **Armin:** So like actually following along what it's doing is also getting harder and harder just by how, how it writes code. And, and I think like to Mario's point, like it actually does get, it, during the the training process, it probably gets rewarded for token efficiency.

[01:55] **Armin:** But as a result of this token efficiency, it is hard to read. And there's a, there's a tension, I think, sort of forming where, um, I think even if you get the interfaces right and everything else, like if I look at an Astra-produced code, I feel an urge to do code formatting.

[02:13] **Armin:** Which I didn't feel for a very, very long time. I basically haven't used code formatters at all because I felt like the LLM is going to follow along the style of the code that's already there. And now it doesn't.

[02:23] **Armin:** Yeah, and it's, it is kind of odd. It is, it is really odd and I don't know where it's going. Um, but I'm a little bit feeling like this might become more of a thing now, and I don't know how I feel about this.

[02:35] **Mario:** You said something earlier which I, I thought was interesting. As the models are trained to not only be coding agents, but also like personal, open-claw-like assistants, it stands to reason that the training might contain, uh, traces or, or things like, just create whatever the fucking code you want to create, as long as it does the thing the user asked for. And the user is a non-technical user and the user doesn't write production systems, but just tiny little things like, build me a, an daily news brief website or something, or a Minecraft clone or anything.

[03:09] **Mario:** So, so if the models are now being trained to produce slop code just to, to make their users happy, which is totally fine, then we'll have a detrimental effect on using these models for production software. So, yeah.

[03:22] **Armin:** So, what I found quite interesting was, so I, I noticed like, with, like, as you sort of look into the code that it produces, like in tests, in shaders, in embedded JavaScript, you can clearly notice that it's way worse than in the regular code that it writes. So I, I wrote in a blog post, like, I think it's like one step removed from regular code, it sort of starts falling into this pattern of, of like really highly compressed things.

[03:45] **Armin:** But then I was like, okay, maybe this just happens to me. So I asked a bunch of people on Twitter like, "Hey, if you build like an Astra game over the weekend and it worked for you, just show me the code." And there were two people who replied like, "Oh yeah, it wasn't so bad." And I just opened the code and it was really, really bad. And, and then it was, I think both of them replied, "Yeah, it's probably not nice."

[04:05] **Armin:** The thing is like, we're, like, we don't really expect it to actually write code this bad, I think. It's, like, I, I, I got fully trusted that the models are at least certain level of like passing bar, and it feels a little bit like it violated this now. I don't know. This is, it definitely feels like a shift.

[04:24] **Mario:** Yeah, I just, just yesterday I, I did some work on a, an old C, C++ codebase in Spine. I switched back to 5.6 Sol, um, because Astra just couldn't write any sensible kind of code. It's, it's very weird. It's very, very weird. I, I, I, I blame personal assistants.

[04:46] **Armin:** One thought that I had, uh, was that if you have the idea, at least in theory, that you don't have to at all consider the code because like the test coverage is going to guarantee you that the code works perfectly, then even if you have like 100% branch coverage, which I don't think is likely, do you, do you read or cover all the possible inputs to that function?

[05:10] **Armin:** And one of the things that I noticed like with, with this is that because it compresses the code so much, I, when I just look at the diff that it does, I, I don't have any confidence that, like, I could even without asking the LLM tell you if the tests are sufficient.

[05:31] **Armin:** I, I'm, I'm really struggling with this, with this whole thing, because like, if the code is too unreadable, then, and I'm not saying like it's completely unreadable, but like, it, it becomes so that, that you're one step further away from it, and then you rely more on like, okay, but there are tests and the tests pass and I can still navigate in my slop game, and so surely the whole thing must be working. But it's like, it becomes so much harder to understand if, if you have, if you feel repulsed looking at the code.

[05:59] **Mario:** So, um, at that point, the tests also just become performative, right? It, they just give you a good feeling of, there are tests. I don't fucking know what they do and if they actually cover what we need to cover in the tests, but they exist. And that's why I feel good. It's, it's very emotion-based, all of it.

[06:18] **Mario:** Yeah. But, but if they produce code that is unreadable, then you have even less incentive of checking whether the code they produced makes any kind of fucking sense. So, it feels like we're getting pushed to being removed from the code.

[06:35] **Armin:** What if you use something like Astra, which is clearly like trained to succeed, but you, we use it only for the tool calls. Like you don't use it for the writing. So like whenever it tries to write some code, you're like, "Oh, you stop. Some agent, I don't know, something else you implement now."

[06:56] **Armin:** Um, because I, I really feel like there's a tension in the training process. There's like, either this, this is, this is really good and we, we should like this because, um, I don't know, software engineering is solved and it's just the bug fixes that we have to deal with now. And so we don't look at the code anymore, so it doesn't matter how it looks, and it's like really purely optimized for the LLM. Or these models are actually only behaving this way because they're being trained to do other things, particularly really good tool calling using code.

[07:22] **Armin:** And so there's a tension in the training process, and you should actually use a different model that's being trained to be an expert software engineer. Um, and I really don't know what the question, the answer is here because, like, I, it's not like you go to OpenAI page and says like, "Yeah, do that."

[07:40] **Mario:** No, but, but maybe that's like a, a model capacity issue now. Like, as they try to accommodate more and more use cases or vertical slices of specific industries, obviously the model needs to know about how to operate within these environments. But that will ultimately mean that there are less parameters available to the things they used to be good for, like, like software engineering.

[08:05] **Mario:** So maybe we are hitting that now. Maybe, maybe it's the, you're trying to accommodate as many industries as possible, so your industry, specifically the software industry, is now suffering because there's not enough parameters left for your specific industry. I don't know.

[08:22] **Armin:** The token spent on engineering went up in a certain way, so you could see like month by month what that was, but none of the top-line numbers moved up at all, um, in a way that was correlatable to this. But obviously the number of commits went up, the number of like other things that you could measure went up.

[08:42] **Armin:** Um, and so it went from like an insignificant part of like the expenditure of the company to a really meaningful part of the expenditure of the company. And, and it might just be that, that, that we haven't figured out yet how to make that work, or, um, like the, like what is being produced actually isn't that much more meaningful overall.

[09:03] **Armin:** And so because now everybody, like as an example, like, the, the, the, the baseline expectation that we have now for a piece of software is that it does more. So you need now to compete with everybody else who's in your space as well. So like, of course your thing now should have a chatbot in it. Of course there should be, I don't know, like the UI should behave in a certain way that was previously not necessary.

[09:26] **Armin:** Like more people now build mobile apps, I think, than they did before, just because it became easier. So maybe this is sort of, it's like a really weird form of like, we are required to build more, but like the, the amount of consumers is still the same, so, so it just has become more expensive to do software engineering. I don't know if that's the answer. Um...

[09:47] **Mario:** Yeah, I mean, I guess it's hard to go to, to, to measure at the moment just because of the economic turmoil, economic turmoil overall with, with oil being up and so on and so forth. So just taking GDP is probably a bad, bad idea. But if you look at individual companies, I don't see them producing more meaningful features for the users, if you're looking at software companies. I, I just don't see it. Like, can you name a single, single software or SaaS product that has meaningfully changed in the past 12 months?

[10:17] **Armin:** I mean, I think in the AI space, you see that a little bit, like...

[10:20] **Mario:** Yeah, but then the question is, who is using all of that stuff from the AI space?

[10:23] **Armin:** Yeah. I was, I found like iOS 27 to be an interesting proof point here because like, clearly there should be more people in Apple using AI tools. Like, I, I heard from people at Apple that there is like plenty amount of like AI-supported software engineering going on. But like from iOS 26 to 27, I felt like it was the most boring iOS release. Like, if anything, it's sort of they push against this in a way.

[10:55] **Mario:** I mean, I, I, I don't think that's bad, actually. I, I don't want a Cambrian, a Cambrian explosion of new features and, and the Homer Simpson's car, right? But then I must wonder, does the additional resources that we have through agentic coding, um, just ensure that whatever you push out has higher quality?

[11:12] **Mario:** I, I would like to think so. I, I personally would like to use agents in a way where I can say, okay, my, my velocity is kind of the same, but everything I release is actually of higher quality, even if the quantity stays kind of the same. That, that would be the goal for me, uh, when using agentic engineering tools.

[11:30] **Mario:** But I'm not sure if we're seeing that either, if you look at companies with their 99.9s going into the 99.99 territory. So...

[11:40] **Armin:** I think where you, where you see it a little bit in terms of like quality, presumably, like depending on how you look at this, is that software should become more secure because we are having to work on all of the security reports. Right? And I think like...

[11:54] **Mario:** Well, that's not happening. I can tell you from first-hand experience. It's definitely not more secure.

[12:01] **Armin:** But it's, it's like, it's also riskier to be, um, be on the internet now with software. Um, one, one of, uh, one of our colleagues, like he's, he's a little bit more now worried about like smart contracts and, and crypto wallets just because they have become such attractive targets for automated, um, security research.

[12:24] **Armin:** Um, but I mean, there are definitely certain areas where like, on, on, in, on average, like there should be more fixes going into, like curl is a good example, or like other software that is really, really old. So they got a lot more valid security reports, so they fixed them. So like, in general, curl is, a curl is probably safer now than it ever was, and it doesn't slop a ton of new features into it.

[12:50] **Armin:** But also the, the risk profile just went up simultaneously because of the same thing that...

[12:54] **Mario:** And that is the problem, because the security patches still take humans to verify and apply. But finding the security vulnerabilities is now like 100x easier. I, I, I literally just had my clanker kind of try to break the DRM of one of my old products and it just did it. It just, like, without inter, intervention from my end. So, yeah, interesting times.
