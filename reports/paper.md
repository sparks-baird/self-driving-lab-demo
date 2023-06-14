---
title: 'self-driving-lab-demo: A Python and MicroPython package for controlling an autonomous research laboratory'
tags:
  - Python
  - materials informatics
  - self-driving lab
  - automation
  - materials science
  - chemistry
authors:
  - name: Sterling G. Baird
    orcid: 0000-0002-4491-6876
    equal-contrib: false
    corresponding: true
    affiliation: "1" # (Multiple affiliations must be quoted)
  # - name: Kevin M. Jablonka
  #   orcid: 0000-0003-4894-4660
  #   affiliation: "3"
  - name: Hasan M. Sayeed
    orcid: 0000-0002-6583-7755
    equal-contrib: false
    affiliation: "1" # (Multiple affiliations must be quoted)
  # - name: Mohammed Faris Khan
  #   equal-contrib: false
  #   orcid: 0000-0001-7527-6368
    # affiliation: "1" # (Multiple affiliations must be quoted)
  # - name: Colton Seegmiller
  #   orcid: 0000-0001-9511-2918
  #   equal-contrib: false
  #   affiliation: "4" # (Multiple affiliations must be quoted)
  - name: Taylor D. Sparks
    orcid: 0000-0001-8020-7711
    equal-contrib: false
    affiliation: "1" # (Multiple affiliations must be quoted)
affiliations:
 - name: Materials Science & Engineering, University of Utah, USA
   index: 1
 - name: Computer Science, University of Southern California, USA
   index: 2
 - name: Laboratory of Molecular Simulation (LSMO), Institut des Sciences et Ingénierie Chimique, École Polytechnique Fédérale de Lausanne, Switzerland
   index: 3
 - name: Computer Science, Utah Valley University, USA
   index: 4
date: 28 July 2022
bibliography: paper.bib

# # Optional fields if submitting to a AAS journal too, see this blog post:
# # https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

The latest advances in machine learning are often in natural language processing such as with long
short-term memory networks (LSTMs) and Transformers, or image processing such as with
generative adversarial networks (GANs), variational autoencoders (VAEs), and guided
diffusion models. `xtal2png` encodes and decodes crystal structures via PNG
images (see e.g. \autoref{fig:64-bit}) by writing and reading the necessary information
for crystal reconstruction (unit cell, atomic elements, atomic coordinates) as a square
matrix of numbers. This is akin to making/reading a QR code for crystal
structures, where the `xtal2png` representation is an invertible representation. The
ability to feed these images directly into image-based pipelines allows you, as a
materials informatics practitioner, to get streamlined results for new state-of-the-art
image-based machine learning models applied to crystal structures.

![A real size $64\times64$ pixel `xtal2png` representation of a crystal structure.\label{fig:64-bit}](figures/Zn8B8Pb4O24,volume=623,uid=bc2d.png)

# Statement of need

Using a state-of-the-art method in a separate domain with a custom data representation
is often an expensive and drawn-out process. For example, [@vaswaniAttentionAllYou2017]
introduced the revolutionary natural language processing Transformer architecture in
June 2017, yet the application of Transformers to the adjacent domain of materials
informatics (chemical-formula-based predictions) was not publicly realized until late
2019 [@goodallPredictingMaterialsProperties2019], approximately two-and-a-half years
later, with peer-reviewed publications dating to late 2020
[@goodallPredictingMaterialsProperties2020]. Interestingly, a nearly identical
implementation was being developed concurrently in a different research group with
slightly later public release [@wangCompositionallyrestrictedAttentionbasedNetwork2020]
and publication [@wangCompositionallyRestrictedAttentionbased2021] dates. Another
example of a state-of-the-art algorithm domain transfer is refactoring image-processing
models for crystal structure applications, which was first introduced in a preprint
[@kipfSemisupervisedClassificationGraph2016] and published with application for
materials' property prediction in a peer-reviewed journal over a year later
[@xieCrystalGraphConvolutional2018]. Similarly, VAEs were introduced in 2013
[@kingmaAutoEncodingVariationalBayes2014a] and implemented for molecules in 2016
[@gomez-bombarelliAutomaticChemicalDesign2016], and denoising diffusion probabilistic
models (DDPMs) were introduced in 2015 [@sohl-dicksteinDeepUnsupervisedLearning2015] and
implemented for crystal structures in 2021 [@xieCrystalDiffusionVariational2021]. Here,
we focus on state-of-the-art domain transfer (especially of generative models) from
image processing to crystal structure to enable materials science practitioners to
leverage the most advanced image processing models for materials' property prediction
and inverse design.

`xtal2png` is a Python package that allows you to convert between a crystal structure
and a PNG image for direct use with image-based machine learning models. Let's take
[Google's image-to-image diffusion model,
Palette](https://iterative-refinement.github.io/palette/)
[@sahariaPaletteImagetoImageDiffusion2022a], which supports unconditional image
generation, conditional inpainting, and conditional image restoration, which are modeling tasks
that can be used in crystal generation, structure prediction, and structure
relaxation, respectively. Rather than dig into the code and spending hours, days, or
weeks modifying, debugging, and playing GitHub phone tag with the developers before you
can (maybe) get preliminary results, `xtal2png` lets you get comparable results using the default parameters, assuming the instructions can be run without
error. While there are other invertible representations for crystal structures
[@xieCrystalDiffusionVariational2022;@renInvertibleCrystallographicRepresentation2022a]
as well as cross-domain conversions such as converting between molecules and strings
[@weiningerSMILESChemicalLanguage1988;@selfies], to our knowledge, this is the first
package that enables conversion between a crystal structure and an image file format.

![(a) upscaled example image and (b) legend of the `xtal2png` encoding.\label{fig:example-and-legend}](figures/example-and-legend.png)

`xtal2png` was designed to be easy to use by both
"[Pythonistas](https://en.wiktionary.org/wiki/Pythonista)" and entry-level coders alike.
`xtal2png` provides a straightforward Python application programming interface (API) and
command-line interface (CLI). `xtal2png` relies on `pymatgen.core.structure.Structure`
[@ongPythonMaterialsGenomics2013] objects for representing crystal structures and also
supports reading crystallographic information files (CIFs) from directories. `xtal2png`
encodes crystallographic information related to the unit cell, crystallographic
symmetry, and atomic elements and coordinates which are each scaled individually
according to the information type. An upscaled version of the PNG image and a legend of
the representation are given in \autoref{fig:example-and-legend}. Due to the encoding of
numerical values as PNG images (allowable values are integers between 0 and
255), a round-off error is present during a single round of encoding and decoding.
An example comparing an original vs. decoded structure is given in
\autoref{fig:original-decoded}.

There are some limitations and design considerations for `xtal2png` that are described
in `xtal2png`'s [documentation](https://xtal2png.readthedocs.io/en/latest/index.html) in
the Overview section.
At this time, it is unclear to what extent deviation from the aforementioned design
choices will affect performance. We intend to use hyperparameter optimization to
determine an optimal configuration for crystal structure generation tasks using the
`xtal2png` representation.

![(a) Original and (b) `xtal2png` decoded visualizations of
[`mp-560471`](https://materialsproject.org/materials/mp-560471/) / Zn$_2$B$_2$PbO$_6$. Images were generated using [ase visualizations](https://wiki.fysik.dtu.dk/ase/ase/visualize/visualize.html). \label{fig:original-decoded}](figures/original-decoded.png){ width=50% }

The significance of the representation lies in being able to directly use the PNG
representation with image-based models which often do not directly support custom
dataset types. We expect the use of `xtal2png` as a screening tool for such models to
save significant user time of code refactoring and adaptation during the process of
obtaining preliminary results on a newly released model. After obtaining preliminary
results, you get to decide whether it's worth it to you to take on the
higher-cost/higher-expertise task of modifying the codebase and using a more customized
approach. Or you can stick with the results of xtal2png. It's up to you!

We plan to apply `xtal2png` to a probabilistic diffusion generative model as a
proof of concept and present our findings in the near future.

<!-- ![Caption for example figure.\label{fig:example}](figure.png) -->

<!-- # Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text. -->

<!--
# Citations
Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)" -->

<!-- # Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% } -->

# Acknowledgements

S.G.B. and T.D.S. acknowledge support by the National Science Foundation, USA under
Grant No. DMR-1651668. H.M.S.and T.D.S.  acknowledge support by the National Science
Foundation, USA under Grant No. OMA-1936383. C.S. and T.D.S. acknowledge support by the
National Science Foundation, USA under Grant No. DMR-1950589.  K.M.J. and B.S.
acknowledge support by the MARVEL National Centre for Competence in Research funded by
the Swiss National Science Foundation (grant agreement ID 51NF40-182892).

# References
