# Catalog of Virtual Experiments and Approaches to Simulation

As part of the project to create an environment for simulated genius agents, the following classification of possible types of scientific experiments and approaches to their virtual implementation is proposed.

## ⚙️ 1. Physical Experiments

| Type of Experiment         | Simulation Method                              | Comment |
|---------------------------|------------------------------------------------|---------|
| Mechanics (Newton, Huygens) | Physics engines like Unity, Unreal, MuJoCo      | Realistic physics of bodies, mass interactions |
| Optics                    | Ray tracing, visual plugins                     | Emulation of refraction, reflection, interference |
| Electricity and Magnetism  | Circuit simulators (SPICE), Omniverse + ModKit | Simulation of circuits, fields, voltage generation |

## 💡 2. Chemical Experiments

| Type of Experiment         | Simulation Method                             | Comment |
|---------------------------|----------------------------------------------|---------|
| Simple Reactions          | Input of pre-calculated data                 | No dynamics — result is substituted from the database |
| Catalytic Processes       | Models based on QM/MM or databases           | High computational requirements — better to use substitution |
| Synthesis Experiments     | Use of existing chemical simulators          | Possible integration with ChemDraw API, RDKit, etc. |

## 🧪 3. Biological Experiments

| Type of Experiment         | Simulation Method                              | Comment |
|---------------------------|------------------------------------------------|---------|
| Cell Growth                | Visualization based on templates                | Pseudo-simulation with result substitution |
| Evolutionary Processes     | Artificial evolution algorithms                  | May be used to assess cognitive hypotheses |
| Genetics and Mutations     | DNA databases, Mendelian rules                  | Symbolic modeling, agent-based evolution |

## 🧭 4. Astronomy and Cosmology

| Type of Experiment         | Simulation Method                              | Comment |
|---------------------------|------------------------------------------------|---------|
| Observation of Celestial Bodies | Use of real NASA, Gaia data                     | Discoveries can be simulated based on hidden information |
| Kepler's Laws, Gravity    | Simulation of orbital models (e.g. Celestia)  | Visualization of trajectories and gravitational effects |
| Spectral Analysis         | Generation of fake spectra                       | Fitting realistic scenarios based on a database |

## 🔬 5. Mathematics and Logic

| Type of Experiment         | Simulation Method                              | Comment |
|---------------------------|------------------------------------------------|---------|
| Derivation of Formulas     | Physical simulation not required                 | Agents can logically derive truths based on axioms |
| Mathematical Modeling      | Code execution sandbox                          | Inclusion of a compiler for hypothesis verification |

## 💻 6. Computer Science and Engineering

| Type of Experiment         | Simulation Method                              | Comment |
|---------------------------|------------------------------------------------|---------|
| Processor Architecture      | Emulation (QEMU, RISC-V simulators)           | Possible simulation of the evolution of computing systems |
| Algorithms and Computations | Software implementation, sandbox                | Support for coding and testing environment |

---

## 📌 General Approaches to Simulation

1. **Substitution of Experimental Data**  
   If agents request a result — a pre-calculated answer is provided from a meta-system.  
   
2. **Dummy Interface**  
   Feedback is simulated through an interface that provides data on behalf of the experimental environment.  
   
3. **Pseudo-equipment Interfaces**  
   Agents see the GUI of laboratory instruments, but calculations are carried out outside their environment.  
   
4. **Feedback on Experiment Validity**  
   In case of incorrect setup, an error or noisy result can be returned, simulating a failed experiment.  
   
5. **Access Limitation to Future Knowledge**  
   All data is filtered according to the epoch — agents receive only the information that could have been available to their culture.  

---

## 📎 Implementation Notes

- Implementation may rely on platforms such as **NVIDIA Omniverse**, **Unity**, **MuJoCo**, **OpenAI Gym**, **SciPy**, **RDKit**, **Qiskit**.  
- If credible simulation is not possible, the use of **expert assessments** or **falsified data** consistent with the scientific logic of the era is allowed.  
- A central repository of results allows agents to share discoveries and synchronize their theories.  

---

## 🧠 Relation to the Task of Simulating Genius

Virtual experiments serve as the interface between the simulated agent and real scientific knowledge. Through them, the agent "learns" about the world, tests hypotheses, and either makes a brilliant discovery or encounters false leads. This is the key element in assessing cognitive capability.

