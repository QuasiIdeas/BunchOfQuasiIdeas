# Low-Resolution Simulations for Our World

Vladimir Baranov

St. Petersburg State University of Aerospace Instrumentation

2019, last update: August 12, 2021

## Introduction

For many years after Nick Bostrom's argument for simulation was presented in 2003 in article [1], many researchers attempted to estimate the computational power required to simulate a world similar to ours. Bostrom writes in his articles about a historical simulation launched by a civilization that has reached a post-human stage of development. In this simulation, an artificial intelligence is created that thinks orders of magnitude faster than a typical human and is capable of rendering a world for a specific player or observer. It is reasonable to assume that the artificial intelligence, while developing the historical simulation, implements numerous optimizations to reduce the load on the main computer, as Bostrom points out that they need to initiate an astronomical number of such simulations, considering that simulations, like virtual machines, may be nested. Bostrom notes that in one second, such a computer could simulate the life of an entire human civilization (~100 billion people). How is such computational efficiency achieved? When will our civilization have the capabilities to launch simulations? What technologies and existing algorithms currently available can help realize this grand project, comparable perhaps only to the Manhattan Project? Why are colossal funds allocated for the study of extraterrestrial civilizations (SETI), while almost nothing is allocated for the development of simulation technology? It might turn out that our space programs are a waste of resources.

## Earlier Estimates of Computational Speed for a World

Robert J. Bradbury [2] suggests that a computer the size of a planet performs about 10^42 instructions per second. Seth Lloyd in article [3] proposes an upper limit for computations of a one-kilogram computer at 5*10^50 operations per second. The speed of computations necessary for simulating a brain varies among different authors and is in the range of 10^16-10^17 operations per second.

My Personal Understanding of the Simulation Hypothesis. When I First Considered This Topic

When I was growing up at my grandmother's house, we loved to go to the arcade and play computer games. This was the name given to a small building with video game machines. These were fairly slow computers, but they allowed the creation of a two-dimensional virtual world on the screen, governed by specific rules, somewhat reminiscent of the laws of physics. Even while playing primitive 2D arcade games, I was always amazed by the limitations present in the virtual world. Why couldn't I go back or break a wall? Then I began to understand that it all comes down to memory size and CPU performance. At that time, the movie "Terminator 2" came out. I liked one scene where Arnold Schwarzenegger steals a car by breaking the window with his fist, takes the keys from the glove compartment, starts the car, and drives off. I thought that in the future, a game would be created in which one could steal cars just like Arnold did in a 3D world. When the guys from the provincial town asked me what games we played there, I told them I played that kind of game. Of course, they didn't believe me. Who could have thought back then that in 10 years, "Grand Theft Auto" would be released? Later, when I got into programming, I learned that the level of detail is a crucial part of game engines (called LOD, from the English abbreviation Level Of Detail). For example, the terrain and objects on it can be represented using a quad tree. Our world may be simulated at the level of detail that can be perceived by the observer. Sometimes a question arises: when was I connected to the matrix? Was I born in a simulation? Was I recently connected to a simulation? Does the simulation exist since the beginning of the Big Bang or, like in "The Matrix," since 1999? Maybe only the place where I live is being simulated, and the simulation expands based on my movements? Are other places, like videos from YouTube, loaded from other simulations? 
http://consc. net/papers/matrix. pdf

Back in school, we constructed Platonic solids; for example, a cone can be built using regular polyhedra. The idea of LOD can be traced in Russian philosophy; for instance, Nikolai of Cusa writes: "The mind is as close to the truth as a polygon is to a circle; the more angles the inscribed polygon has, the closer it is to the circle. But it will never be identical to the circle."

During my senior years in high school, the movie "The Matrix" was released, where the main idea was that the world is a computer simulation, similar to those I played in my childhood. I remember cutting a scene from the movie where Morpheus, against a white background, approaches an old television and shows Neo the world he lived in and what the real world is. Shortly after, in university, I read books by Nick Bostrom and Seth Lloyd, where the laws of physics in the real universe were represented as operations on bits. Although the simulation hypothesis cannot be experimentally confirmed, I assign it a non-zero probability. (update) see [17]

When I seriously contemplated the simulation hypothesis, I began to revisit events in my life in the context of this hypothesis. It is hard to believe that life has no meaning since natural selection, in principle, has no direction. But if we assume that the world is a high-level simulation, then perhaps our lives have a purpose only in the context of this simulation and serve its goals. For instance, our simulation might be necessary to test some mathematical hypothesis, with all atoms in our world serving as the basis for such calculations. 

## Computational Speeds with Reasonable Resource Consumption

Seth Lloyd, in his book "Programming the Universe," starts from a materialistic concept that the world is fundamentally materialistic. And the "big" world somehow arises from the elementary interactions of this vast number of particles.

Lloyd mentioned in one of his lectures that simulating the universe would require a computer the size of the universe, otherwise it would collapse into a black hole. But why is he so sure that we need to simulate the entire universe of 10^122 atoms? Chess players would call such a method brute force. It’s important to mention a critically important term for virtual reality: level of detail.

Firstly, we need to simulate not the entire universe but only one habitable planet. This can be accomplished using a hypothetically possible astroengineering computer, a "matryoshka brain" (or several concentric Dyson spheres around any of billions of stars). The power of such a device would be sufficient for millions of optimal simulations per second in my sense of the word, simulating thousands of years of simulated time. Instead of a simplistic clock mechanism in the case of historical simulation, we deal with an artificial intelligence that, as it were, stands behind the scenes. It can decide which objects of the world need to be calculated with which level of detail and do this not from the bottom up but from the top down, as is done in any modern game engine. For example, calculating chemical reactions can be quite costly because it requires descending to the level of molecules. However, an ordinary person encounters chemical reactions only when preparing food, and when that food comes from sources I won't specify. Even in my case, it requires calculating that I will add pepper to my scrambled eggs with a probability of 3%, that I will make an omelet with a probability of 10%, and that I will over-salt the eggs with a probability of 2%. The result of such a simulation could be a choice from a table of precomputed results without simulating any chemical reactions. The Monte Carlo method can assist in such simulations. The Monte Carlo method relates to simulation modeling, where the behavior of all components of a system is reproduced and studied during calculations. How can you model a complex system without knowing the precise mathematical laws it follows? The answer lies in the category name of the method—“simulation.” If the behavior of a system is complex enough and there is no opportunity to describe it using strict mathematical formulas, it is necessary to conduct a certain number of experiments (so-called random trials) at each of the nodes of the system to evaluate how they behave. Besides the Monte Carlo method, universal function approximators—neural networks—can be applied. They can be used to model chemical reactions by approximately solving the Schrödinger equation. This saves a tremendous amount of calculations. All you need to do is simulate the preparation of scrambled eggs a few times and use those results every time someone is making scrambled eggs for breakfast. Thomas Campbell provides an example of firing a cannonball from a cannon. This example demonstrates the general principle of simulation based on probabilistic distributions. If you start a slow process of deterministic simulation, it will take weeks on the best supercomputers. Billions of molecules and how the explosion's energy spreads through the cannon and reaches the cannonball. The exhaust gases cause the cannonball to spin in a certain direction. All of this significantly affects where the cannonball will land. And as soon as the cannonball leaves the barrel, you need to consider air pressure; pressure changes if you move up or down, and temperature and the density of the air also change. The cannonball is not a perfect sphere but a spheroid, which affects its aerodynamics. This is a very complex problem for deterministic simulation. Instead of such simulation, Campbell suggests modeling cannon firing using probabilistic distributions. This consists of the following: we take a cannon, load it 100 times, and observe where the cannonball lands after firing. We construct a probability distribution of the coordinates where the cannonball lands. This dispersion pattern results from variations in the atmosphere and in the cannonball itself. Instead of spending weeks computing on a supercomputer, we select coordinates from the distribution in microseconds of computer time. Based on Bostrom's calculations, one can assume that our simulation is far from the first. Considering that there are millions of simulations similar to ours existing simultaneously, we are surely somewhere in the middle rather than at the start, in the very first simulation. Therefore, it can be assumed that the computers of the future have already undertaken most of the labor-intensive deterministic calculations that are required for trivial tasks like making scrambled eggs. But when it comes to modeling a new rocket or airplane, there will be a certain jump in the load on the simulator’s processor. But only at the stage of its design and testing. While the aircraft's components are not ready, it is essential to honestly simulate all the signals passing through the electrical circuits to identify failures and bugs in the software. As long as the system's logic is not established and necessary optimizations have not been found or probabilistic distributions computed. Considering that simulations can be paused and that we have certain resource reserves, this should not pose a significant problem. The same goes for cellular phone signals. In the simulation, there are no radio waves or fields (fields are a mathematical abstraction), only data streams. There is no point in modeling signal transmission via electromagnetic waves or the logic of transmitters and receivers (literally how an electrical signal moves through transistors). All of this is modeled once during system development. It is enough to have data on the state of the environment (level of interference), know if someone has turned on a jamming device, whether the transmitter/receiver has broken, or if someone has interfered with the line. In the case of an active jamming device, there is no need to model the propagation of radio waves in space and calculate signal distortions. It is sufficient to know the parameters of the jamming device, whether it is on or off, since its parameters are known. If someone has interfered with the line, it is necessary to redirect the data stream.

Certainly! Here is the translation of your text into English:

---

Displaying the insides of any objects, whether they are vehicles, people, or cockroaches, makes little sense most of the time, unless you crush a cockroach or rip someone's intestines out. :) In a simulation, there is no point in drawing air molecules for some players to breathe. No one will faint from asphyxiation because we are not in Newtonian objective reality. Even if someone wanted to measure the oxygen level with a device, it would not show 0. It is likely that the room is full of oxygen, given that there are many trees outside. In general, the data from any instruments can be simulated based on probabilistic distributions, a set of rules, and consistency with history. If someone throws a gas grenade into the room, we turn to statistics on human survival rates at a certain concentration of a particular substance in the blood or lungs. If someone wants to measure the presence of molecules in the blood, here we need to simulate molecules to maintain consistency with history. Statistically speaking, it can be assumed that very detailed simulations where little optimization occurs and everything is honestly simulated down to the atom are less efficient and, therefore, less detailed compared to optimal simulations. As A. Turchin writes, "On the other hand, 'hasty' simulations will contain many more glitches but will consume immeasurably fewer computational resources. In other words, for the same expense, one could either create one very accurate simulation or a million approximations. Furthermore, we assume that the same principle applies to simulations as it does to other things: namely, that the cheaper a thing is, the more often it occurs (that is, there are more pebbles than diamonds in the world, more meteorites than asteroids, etc.). Thus, we are more likely to be inside a cheap simplified simulation rather than a complex ultra-accurate simulation."

## Optimizations at the Level of Elementary Particle Physics

In the famous double-slit experiment, light exhibits its particle-wave properties. If there is an observer (which could be a photodetector), light behaves like a particle; if not, then there is no particle. ## The Role of the Observer

Here it should be noted that there are several interpretations in quantum mechanics. The traditional Copenhagen interpretation posits that the collapse of the wave function is caused by an observer or detector. However, in reality, decoherence (the detection of) a photon can be caused by the surrounding environment, such as an air molecule. In a simulation, there is no world independent of the observer, and there is no objective reality in the classical sense. If you are riding a bicycle on a rocky path in a dacha and there is no one else on that path (including cameras with tape recorders, cats, and dogs), and there is wind outside, you turn off that path. Now there are no observers on it. There is no one to render that path. Even if some pebble or twig could potentially shift under the influence of the wind, those physical calculations will be cut off, meaning they will not be performed. You still do not remember where each pebble was and where each twig lay. Just as in the example with the forest, when you re-enter that path, the system will generate a new distribution of stones on the road. Such minor details do not make sense to store in the simulator's memory, let alone all the atoms and molecules of which the stones are composed. If you lose your balance and break your leg on one of the stones, the branching of history will occur only if you are not an NPC (non-player character) and if you are playing a role that is potentially important to the story. Now, consider the story of a dead tree in the forest. The connection with procedural world generation and memory conservation in the simulator comes into play. Suppose a man enters the forest and sees a fallen dead tree. Why did he see it? Well, it was probable, likely that among 50 trees in the forest, there would be one dead. This does not mean it was standing and then fell; it simply means that it is dead. Further, he returns five years later and the tree is still lying in the same place. Because the information that it is dead and on the ground is stored in his memory. He then goes even deeper into the forest where he is happily eaten by a bear. Another person comes into that same forest after some time. Will he see the dead tree? He may or may not. A new random sampling from the 50 normal standing trees will be carried out for him.

## The Brain of the Sim (Simulated Being)

The brain that neurobiologists see through PET scans or when it is directly extracted may represent nothing more than a simple voxel texture (or deformation map) whose function is simply to explain to other sims what is wrong with it. For example, if a sim bumps its head or has a ruptured vessel, it stops moving normally. It walks limping, speaks indistinctly, etc. But in some special cases, the robustness of the real conscious super-system allows for the enhancement of some other cognitive functions. For example, hearing may become sharper if the visual part of the voxel texture is damaged. We can find evidence for this hypothesis in contradictory factual data in the language sciences. For instance, it was once believed that computations related to language were performed by a localized area of the brain called Broca's area. However, new evidence suggests that language is distributed throughout the brain. Quentin Tarantino mentioned in one of his interviews about a person who, as a result of an injury, lost the "English part of the brain" and began to speak Spanish. There have been examples of savant individuals calculating multiplications of 8-digit numbers in seconds, but overall, they could not lead independent lives. Others could live normal family lives, had jobs, supported their families, and when scientists examined their brains through MRI, it turned out that they simply had a thin piece of what is called the neurocortex attached to the brainstem, with a large part of the skull filled with fluid. Gödel's theorem has shown that one cannot understand the brain using the brain itself. In any theory, there are logical contradictions that cannot be explained within the framework of that theory.

--- 

Let me know if you need any more help!

## Wigner's Friend Paradox
[More details can be added describing the experience]
Confirmation that objective reality does not exist in the form assumed by Newton's followers. Reality is probabilistic and informational; it varies for everyone. However, consistency must be present within it. The flows of information are responsible for the consistency of the narrative. What optimizations are applied for rendering large spaces in games?

Culling by FOV (Field of View).
Description of terrain rendering algorithms (quad tree) and objects used in open-world games. Procedural world generation in games like No Man's Sky or Minecraft. Modeling vegetation using fractal algorithms like L-systems.

## Material Simulation
A good simulation should feature realistic materials. A couch should be soft, while a table is hard; a board should bend if you stand on it, and a plastic bottle should crumple. In other words, deformation calculations are necessary. When testing new cars, mathematical modeling is conducted to calculate the deformations of the entire car body upon collisions. By the early 2000s, programs for 3D modeling of clothing and soft body tissues started to emerge. Naturally, no one models clothing or muscles at the molecular level; that would be a waste of resources. Instead, you have a set of equations to describe surface deformations when forces are applied to them. Only during the development of a new material or conducting experiments is atomic-level calculation necessary. To create an adequate mathematical model, it is essential to understand material behavior under changes in temperature and pressure. All of this is included in a set of rules (literally lines of code) where the individual atoms are no longer needed. When an object made of this material appears in a simulation, you only need the code describing its behavior and a 3D model of the object made from this material. In game engines since the 2000s, special programs for graphics processors known as shaders are used for materials.

## Weather Simulation
Weather is typically modeled using chaos theory.

## Energy Efficiency in Brain Computation
Klee Irwin formulated an abstract principle known as the principle of least computational action. When I write new programs, instead of coding from scratch, I always look for something similar in my old programs. The brain is a machine that loves to save energy whenever possible, as it was previously scarce. The brain changes itself to minimize free energy [10]. Nature seems to operate similarly; see the links about fractals below [5]. Many works of art, whether a novel or a movie script, are not original but are based on something that already exists [7]. Examples include Shakespeare's works, Hollywood scripts, and Van Gogh's paintings. If you look at fighter jet designs immediately after World War II, you can see common designs in both Soviet and American aircraft. Furthermore, if you write down all the deductive conclusions of arithmetic theorems on paper and number them, you will have a multitude of integers from zero to infinity. To find a specific sequence of theorems in this vast array would require enormous computational power [8].

# Conclusion. How can we attempt to prove the simulation hypothesis?
The main idea of this article is that you use computation results from one world to quickly clone those results in another world. For instance, it doesn’t make sense to simulate the generation of potato shapes from the genetic and molecular level each time. To prove the simulation hypothesis, someone might try to take 1 million potatoes and find a few nearly identical ones. Alternatively, one could find a formula for a morphing shape function using machine learning methods. To do this, one would need to 3D scan the potatoes and run a procedure to search for a space of functions by which this specific geometric structure can be generated. Here, it is important to note that it doesn’t make sense to delve into the microstructure because it’s similar to terrain relief; microstructure is generated when you zoom in or look through a microscope. I don’t think the list of such formulas will exceed 10 items. According to Occam's principle, the shortest formula will be the closest to the original. The second direction is the search for fractal structures. I believe that continuing attempts at reverse-engineering the simulation is valuable, if only because it is an interesting thought experiment.

Links
1. N. Bostrom ARE YOU LIVING IN A COMPUTER SIMULATION?
https://www.simulation-argument.com/simulation.html
Russian translation by A. Turchin https://www.proza.ru/2009/03/09/639

2. R. J. Bradbury, “Matrioshka Brains.” Working manuscript (2002), http://www.aeiveos.com/~bradbury/MatrioshkaBrains/MatrioshkaBrains.html. 

3. S. Lloyd, “Ultimate physical limits to computation.” Nature 406 (31 August): 1047-1054 (2000). 

4. T. Campbell "My big Toe" www.my-big-toe.com
https://www.youtube.com/watch?v=WxBOBWLAn2Y&t=1179s

5. Could our universe be fractal? https://youtu.be/tN_eNQFcv5E

6. Klee Irwin - The Principle of Efficient Language 
https://www.youtube.com/watch?v=ZxKdv-_BSZo

7. Your Brain Can't Create New Ideas 
https://youtu.be/ZjnHp5R_364

8. Nikolai Kuzansky http://eurasialand.ru/txt/babaev/80.htm

9. Vladimir Vernadsky "Biosphere and Noosphere" http://www.spsl.nsc.ru/win/nelbib/vernadsky.pdf

10. Max Tegmark. The Mathematical Universe Hypothesis
https://ru.wikipedia.org/wiki/Гипотеза_математической_вселенной

11. Monte Carlo Method. https://ru.wikipedia.org/wiki/Метод_Монте-Карло

12. Quantum Entanglement https://ru.wikipedia.org/wiki/Квантовая_запутанность

Here is the translation of your text into English:

---

org/wiki/Quantum_Entanglement

12. Anders Sandberg  
The Physics of Information Processing Superobjects: Daily Life Among the Jupiter Brains

13. Brains, Computation And Thermodynamics: A View From The Future?  
https://www.3quarksdaily.com/3quarksdaily/2020/07/brains-computation-and-thermodynamics-a-view-from-the-future.html

14. D. Deutsch "The Fabric of Reality" 2015

15. Jim Elvidge  
https://www.theuniversesolved.com/

16. Deep-neural-network solution of the electronic Schrödinger equation  
Jan Hermann, Zeno Schätzle & Frank Noé  
https://www.nature.com/articles/s41557-020-0544-y

17. A Bayesian Approach to the Simulation Argument  
David Kipping  
https://www.mdpi.com/2218-1997/6/8/109/htm

18. Confirmed! We Live in a Simulation. We must never doubt Elon Musk again  
https://www.scientificamerican.com/article/confirmed-we-live-in-a-simulation/

19. Time-Warped Foveated Rendering for Virtual Reality Headsets  
Linus Franke, Laura Fink, Jana Martschinke, Kai Selgrad, Marc Stamminger  
https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14176

20. RBF Liquids: An Adaptive PIC Solver Using RBF-FD  
Rafael Nakanishi, University of São Paulo - USP, Brazil  
https://rnakanishi.github.io/files/rbf-sa2020.pdf

21. Rizwan Virk - The Simulated Multiverse: An MIT Computer Scientist Explores Parallel Universes, the Simulation Hypothesis, Quantum Computing, and the Mandela Effect - Bayview Labs, LLC (2021)

22. Reality+ by David J. Chalmers

23.  

--- 

Let me know if you need further assistance!

