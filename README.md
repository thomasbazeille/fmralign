# fmralign
Functional alignment and template estimation library for functional Magnetic Resonance Imaging (fMRI) data

This library is meant to be a light-weight Python library that handles functional alignment tasks. It is compatible with and inspired from [Nilearn](http://nilearn.github.io)
Alternative implementations of these ideas can be found in the [pymvpa](http://www.pymvpa.org) or [brainiak](http://brainiak.org) packages.

## Getting Started

### Prerequisites

fmralign requires a Python installation and the following dependencies:
* Python >= 3.6,
* Numpy >= 1.11
* SciPy >= 0.19
* Scikit-learn >= 0.19
* Matplotlib >= '1.5.0'
* Nibabel >= 2.0.2
* Nilearn >= 0.4

### Installing

Open a terminal window, go the location where you want to install it. Then run:

'''git clone
cd fmralign/
pip install -e .'''

If you plan to use optimal transport based method, you should also run:

'''pip install POT'''

You're up and running!

### Documentation

You can found an introduction about functional alignment `place_holder <http://brainiak.org>`.

## License

This project is licensed under the Simplified BSD License.

## Acknowledgments

This project has received funding from the European Union’s Horizon
2020 Research and Innovation Programme under Grant Agreement No. 785907
(HBP SGA2).
This project was supported by [Digiteo](http://www.digiteo.fr).
