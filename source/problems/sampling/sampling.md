In a *Sampling* problem, the computational model is assumed to be of the form: $f:\mathbb{R}^N\rightarrow\mathbb{R}$, where $N$ is the number of variables, as defined by the user. Given a set of values for the variables (a sample), the model produces a single real value containing the direct evaluation of $f(x)$. 

** Usage **

```python
  k["Problem"] = "Sampling"
```

##Requirements

+ A [Simple](/usage/models/simple) computational model should be defined.
+ At least one variable should be defined.

## Configuration

### Problem Settings
 
### Variable-Specific Settings