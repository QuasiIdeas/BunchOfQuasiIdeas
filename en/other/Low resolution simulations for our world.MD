# Low resolution simulations for our world
Quasi 2019 <br/>
last update: 12 Aug 2021 <br/>

<br/>
## Introduction

Over the years since Nick Bostrom's 2003 simulation argument was made in [1], many researchers have attempted to calculate the computer processing power required to simulate a world similar to ours. Bostrom in his articles writes about the historical simulation that was launched by a civilization that had reached the post-human stage of development. In which artificial intelligence will be created that thinks orders of magnitude faster than an ordinary person and is capable of participating in rendering the world for a specific player or observer. It is reasonable to assume that artificial intelligence, when developing a historical simulation, implements many optimizations in it to reduce the load on the main computer, because, as Bostrom points out, they need to run an astronomical number of such simulations, taking into account the fact that simulations as virtual machines can be nested. Bostrom notes that in one second such a computer will be able to simulate the life of an entire human civilization (~100 billion people).

How is such computational efficiency achieved? When will our civilization be able to run a simulation? What technologies and algorithms that exist now will help implement this grandiose project, comparable only to the Manhattan one. Why are colossal funds allocated for the study of extraterrestrial civilizations (SETI), but practically nothing is allocated for the development of simulation technology? It may turn out that our space programs are a waste of resources.
Previously given calculation speed estimates for the world
Robert J. Bradbury [2] suggests the number of operations of a planet-sized computer is about 10^42 instructions per second. Seth Lloyd in article [3] suggests an upper limit of computation for a one-kilogram computer of 5*10^50 operations per second.

The computational speed required for brain simulation also varies among different authors and is in the range of 10^16-10^17 operations per second
My personal understanding of the simulation hypothesis. When did I even think about this topic?

When I was growing up with my grandmother, we loved to go to the base and play computer games. That was the name of the house with computer machines. These were rather slow computers, but they made it possible to create a two-dimensional virtual world on the screen, which obeyed certain rules, in some places even reminiscent of the laws of physics. Even when playing primitive 2D arcade games, I was always surprised by the limitations that existed in the virtual world. Why can't you go back or destroy the wall? Then I began to understand that everything depends on the amount of memory and processor performance.

At that time, the movie Terminator 2 was released. I liked one scene where Arnold Schwarzenegger steals a car by breaking the window with his fist, takes the keys from the glove compartment, starts the car and drives away. And I thought that in the future a game would be created in which it would be possible, just like Arnold, to steal cars in a 3-dimensional world. When the guys from a provincial town asked what games you play there, I told them that I play these kinds of games. Of course they didn't believe me. Who could have thought then that 10 years later the game Grand Threft Auto would appear.

Later, when I got into programming, I learned that the level of detail is the most important part of game engines (called LOD, from the English abbreviation Level Of Details). For example, the terrain and objects on it can be displayed using a quad tree. Our world can be simulated at the level of detail that an observer can perceive.

Sometimes the question arises when I was connected to the matrix. Was I born in a simulation? Have I recently been connected to a simulation? Has the simulation existed since the beginning of the Big Bang or, like in the matrix, since 1999? Maybe only the place where I live is simulated, the simulation expands depending on my movements? Are other places, for example YouTube videos, loaded from other simulations?: http://consc.net/papers/matrix.pdf

Back in school we built Platonic solids; let’s say a cone can be built using regular polyhedra. The idea of LOD can be traced in Russian philosophy, for example, Nikolai Kuzansky writes. “Reason is as close to truth as a polygon is close to a circle; the greater the number of angles of an inscribed polygon, the closer it is to a circle. But not when it is not identical to a circle.”
During my high school years, the movie The Matrix came out. Where the main idea of the film was that the world is a computer simulation, like the ones I played as a child. I remember cutting out a piece from the film where Morpheus, on a white background, approaches an old TV and shows Neo what world he lived in and what the world really is. A little later at university, I read a book by Nick Bostrom and Seth Lloyd in which the laws of physics of the real universe were presented as operations on bits.

Although the simulation hypothesis cannot be confirmed experimentally, I give it a non-zero probability. (update) see [17]
When I started thinking seriously about the simulation hypothesis, I began to reconsider the events of my life in the context of this hypothesis. It's hard to believe that life has no meaning. Because natural selection, in principle, has no direction. But if we assume that the world is a high-level simulation, then perhaps our lives make sense only in the context of this simulation and serve its purposes. For example, our simulation is needed to test some mathematical hypothesis, and all the atoms in our world serve as the basis for such a calculation.
Computing speeds in case of reasonable consumption of computing resources
Seth Lloyd in his book "Programming the Universe" starts from the materialist concept that the world is fundamentally materialist. And the “big” world seems to arise from the elementary interactions of this huge number of particles. Lloyd mentioned in one of his lectures that to simulate the universe you will need a computer the size of the universe, otherwise it will collapse into a black hole. But why is he so sure that it is necessary to simulate the entire universe of 10^122 atoms. Chess players would call this method bruite force. or brute force method. It is necessary to mention such a critically important term for virtual reality as level of detail.

Firstly, you don’t need to simulate the entire universe, but only one inhabited planet. This can be done on a hypothetically possible astro-engineering computer, Matryoshka Brains (or several concentric Dyson spheres around any of the billions of stars). The power of such a thing will be enough for millions of optimal, in my sense of the word, simulations per second of real time in which thousands of years of simulated time pass.

Instead of a dull clockwork mechanism in the case of a historical simulation, we are dealing with artificial intelligence standing behind the scenes. And he can decide which objects in the world need to be calculated with what level of detail and do this not from bottom to top, but rather from top to bottom, as is done in any modern game engine. For example, chemical reactions are quite expensive to calculate, because it requires going down to the level of molecules. But the average person encounters chemical reactions only when he prepares his own food, and when this food comes out, I won’t specify where it comes from. And then in my case, I need to calculate that with a 3% probability I will add pepper to the scrambled eggs, with a 10% probability I will make an omelette, with a 2% probability I will over-salt the scrambled eggs. The result of such a simulation can be a selection from a table of ready-made results without simulating any chemical reactions. The Monte Carlo method can help in these kinds of simulations [10]. The Monte Carlo method refers to simulation modeling in which, when calculating a system, the behavior of all its components is reproduced and studied. How can you model a complex system without knowing the strict mathematical laws that it obeys? The answer to this question is contained in the name of the category of the method - “imitation”. If the behavior of the system is quite complex and it is not possible to describe it with strict mathematical formulas, it is necessary to carry out a certain number of experiments (the so-called random tests) with each of the nodes of this system in order to evaluate how they behave. In addition to the Monte Carlo method, you can use universal function approximators - neural networks. They can be used to model chemical reactions by approximately solving the Schrödinger equation.[16] This saves a huge bunch of calculations. All you need to do is simulate cooking scrambled eggs several times and use these results every time someone cooks scrambled eggs for breakfast.

Thomas Campbell in one of his lectures gives the example of firing a cannonball [4]. This example demonstrates the general principle of modeling based on probability distributions. If you start a slow deterministic simulation process, it will take weeks on the best supercomputers. Billions of molecules, like the energy of the explosion, spreads through the gun and reaches the core. The escaping gas causes the core to spin in a certain direction. And all this significantly affects where the core lands. And as soon as the core leaves the barrel you need to take care of the air pressure, the pressure changes if you move up or down, the temperature, the density of the air also changes. The core is not an ideal sphere, but a spheroid, and this affects aerodynamics. This is a very difficult problem for deterministic simulation. Instead of such a simulation, Campbell suggests simulating the firing of a cannon using probability distributions. Which is as follows. We take a cannon, load it 100 times and look where the cannonball landed after firing. We construct a probability distribution about which coordinates the nucleus falls into. This dispersion pattern results from differences in the atmosphere and core. Instead of spending weeks of calculations on a supercomputer, we select coordinates from a distribution in microseconds of computer time.

Based on Bostrom's calculations, we can assume that our simulation is far from the first. Bearing in mind that there are millions of simulations similar to ours at the same time, we are probably somewhere in the middle rather than at the beginning, in the very first simulation. Therefore, it can be assumed that the computers of the future have done most of the labor-intensive deterministic calculations required for trivial tasks like cooking scrambled eggs. But when it comes to simulating a new rocket or aircraft, there will be a certain jump in the load on the simulator's processor. But only at the stage of its development and testing. While the aircraft components are not ready, it is necessary to honestly simulate all the signals passing through the electrical circuits to identify failures and bugs in the software. Until the logic of the system is established and until the necessary optimizations are found or probability distributions are calculated. Considering that simulations can be paused and that we have a certain reserve of resources, this will not be a big problem.

The same goes for cell phone signals. In the simulation there are no radio waves or fields (a field is a mathematical abstraction) there are only streams of data. It doesn't make sense to model signal transmission through electromagnetic waves or transmitter and receiver logic (literally how an electrical signal passes through transistors). This is all modeled once during system development. It is enough to have data on the state of the environment (interference level), to know whether someone has turned on a jammer, whether the transmitter/receiver has broken down, or whether someone has jammed into the line. If the jammer is turned on, modeling of radio wave propagation in space and calculation of signal distortion are not required. It is enough to know the parameters of the jammer, whether it is on or off, because its parameters are also known. If someone cuts into the line, you need to redirect the data flow.

It doesn’t make sense to display the insides of any objects, be it vehicles, people, cockroaches most of the time, until you crush a cockroach or until you let someone’s guts out. :) In a simulation, it makes no sense to draw air molecules so that one of the players breathes them. No one will faint from suffocation because we are not in Newtonian objective reality. Even if someone wants to measure the oxygen level with a device, the device will not show 0. After all, it is likely that the room is full of oxygen, because there are many trees outside. In general, data from any devices can be simulated based on probability distributions, a set of rules, and consistency with history. If someone throws a gas grenade into the room, we turn to the statistics of survival of people at such and such a concentration of such and such a substance in the blood or in the lungs. If someone wants to measure the presence of molecules in the blood, this is where they need to simulate the molecules to maintain consistency with history.
Purely statistically, one can imagine that there are very detailed simulations in which there are few optimizations and everything is honestly simulated down to an atom less than optimal and, accordingly, less detailed. As A. Turchin writes, “On the other hand, simulations made “hastily” will contain much more glitches, but at the same time consume immeasurably less computing resources. In other words, with the same costs it would be possible to make either one very accurate simulation, or a million Further, we assume that the same principle applies to simulations as to other things: namely, that the cheaper a thing is, the more common it is (that is, there are more glass pieces in the world than diamonds, more meteorites than asteroids, etc.) Thus, we are more likely to be inside a cheap, simplified simulation, rather than inside a complex, ultra-precise simulation."

## Optimizations at the level of particle physics.
In the famous double-slit experiment, light exhibits its wave-particle properties. If there is an observer (which could be a photodetector), then the light behaves like a particle; if there is no observer, then there is no particle.

## The role of the observer
Here we can point out that there are several interpretations in quantum mechanics. The traditional Copenhagen theory states that the collapse of the wave function is caused by the observer or detector. But in fact, decoherence (detection) of a photon can be caused by the environment, such as an air molecule.

In a simulation there is no world independent of the observer and there is no objective reality in the classical sense. If you are riding a bicycle along a country rocky path and there is no one else on this road except you (including cameras with a video recorder, cats and dogs). Let the wind blow outside. You are turning off this road. Now there are no observers on it. There is no one to render this track for. Even if some pebble or branch could potentially move under the influence of the wind, these physical calculations will be cut off, i.e. will not be fulfilled. You still don’t remember where which pebble was and which branch lay where. Just like in the example with the forest, when you enter this path again, the system will generate a new distribution of stones along the road. It makes no sense to store such small details in the simulator’s memory, and even less so all the atoms and molecules that make up the stones. If you lose your balance and break your leg on one of the stones, then the story will branch only in case. unless you are an NPC if you play some potentially important role in the story.

Now the story is about a dead tree in the forest. Connection with procedural world generation and saving simulator memory. Let's say a man went into the forest and saw a dead tree felled there. Why did he see him? Well, it was probable, it was probable that among the 50 trees in the forest there would be one dead one. This does not mean that it stood and then fell. It just means it's dead. Then he returned five years later and the tree still lies in the same place. Because the information that it is dead and lying on the ground is stored in its memory. Then he goes even further into the forest where he is safely eaten by a bear. Another person comes some time later to the same forest. Will he see the dead tree? Perhaps it will or perhaps not. A new random sample of 50 normal standing trees will be taken for it.

## Brain of a Sim (simulated creature)
The brain that neuroscientists see through PET scans or when directly removed may not be anything more than a simple voxel texture (or deformation map) whose function is simply to explain to other Sims what is wrong with it. If, for example, a Sim hits his head or has a blood vessel burst, he stops moving normally. He walks with a limp, speaks slurred, etc. But in some special cases, the robustness of the real conscious supersystem makes it possible to improve some other mental functions. For example, hearing is enhanced if the visual part of the voxel texture is damaged.

We can find confirmation of this hypothesis in contradictory factual information in the sciences of language. For example, it was previously thought that language-related computations were performed by a localized area of the brain called Broca's area. New information suggests that language is distributed throughout the brain. Quentin Tarantino, in one of his interviews, talked about a man whose “English part of the brain” failed as a result of an injury and he began to speak Spanish.

There were examples of savant people calculating multiplications of 8-digit numbers in seconds, but in general they could not lead an independent life. Others could lead a normal family life, had a job, supported a family, and when scientists looked at their brains through an MRI, it turned out that they only had a thin piece of the so-called neurocortex attached to the brain stem, and most of the skull was filled with fluid[15].

In any theory there are logical contradictions that cannot be explained within the framework of the theory. That's why we need to develop superintelligence to understand how the human brain works. Because the data that was accumulated in the field of neuroscience is so immense.

## Wigner's friend paradox
[more details can be made with a description of the experience] Confirmation that objective reality does not exist in the form that Newton's followers assumed. Reality is probabilistic and informational; it is different for everyone. But there must be consistency in it. FLOWS of information are responsible for the consistency of history. 

What optimizations are used to render large spaces in games?

Clipping by FOV (field of view) Description of terrain rendering algorithms (quad tree) and objects used in open world games.

Procedural world generation in the games No man Sky or Minecraft.

Vegetation modeling example fractal algorithm L-system
Imitation of materials
A good simulation should have realistic materials. The sofa should be soft, the table should be hard, the board should sag when you stand on it, the plastic bottle should crumple. In other words, calculation of deformations is necessary. When testing new cars, mathematical modeling is carried out to calculate the deformations of the entire car body during collisions. Already in the early 2000s, programs for 3D modeling of clothing and soft body tissues appeared. Of course no one models clothes or muscles at the molecular level, it's a waste of resources, instead you have a set of equations to describe the deformation of a surface when a force is applied to it. Only when developing a new material or conducting experiments do you need calculations down to the atoms. To develop an adequate mathematical model, it is necessary to know the behavior of the material under changes in temperature and pressure. All this is included in a set of rules (literally lines of program code) for which the atoms themselves are no longer needed. When an object made from this material appears in a simulation, you only need code describing its behavior and a 3D model of the object that is made from this material. In game engines since the 2000s, special programs for the graphics processor called shaders are used for materials.

## Weather simulation
It is customary to model weather using chaos theory.

## Saving energy on brain calculations
Kelly Irwin formulated an abstract principle called the principle of least computational action. When I write new programs, instead of writing new code from scratch, I always look in my old programs to see if I did something similar. The brain is such a machine that likes to save energy at every opportunity, because before it wasn’t very good with food. The brain modifies itself to minimize free energy [10]. Nature does the same thing, see links about fractals below[5].

Many works of art, be it a novel or a movie script, are not original, but are based on something that already exists[7]. Examples include Shakespeare's works, Hollywood scripts, and Van Gogh's drawings. If you look at the models of fighter aircraft immediately after World War II, you can see the general design of the aircraft of the USSR and the USA.
I can add that if you write all the conclusions of the theorems of arithmetic on paper and number them, you will get a set of integers from zero to infinity. And in order to find the required sequence of derivation of the theorem in this huge array, enormous computing power will be required[8].

How can you try to prove the simulation hypothesis?
The main idea of this article is that you use the results of calculations in one world to quickly clone the same results in another world. For example, it makes no sense to simulate the generation of the potato form every time starting from the genetic and molecular level. To prove a simulation hypothesis, someone could try to take 1 million potatoes and find several that are almost identical. Or find the formula for the shape morphing function using machine learning methods. Basically you need to find generator neural network of that kind of data. To do this, you need to scan potatoes in 3D and run some procedure for searching the function space from which this particular geometric structure can be generated. Here it must be taken into account that it makes no sense to go down to the microstructure level. Because here the situation is the same as with the terrain, the microstructure is generated at the moment when you zoom or look through a microscope. I don’t think that the list of such formulas will exceed 10 positions. According to Occam's principle, the shortest formula will be the closest to the original.

The second direction is the search for fractal structures. I think it's useful to continue trying to reverse engineer a simulation, if only because it's an interesting thought experiment.

## Links
N. Bostrom ARE YOU LIVING IN A COMPUTER SIMULATION? https://www.simulation-argument.com/simulation.html Russian translation by A. Turchin https://www.proza.ru/2009/03/09/639

R. J. Bradbury, “Matrioshka Brains.” Working manuscript (2002), http://www.aeiveos.com/~bradbury/MatrioshkaBrains/MatrioshkaBrains.html.

S. Lloyd, “Ultimate physical limits to computation.” Nature 406 (31 August): 1047-1054 (2000).

T. Campbell "My big Toe" www.my-big-toe.com https://www.youtube.com/watch?v=WxBOBWLAn2Y&t=1179s

Could our universe be fractal? https://youtu.be/tN_eNQFcv5E

Klee Irwin - The Principle of Efficient Language https://www.youtube.com/watch?v=ZxKdv-_BSZo

Your Brain Can't Create New Ideas https://youtu.be/ZjnHp5R_364

Nikolai Kuzansky http://eurasialand.ru/txt/babaev/80.htm

Vladimir Vernadsky "Biosphere and noosphere" http://www.spsl.nsc.ru/win/nelbib/vernadsky.pdf

Max Tegmark. Mathematical Universe Hypothesis https://ru.wikipedia.org/wiki/%D0%93%D0%B8%D0%BF%D0%BE%D1%82%D0%B5%D0%B7%D0%B0_%D0% BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE% D0%B9_%D0%B2%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%BD%D0%BE%D0%B9

Monte Carlo method. https://ru.wikipedia.org/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4_%D0%9C%D0%BE%D0%BD%D1%82%D0 %B5-%D0%9A%D0%B0%D1%80%D0%BB%D0%BE

Quantum entanglement https://ru.wikipedia.org/wiki/%D0%9A%D0%B2%D0%B0%D0%BD%D1%82%D0%BE%D0%B2%D0%B0%D1%8F_ %D0%B7%D0%B0%D0%BF%D1%83%D1%82%D0%B0%D0%BD%D0%BD%D0%BE%D1%81%D1%82%D1%8C

Anders Sandberg The Physics of Information Processing Superobjects: Daily Life Among the Jupiter Brains

Brains, Computation And Thermodynamics: A View From The Future? https://www.3quarksdaily.com/3quarksdaily/2020/07/brains-computation-and-thermodynamics-a-view-from-the-future.html

14 D. Deutsch “The Structure of Reality” 2015

15 Jim Elvidge https://www.theuniversesolved.com/

Deep-neural-network solution of the electronic Schrödinger equation Jan Hermann, Zeno Schätzle & Frank Noé https://www.nature.com/articles/s41557-020-0544-y

A Bayesian Approach to the Simulation Argument David Kipping https://www.mdpi.com/2218-1997/6/8/109/htm

18.Confirmed! We Live in a Simulation. We must never doubt Elon Musk again https://www.scientificamerican.com/article/confirmed-we-live-in-a-simulation/

Time-Warped Foveated Rendering for Virtual Reality Headsets Linus Franke, Laura Fink, Jana Martschinke, Kai Selgrad, Marc Stamminger https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14176

RBF Liquids: An Adaptive PIC Solver Using RBF-FD Rafael Nakanishi, Universidade de São Paulo - USP, Brazil https://rnakanishi.github.io/files/rbf-sa2020.pdf

Rizwan Virk - The Simulated Multiverse_ An MIT Computer Scientist Explores Parallel Universes, the Simulation Hypothesis, Quantum Computing and the Mandela Effect-Bayview Labs, LLC (2021)

Reality+ by David J Chalmers
