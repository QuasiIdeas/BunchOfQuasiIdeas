  + - - - + - + - -
  + - + - + copyright by Vladimir Baranov  <br>
  + - + - + email: vsbaranov83@gmail.com  <br>

```
                            )            (
                           /(   (\___/)  )\
                          ( #)  \ ('')| ( #
                           ||___c\  > '__||
                           ||**** ),_/ **'|
                     .__   |'* ___| |___*'|
                      \_\  |' (    ~   ,)'|
                       ((  |' /(.  '  .)\ |
                        \\_|_/ <_ _____> \______________
                         /   '-, \   / ,-'      ______  \
                b'ger   /      (//   \\)     __/     /   \
                                            './_____/
```              
  
| Activity | Reward |
|---|---|
|Punishment for not inovating  |-80 |
|Punishment for trying inovating but failing | -5 |
| Reward for successful inovation | 100000 |

Protocol #002 describes <br>
"vccl - Video content creation language <br>
Vladimir Baranov vsbaranov83@gmail.com <br>
Document creation date: 02 September 2021

* Formal language for constructing video content based on text, taking into account the capabilities of GPT-3 systems (like Codex)
* See [document](https://github.com/Kvazikot/VideoProjects/blob/master/Video_content_creation_Protocol_001_eng.MD) describing software stack that need to be develop
* The Heisenberg Uncertainty Principle works in our favor when you want to change human history by changing just one byte of your video content description
* Provide the ability to schedule a convenient time for creative work, leaving the entire routine to the machine. But also i want to provide some fredom in creativity expression to the machine
* Probably we cant teach AI to some not trivial level of estetics by providing feeed back in the form of likes on video with automated content creation
* Hard-coded rules at the lowest level may include chunks of shader code with several control parametres (uniforms)
* In the end stages of this project one could create simple 3d scene with animation based only on text description from the Unity Assets free stuff. The level of details of such scenes is far less important rather then diversity of end result (uploadable video).
* The ultimate goal of the project may be to make a cool toy for the kids in minecraft like game

The language vccl is a form of [Embedded Generalized Markup Language](https://ru.wikipedia.org/wiki/Generalized_Markup_Language)

# Machine Fredom Rules (MFR)
Tag src that defines urls in MFR can be defined more broadly 
as: 
```
[maninblack1]: "Memory eraser from the man in black movie scene" 
```
MFR is used when you dont know exact future context of 
the paragraph or basicaly dont want to define detailed rules i.e. functions with fixed parametres.
It allows to use code-generator like Codex for example trained on vccl rules 
to generate hard-coded version of the script including neccesary security levels 
Let the machine do the boring job. 
keywords are marked with * * is used in ML algorithm 
for more precise defining the context (italic in markdown rendered page)

```
:fly_bird_fly_tag
No exact date is known when *Wheeler* came up with the idea 
for the quantum eraser experiment. 
Now I'm not talking about a literal scenario when 
naked terminators leave the time machine.
:eol.
```

# Pauses
You can define pauses beetween chunks of narrated text as:
Pauses will be filled with any random stuff related to the topic.
```
[pause][10-20 sec]
```


# Hard-coded Rules
```
Tag vsrc defines urls or file paths. 
:vsrc 
[label]: [http://video-hosting/video-id] 
:eol. 
```

Tag vfx description
```
videocube = "Take 3d rimitive cube and make video on textures. "
```

Tag orbit movement description
```
orbit = "Move camera by orbit around cube. And go out of the galaxy to the blackhole. That is the wrong tag  "
```

<00:00:50><src wheeler_1><vfx zoom, fade_out(time_sec=0.2),para_text(color=#00FF0022)> <br>
In John Wheeler's famous double slit thought experiment ...


```
<00:00:50><list img1,img2,img3><list(map(trace(lambda x: x*2), range(3)))><stack hstack><vfx slideshow> 
In John Wheeler's famous double slit thought experiment ...

<00:01:06> <src wheeler_1,terminator_nude,nanobot,big_bang1><vfx videocube,para_text> No exact date is known 
when Wheeler came up with the idea for the quantum eraser experiment. 
Now I'm not talking about a literal scenario when naked terminators leave the time machine.
This is done for the fun of the audience, as well as the batteries in the "matrix", because Hollywood films are designed for a mass audience. I am talking about the possibilities offered by quantum theory to erase information in the future, to influence the past no matter how distant. Delta t could be 5 milliseconds to detect a cancer cell, or it could be the age at which the universe was born.

[pause] [10-20 sec]

<00:02:35> What is known for sure is that it was only in the 1980s that the delayed choice experiment was implemented. At the University of Maryland, Carroll Alley, Oleg Jakubowicz, and William Wickes — on a laboratory bench. Strange coincidence - The Terminator movie entered in 1984.

[pause] [10-20 sec]
```


# Special tags for embed vccl into a naration text of the video
Sorces i.e. urls of the videos is defined in the head of the document before the main text and use MarkDown bracket tags <br>

# 3 Levels of security. Syntatic freedom. Allowed Tokens
If we assume to embed some python syntax into the vccl we need to narrow the scope of possible programs
We can define map of allowed functions or modules involved only in building video content(3d rendering, vfx, borowing video from youtube) 
or more general tokens. 
Is also neccesary to limit porn content to a cultural norms of randomly selected society in random selected epoch

allowed_python_tokens:= for range while lambda map list set str




























