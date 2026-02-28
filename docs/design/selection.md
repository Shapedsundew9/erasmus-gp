# The Erasmus Selection Algorithm

## 1. Introduction: Parallels with Natural Selection

The selection functions in Erasmus are based on a scheme that closely mirrors natural selection in the real world. In nature, a population's size is a direct function of its *survivability*—the easier a species finds its ability to survive in a given environment, the more successful it will be, and its population will grow. Consequently, when drawing from the gene pool to create the next generation, the most probable selection is the most abundant one.

In Erasmus, survival is a function of competition. However, since the system is strictly interested in finding solutions to user-defined problems (rather than genetic code-defined problems), we do not simulate a direct "arms race" where competing genetic codes actively attempt to destroy each other. Instead, competition is simulated indirectly through the struggle for limited environmental resources—represented here as the fitness "rewards" gained by solving parts of a problem.

If a genetic code (GC) can exclusively solve a specific part of a problem, it faces no competition for those available rewards and can claim them entirely, heavily encouraging evolutionary diversity and niche-finding. When multiple GCs compete for the same rewards, the distribution of those limited rewards is swayed by each code's *efficiency* at claiming them. In the realm of compute, efficiency is defined by speed (execution time) and size (codon count). Furthermore, nature rewards lineages that produce viable offspring; therefore, Erasmus incorporates an "evolvability" factor to organically encourage successful parent GCs to propagate while suppressing those with stagnant or destructive mutations.

Selection from the gene pool for reproduction is ultimately random, but heavily weighted by a GC's simulated population size.

---

## 2. Algorithm Definition: Variables, Equations, and Constraints

The progression from evaluating a genetic code against a problem to determining its population weight follows this mathematical hierarchy:

### Core Definitions

* **Problem:** A user-defined function that evaluates a genetic code. It consists of one or more Test Cases.
* **Test Case (TC):** An instance of a problem against which a GC's fitness is measured.
* **Test Group ($g$):** A defined collection of Test Cases considered indistinguishable for the purposes of competition. Groups cannot overlap, and all TCs must belong to a group. A problem must have $\ge 1$ test groups.
* **f_min:** To prevent mathematical overflows variables that have a $>0$ requirement are constrained by a range defined by $f_min$ in the implementation. By default $f_min$ is `sys.float_info.min` in python 3.  

### Fitness Metrics

* **Test Case Fitness ($f_{tc}$):** The absolute fitness score a GC achieves on a specific test case.
  * *Constraint:* The sum of the *maximum possible* test case fitness scores for an entire problem must equal exactly $1.0$.
* **Solution Fitness ($f_s$):** The sum of all $f_{tc}$ for a GC across the entire problem.
  * *Constraint:* $0.0 \le f_s \le 1.0$
* **Group Fitness ($f_g$):** The sum of the test case fitnesses ($f_{tc}$) a GC achieves specifically within a single test group.

### Efficiency ($\eta$)

Efficiency dictates how well a GC competes for rewards within a group. It is the product of three coefficients:
$$\eta = t \times z \times e$$
*Constraint:* $0.0 < \eta \le 1.0$

* **Execution Time Coefficient ($t$):** Measures execution speed relative to a threshold and competitors. All times are measured in seconds.
    $$t = \min\left( \frac{T_{threshold}}{T_{avg}}, \frac{T_{avg\_competing}}{T_{avg}}, 1.0 \right)$$
  * $T_{avg}$: Average execution time of the GC for the test cases in the group where it scored $> f_min/2.0$.
  * $T_{avg\_competing}$: Average execution time of all competing GCs for those same test cases.
  * $T_{threshold}$: User-defined constant (default $10^{-12}$ seconds). Must be $>= f_min/2.0$.
  * *Constraint:* $0.0 < t \le 1.0$

* **Size Coefficient ($z$):** Measures genetic size relative to a threshold and competitors.
    $$z = \min\left( \frac{Z_{threshold}}{Z_{avg}}, \frac{Z_{avg\_competing}}{Z_{avg}}, 1.0 \right)$$
  * $Z_{avg}$: Number of codons in the GC.
  * $Z_{avg\_competing}$: Average number of codons of all competing GCs.
  * $Z_{threshold}$: User-defined constant (default $2$). Must be an integer $> 1$.
  * *Constraint:* $0.0 < z \le 1.0$

* **Evolvability ($e$):** A measure of a GC's lineage reputation, representing the potential of its offspring.
    $$e_{new} = (1 - \alpha) \cdot e_{old} + \alpha \cdot \left( \frac{1}{N} \sum_{i=1}^{N} s_{offspring\_i} \right)$$
  * $e_{old}$: The parent's previous evolvability score (newly generated GCs default to $0.5$).
  * $\alpha$: The learning rate/discount factor (e.g., $0.2$) determining how quickly reputation changes.
  * $N$: The number of direct descendants the GC has in the current generation.
  * $s_{offspring\_i}$: The calculated survivability of the $i$-th offspring.
  * *Constraint:* $0.0 \le e \le 1.0$

### Competition & Survivability

* **Group Competition Fitness ($f_{gc}$):** The actual fitness awarded to a GC for a test group after accounting for competition and efficiency.
  $$f_{gc} = f_g \times \left( \frac{\eta}{\sum \eta_{competing}} \right)$$
* **Survivability ($s$):** The ultimate score determining the GC's population representation. It is the sum of all Group Competition Fitnesses across the problem.
  $$s = \sum f_{gc}$$
  * *Constraint:* $0.0 \le s \le 1.0$

* **Population:** Directly proportional to Survivability ($s$).

---

## 3. Explanation of Design Intent

### The "Crowding Penalty" & Memory-Efficient Diversity

The concept of Test Groups combined with the $f_{gc}$ formula acts as a highly efficient "Crowding Penalty" rather than a standard strict resource-sharing model. In standard Implicit Fitness Sharing, competition is calculated per test case, which scales linearly in memory and compute. If a problem has millions of test cases, the system would grind to a halt tracking the specific competitors for every single case.

By grouping cases, the system assumes that any GC scoring points within a group is occupying the same "environmental niche." If a group becomes heavily populated with competing GCs, the formula $f_g \times (\eta / \sum \eta_{competing})$ naturally drops the reward for operating in that space. Even if two GCs solve entirely different cases *within* the same group, they mutually reduce the fitness they extract from it.

This is an intentional and beautiful trade-off: it creates intense evolutionary pressure for GCs to mutate and explore entirely empty, unsolved test groups (driving diversity) at a fraction of the memory overhead required to track individual case-level competition.

### Efficiency as a Competitive Edge

In nature, two predators might hunt the same prey, but the faster, leaner predator will secure the lion's share of the calories. The Execution Time ($t$) and Size ($z$) coefficients simulate this. If a Test Group is crowded, a GC can maintain a higher $f_{gc}$ by executing faster or using fewer codons than its peers. The mathematical formulation bounds these advantages between $0.0$ and $1.0$, ensuring that an infinitely fast program doesn't achieve infinite fitness, but simply claims up to 100% of its potential share.

### Evolvability via Retroactive Credit

Tracking deep, multi-generational family trees to determine if a GC is a "good parent" is computationally prohibitive. Evolvability ($e$) solves this using a reinforcement learning concept: Retroactive Discounted Credit.

Instead of looking forward, the system updates a parent's reputation retroactively at the end of every generation based on the survivability ($s$) of its immediate offspring. Because those offspring will, in turn, have their own $e$ scores updated by *their* offspring, the system naturally allows the success of a grandchild to ripple back up the family tree. This organic backpropagation seamlessly rewards lineages that consistently produce viable code, suppressing fragile genetic combinations that frequently produce "broken" descendants.
