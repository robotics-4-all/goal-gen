# goal-gen

This package includes the code-generator for Goal-DSL, that uses Goalee library to implement
the validation software.

# Table of contents
1. [Installation](#installation)
2. [Usage](#usage)


## Installation

Download this repository and simply install using `pip` package manager.

```
git clone https://github.com/robotics-4-all/goal-gen
cd goal-gen
pip install .
```

## Usage

This generator is provided via `textx` for generating the source code from given input goaldsl
model. An example of using the cli is given below:

```
textx generate target.goal --target goalee
```