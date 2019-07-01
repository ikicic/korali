# Korali  ![](images/logo.png){: style="height:25px;width:25px"}
<center>**High-performance framework for uncertainty quantification of large-scale models.**</center>

### **Download**

Latest Release: 28/06/2019 - [Korali v1.0.0](https://github.com/cselab/korali.git) - Build Status: [![CircleCI](https://circleci.com/gh/cselab/korali.svg?style=svg&circle-token=d73f56a4d14073880f8fe1140964afb58f2b1c35)](install/build)

 + [Installation Guide](install/install.md)
 + [Release Notes](https://github.com/cselab/korali/blob/master/docs/RELEASE-NOTES)
 + [System Requirements](install/requirements.md)

### **What Korali Does**

??? abstract "Optimization (Constrained and Unconstrained)"
	Given any objective function $f:\mathbb{R}^N\rightarrow\mathbb{R}$ Korali can find its minima or maxima:

	$$\vartheta^\star = \mathop{\arg\min}\limits_{\vartheta}  f(\vartheta)$$

??? abstract "Distribution Sampling"
	Given any probability distribution of type $f:\mathbb{R}^N\rightarrow\mathbb{R}$, Korali can draw samples to determine its distribution: 
	
	$$\vartheta^{(k)} \sim f.$$

??? abstract "Bayesian Inference"
	Given a set of data $d$, the output of a computational model $f(x;\vartheta)$, a likelihood function $p(d|\vartheta)$, and a prior probability density $p(\vartheta)$ Korali will build the posterior distribution:

	$$ p(\vartheta | d)  =  \frac{p(d | \vartheta) p(\vartheta)}{p(d)} $$

	Allowing users to compute the maximum a posteriori estimate:

	$$\vartheta^\star = \mathop{\arg\min}\limits_{\vartheta}  p(\vartheta | d) $$

	Or sample its posterior distribution:

	$$\vartheta^{(k)} \sim p(\vartheta | d).$$

### **Design Principles**

??? success "High-Performance"

	Korali's work distribution engine has been optimized to fully harness computational resources of large-scale supercomputers, maximizing throughput and minimizing latency and load imbalance.
	
	Furthermore, Korali supports the execution of parallel (OpenMP, Pthreads), distributed (MPI, UPC++), and GPU-based (CUDA) models.
	
??? success "Ease of Use"
	Korali provides an intuitive string-based interface that is mostly language-independent.

??? success "Extensibility"

	Korali is designed as a completely modular and extensible software. Researchers can easily integrate and test new statistical methods for optimization and sampling into Korali. Likewise, new problems types can be easily added into Korali's engine.

??? success "Multi-Language"

	Korali applications can be programmed in either C++ or Python. Additionally, Korali can sample from C++/Fortran/Python and pre-compiled computational models.

??? success "Multi-Intrusiveness"

	A novelty in Korali is its support for multi-intrusive evaluation. That is, Korali can sample from computational models either semi-instrusively, through static linking or dynamic loading of Python modules; or nonintrusively, through shell command execution.