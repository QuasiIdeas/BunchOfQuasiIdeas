This project is licensed under the terms of the GNU General Public License v3.0

  + - - - + - + - -
  + - + - + copyright by Vladimir Baranov (Kvazikot)  <br>
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
## About Useful Clicker
The UC program is intended for programming user actions.
For example, to automatically search for materials in youtube and download certain videos.
The program has a built-in computer vision functionality, i.e. it can identify the buttons on the screen by analyzing the pixels in the image.
In this sense, it works similar to how the retina of an animal's eye works.
The buttons are highlighted in green in the style of augmented reality.

## New concept for Useful Clicker (3/28/2022)
The program must recognize the context. Those. which window is currently on the screen, which buttons are on the screen.
It circles all the buttons in green, and the button to be clicked in red.
He also signs the sequence number of the action next to the button.
All this can be arranged in a full-screen semi-transparent widget.
The "Next Frame" and "Previous Frame" buttons at the top of the screen.
That is, the clicker also works in the clicker programming mode. To return the previous window e.g.
## The idea for an astronomical number of screenshots for reverse engineering human software (came from Marvell comics)
We need to create an astronomical number of screenshots for all sorts of programs and operating systems.
Each dialog box is unique to the program. Therefore, the clicker will be oriented towards reverse engineering of traditional software.
Soon, according to the idea of ​​Elon Musk, all traditional software i.e. the expertise of some engineer will replace neural networks.
But we need to prepare a description of the functions of every program on Earth that has ever existed.
So that the future AGI can use these compiled programs for its calculations.
So that he does not need to invent the wheel, roughly speaking
Since AGI thinks orders of magnitude faster than humans, it will be able to use human software
in such interesting combinations that people never even dreamed of. But this information should be available.
In order not to waste time on reverse engineering.
Perhaps at some stage AGI will be able to explore various software written by people.
By disassembling it.
To do this, I provided the Function Description window, which a person must fill out.
  
This idea is explained in more detail in the next video.
https://youtu.be/BYM5G5CIgS8

## Reformulation of the problem (5/6/2022) . Few new thoughts. 
Check UsefulClicker on noisy data. 
This is related to interactive mode there clicker is mirrors user event but with a small delay.
* 1. Try to predic there user is about to click next second or more. The possible mathematical models can be: inverse reinforcment learnong, CNN 
* 2. MicroRecorder suppose to do several things 
  * a) Record mouse
  * b) Record voice and extract text from audio signal
  * c) Record keyboard events
  * d) Record screen with interactive button recognition
* 3. Find youtube videos with tutorials on most popular programs for solving common problems on computer like Microsof Excel
* 4. Try to replay tutrial based only on video data from youtube.
* 5. Develop a plugin that invoke some video search for a particular tutorial. Maybe embed youtube search in UC interface.
* 6. You probably need connect some decentralised blockchain based database of tutorials and make team working support (like Discord)

The UsefulClicker in its development stage project right at the point of collecting vast amount of data.
So since this is a toy project and it respects ai aligment problem. 
I have to write some security requerments at this early stage.
Inteligence can be a harmful weapon.
Next stage is actualy has more teoretical than practical sense at this point.


## Compression
It is necessary to make such programs for the clicker so that they take up a minimum of bytes and do a maximum of useful work. It is possible to add additional information so that it can be restored in case of errors in the communication channel. Here you can compress the information using not only artificial neural networks, but also the slightly forgotten information theory of Claude Shannon's [1]. 

## Short UC code
It neccessary to implement short one string encoding of clicker instructins.
For the small band-width communicatioons like brain net.
```  
<!-- example of short program for Useful Clicker
xy,140:122,ctrl+f,"banana republic gdp",enter,cr,56,cb,"next"
```  
xyl,140:122 - mouse click, left button in point with coordinates (140,120) <br/>
cr,56 - click rectangle object on the page with number #56 <br/>
cb,"next" - click "next" button  <br/>
  
# Macro recording with code generation of optimal xml code,
  * input: for which mouse trajectory and keyboard events.  
  * output: minimal xml code, preferably with human-readable content
  ```
  <window template="notepad_template.png"/>
  <menuclick> File -> Open </menuclick>
  <inputline>readme.txt</inputline>
  ```
  
# XML document sheme for Useful Clicker 0.91. Sort of meta language (Language of languages)
  
```  
<!--         INCLUDE DERECTIVE          -->
<include> sheme1.xml </include>
<include> sheme2.xml </include>

<!--         CODE BLOCK(PYTHON, C++, etc)          -->
<code source_name="block.py" lang="python" >
  import random
  print( random.randint(0, 13) )
</code> 

<!--         SHELL CODE BLOCK(bash, cmd etc)          -->
<shell name="cmd" bg="1" showConsole="1"> start / B date </shell>
 
 <!--         RUN PYTHON FUNCTION          -->
 <py_call name="pyFunctionName($(arg1))"/>  
 
 <!--         FUNCTION CALL           -->
 <call name="SetUrl" arg0="https://www.hh.ru" comment="set hh url" />
 
 <!--         FUNCTION DEFINITION           >
 <!-- every function is inialised global python variables arg0, arg1 etc  --> 
  
  <func name="Type test 2">
   <shell bg="1" showConsole="1" hotkey="ctrl + a" cmd="notepad.exe" comment="run notepad"/>
   <type mode="copy_paste" text="This is an example of text that was generated by UsefulClicker today. " />
  </func>
 
 
  <func name="Change font">
   <click button="left" x="1531" y="661" />
   <hotkey hotkey="alt+o"/>
   <hotkey keysequence="f" delay_ms="100"/>
   <hotkey hotkey="alt+s" delay_fixed="500"/>
   <type text="48" />
   <hotkey keysequence="enter" delay_ms="100"/>
   </func>
  
  <func name="Post Twit">
    <click button="left" x="1700" y="416" comment="click in chrome window" />
    <hotkey hotkey="F6"/>
    <type text="https://twitter.com/" />
    <hotkey keysequence="enter" delay_ms="1000"/>
    <clickimg targetImg="$(UsefulClicker)/images/18.10.45.400.png" button="left" delay_fixed="1000"> </clickimg>
    <type text="This is an example of the text generated by UsefulClicker today." delay_fixed="1000"/>
    <clickimg targetImg="$(UsefulClicker)/images/18.01.05.902.png" button="left"> </clickimg>
    <hotkey keysequence="enter" delay_ms="1000"/>
  </func>
  
  <func name="PirateBay test">
  <foreach list="Thrillers_beetwen_1979-1989" do="PirateBay_spider"/>
  <shell cmd="notepad.exe tmp.txt"/>
 </func>
 
 <func name="Generators test">
 <gen list="INTEGERS" f="i+1" range="1:10:1"/>
 <check INTEGERS="1 2 3 4 5 6 7 8 9 10"/> 
 </func>

 <!--  12 expression test  -->
<func name="12 expression test">
<set A="2+2+1+4+4"/>
<check A="13"/>
<set B="2*3"/>
<check B="6"/>
<set B="12/2"/>
<check B="6"/>
<set C="(2+2)*3+1"/>
<check C="13"/>
<set D="10e3*6+6+6"/>
<check D="666"/>
<set E="sqrt(9)*4+1"/>
<check E="13"/>
<set F="sqrt(sqrt(8+1)*3)*4+1"/>
<check F="13"/>
<set G="(A+B)/2"/>
<check G="9"/>
<set H="pi"/>
<check H="3.1415" tol="0.001" comment="check constant pi with deshired tolerance"/>
<set J="G==9"/>
<check J="true"/>
<check J="1"/>
</func>
  ````

# Detection of buttons or rectangle areas on the screenshot
We use convolutional filters with long kernel to detect edges of rectangle.
This contours go to the CNN that can classify rectangles and text.
After that we apply some algo based on set teory.
The last stage of button detection is actually applying CNN for the letters. 
  
## Screenshots 
![image](https://github.com/Quasikot/BunchOfQuasiIdeas/blob/main/images/UC_ALGO.png)

fig.1 Button detector

![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/screenshots/delay_widget.png)

fig.2 Widget for setting delays

![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/screenshots/xml_editor_screenshot.png)

Fig.3 Clicker program editor in the form of an xml tree.

![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/screenshots/mainwindow_0.92.png)

fig.4 The editor of the clicker program in the form of an xml tree with pictures on the right.

![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/screenshots/testform_0.92.png)

fig.5 Cool test program

# This is my scetches for cv part of UsefulClicker.
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/galaxy_cluster_shitt.jpg)
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/path_matcher_idea.jpg)
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/quad_tree_clustering.jpg)
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/spiral_idea.png)
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/cnn_for_button_detection.jpg)
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/page_segmentor.jpg)
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/button_cnn_clasifer.jpg)
![image](https://github.com/Kvazikot/UsefulMacro/blob/master/UsefulClicker/cv/sketches/android_port_qpython.jpg)
![image](https://raw.githubusercontent.com/Kvazikot/UsefulMacro/master/UsefulClicker/cv/sketches/rect_numbers.png)
  
## References
* THE MATHEMATICAL THEORY OF COMMUNICATION CLAUDE E. SHANNON, WARREN WEAVER
* Engineering a Compiler (Keith Cooper, Linda Torczon) 
* CS 61B - Data Structures - Jonathan Shewchuk
