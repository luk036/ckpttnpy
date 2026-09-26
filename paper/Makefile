# Build entry point for the papers in this directory.
#
# ckpttn-paper.md -> ckpttn-paper.pdf (two-column IEEEtran).
# Requires: pandoc and a LaTeX engine with pdflatex.
#
# Why these flags:
#   * `documentclass: IEEEtran` (in the .md front matter) gives the two-column
#     IEEE layout and the I/II/... section numbering.
#   * `--shift-heading-level-by=-1` maps the body's `##` headings to \section
#     (the title is metadata, so no `\section` would be emitted otherwise).
#   * No pandoc-crossref/citeproc: the paper uses no `@`-cross-references, and
#     its numbered reference list is plain text. Tables are written as raw
#     LaTeX (`{=latex}` blocks) because pandoc pipe tables become `longtable`,
#     which IEEEtran's two-column mode rejects.

PANDOC := pandoc
FLAGS  := -s -t latex -N --shift-heading-level-by=-1 --pdf-engine=pdflatex

# Figure PDFs live under figs/ and are \includegraphics'd by ckpttn-paper.md.
# They must be prerequisites, or `make` will not rebuild the paper when a
# figure is regenerated (the .md itself looks unchanged).
FIGURES := figs/p1-2way.pdf figs/p1-3way.pdf \
           figs/fig_cut.pdf figs/fig_gain.pdf figs/fig_ratio.pdf figs/fig_runtime.pdf

.PHONY: ckpttn-paper clean

ckpttn-paper: ckpttn-paper.pdf

ckpttn-paper.pdf: ckpttn-paper.md $(FIGURES)
	$(PANDOC) $(FLAGS) ckpttn-paper.md -o $@

# Trailing `; true` forces make to run these through a shell; `rm` is not an
# .exe on Windows, where make may otherwise fail to exec it directly.
clean:
	-@rm -f ckpttn-paper.tex ckpttn-paper.aux ckpttn-paper.log ckpttn-paper.out ckpttn-paper.toc ; true
