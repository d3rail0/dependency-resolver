# Dependency resolver tool (DRT)

The dependency resolver tool consists of two main parts:
- **Dependency scanner** - scans all dependencies among your C/C++ project files.
- **Graph visualizer** - draws a hierarchical graph of the dependencies on the screen.

The scanner is used to obtain all includes from project files which are then used to form a directed cyclic or acyclic graph. Cycle (if present) is removed by reversing certain edges and topological order is computed at the same time. Graph with the altered state (in case of cycle presence) is passed to a node layering module that assigns nodes to different vertical layers and computes alternative traversal edges in case there are long edges by adding dummy vertices. Finally, graph and layering are passed to the graph visualizer where it is then rendered onto the screen.

The tool can be used to quickly find circular dependencies.

## Install instructions

Requires: **Python 3.7+**

#### Step 1
Open a terminal and navigate to where you extracted the DRT.

Example: `cd "G:\dependency-resolver-master\"`

#### Step 2
Run `pip install -r requirements.txt`
#### Step 3
Run `py main.py`

## How to use

Click on the *Select* button to select a directory containing C/C++ project files. The dependency scanner will get all the includes from files and create a hierarchical representation of project dependencies. Warnings will show in the bottom-left corner in case a cyclic dependency was detected. Besides, at least one of the edges that are in the cycle will be highlighted.

## Background

DRT is a small proof-of-concept tool developed for a semester project to show how the toposort algorithm could be practically used.

## Demo

![Project showcase](demo.gif)

## References

- https://www.tcs.uni-luebeck.de/downloads/papers/2011/2011-configurable-graph-drawing-algorithms-jannis-pohlmann.pdf
- http://atom3.cs.mcgill.ca/people/denis/atom3layout/files/DenisThesisTwoSideBook.pdf
- https://iris.polito.it/retrieve/handle/11583/2622803/326613/final.pdf
- https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/505558/1/thesis.pdf
- https://d-nb.info/1023081776/34 - Hierarchical Drawing of Directed Graphs
- https://publications.lib.chalmers.se/records/fulltext/161388.pdf

Websites: 
- https://pvigier.github.io/2018/02/09/dependency-graph.html
- https://deepsource.io/blog/introduction-static-code-analysis/
- http://www.logarithmic.net/pfh/blog/01208083168
- https://eli.thegreenplace.net/2011/07/03/parsing-c-in-python-with-clang
- https://davis.wpi.edu/~matt/courses/graphs/
- http://www.graphviz.org/documentation/TSE93.pdf
- https://llvm.org/devmtg/2010-11/Gregor-libclang.pdf
- http://faculty.cs.niu.edu/~freedman/340/340notes/340graph.htm
