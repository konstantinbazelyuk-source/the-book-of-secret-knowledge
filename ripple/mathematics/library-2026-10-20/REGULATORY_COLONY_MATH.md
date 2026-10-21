# Scientific basis and limits of transfer

These sources informed explicit computations. They do not certify this software or establish that its engineered parameters are biological mechanisms.

| Primary source | Verified scientific context | Engineering use here |
|---|---|---|
| Turrigiano et al. (1998), *Activity-dependent scaling of quantal amplitude in neocortical neurons*, DOI 10.1038/36103; https://pubmed.ncbi.nlm.nih.gov/9495341/ | Activity-dependent changes can regulate synaptic input strength | Motivation for regulation; original source homeostasis is retained. The new running-mean divisor is not a reproduction of that experiment or its biological timescale. |
| Carandini & Heeger, *Normalization as a canonical neural computation*, DOI 10.1038/nrn3136; https://pmc.ncbi.nlm.nih.gov/articles/PMC3273486/ | Divisive normalization is studied across sensory computations | A declared input-pool normalization equation, tested for causal effect and bounded denominator |
| Tasic et al. (2018), *Shared and distinct transcriptomic cell types across neocortical areas*, DOI 10.1038/s41586-018-0654-5; https://pubmed.ncbi.nlm.nih.gov/30382198/ | Gene-expression profiles distinguish neuronal cell types | Motivation for an explicit genotype-to-cell-type map. No transcriptomic dataset or inferred biological type is used in training. |
| Gabbiani et al. (2002), *Multiplicative computation in a visual neuron sensitive to looming*, DOI 10.1038/nature01190; https://pubmed.ncbi.nlm.nih.gov/12447440/ | Experimental/theoretical work supports multiplicative processing in an identified visual neuron | Motivation for testing pairwise state interactions; the polynomial readout is engineered, not a reproduction of the locust neuron |
| Jeffrey H. Shapiro, MIT 6.453, Lecture 18 (2016), https://ocw.mit.edu/courses/6-453-quantum-optical-communication-fall-2016/af456c94851f95431b1db2819296a5d8_MIT6_453F16_Lect18_Notes.pdf | Coherent optical detection, photon units, efficiency and count statistics connect semiclassical and quantum descriptions | The Poisson count model, with explicit simplifying dark-count/saturation assumptions |
| MIT 6.453 course readings, https://ocw.mit.edu/courses/6-453-quantum-optical-communication-fall-2016/pages/readings-and-lecture-slides/ | Coherent states, linear optical systems and photodetection | Passive amplitude transformations; no assertion that nonclassical resources were simulated or measured |

For coherent light through passive linear optics, propagating complex amplitudes and evaluating count probabilities avoids enumerating enormous numbers of photon histories. That is the relevant mathematical reduction used here. It does not make an unexecuted trial count an executed experiment.

Original LIF/Delta/Daughter sources and the Charlie port/reference remain the preserved Ripple implementations identified in the source manifests. They are user-engineered cell models, not claimed copies of all known biological neuronal types. Other Library spin-offs contain scheduling, routing, event telemetry and program inference; those roles are not reclassified as additional neuron types merely to inflate the model's taxonomy.

The current source inspection covers the prior 25-archive inventory, newer Genetic Weights v1.7 and ClusterNeuron v2.4 AddOn, and the newer paired-colony coupling/failure report. The latter explicitly records failure under polarity shifts and correlated decoys. This work carries forward the need for causal controls, not an unsupported claim that communication solves unfamiliar semantics.

No Claude, Gemini, Grok or other external model was used as an experimental oracle. Public primary research was consulted; execution occurred in the available hosted Python/Node runtime. No extra cloud account, quantum processor or paid compute cluster was provisioned.
