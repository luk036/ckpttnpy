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
#   * `--citeproc` resolves the paper's `[@key]` citations against ckpttn.bib
#     with the vendored ieee.csl style (numeric `[1]`), so the bibliography is
#     generated rather than hand-maintained. Both files are prerequisites, and
#     `nocite: @*` in the front matter keeps entries that are listed for
#     further reading but not cited in the text.
#   * Tables are written as raw LaTeX (`{=latex}` blocks) because pandoc pipe
#     tables become `longtable`, which IEEEtran's two-column mode rejects.

PANDOC := pandoc
FLAGS  := -s -t latex -N --shift-heading-level-by=-1 --pdf-engine=pdflatex --citeproc

# Citation inputs: the BibTeX database and the CSL style. Changing either must
# rebuild the PDF, so both are prerequisites of the rule below.
BIB := ckpttn.bib ieee.csl

# Figure PDFs live under figs/ and are \includegraphics'd by ckpttn-paper.md.
# They must be prerequisites, or `make` will not rebuild the paper when a
# figure is regenerated (the .md itself looks unchanged).
FIGURES := figs/p1-2way.pdf figs/p1-3way.pdf \
           figs/fig_cut.pdf figs/fig_gain.pdf figs/fig_ratio.pdf figs/fig_runtime.pdf

.PHONY: ckpttn-paper ckpttn-talk clean

ckpttn-paper: ckpttn-paper.pdf

ckpttn-paper.pdf: ckpttn-paper.md $(FIGURES) $(BIB)
	$(PANDOC) $(FLAGS) ckpttn-paper.md -o $@

# ckpttn-talk.md -> ckpttn-talk.pdf (Beamer slides).
# Why these flags:
#   * LuaLaTeX is required: the deck keeps emoji, which need a font fallback
#     registered in preamble.tex.
#   * `--include-in-header` MUST be a command-line flag; setting it from YAML
#     metadata is silently ignored.
#   * pandoc writes the .tex first, then LuaLaTeX runs twice so that the
#     `\tableofcontents` outline is populated on the second pass.
#   * `--slide-level=2`: `#` = \section, `##` = frame.
LUALATEX   := lualatex
TALK_FLAGS := -t beamer --slide-level=2 --include-in-header=preamble.tex

ckpttn-talk: ckpttn-talk.pdf

ckpttn-talk.tex: ckpttn-talk.md preamble.tex $(FIGURES)
	$(PANDOC) $(TALK_FLAGS) ckpttn-talk.md -o $@

ckpttn-talk.pdf: ckpttn-talk.tex
	$(LUALATEX) -interaction=nonstopmode -halt-on-error ckpttn-talk.tex
	$(LUALATEX) -interaction=nonstopmode -halt-on-error ckpttn-talk.tex

# Trailing `; true` forces make to run these through a shell; `rm` is not an
# .exe on Windows, where make may otherwise fail to exec it directly.
clean:
	-@rm -f ckpttn-paper.tex ckpttn-paper.aux ckpttn-paper.log ckpttn-paper.out ckpttn-paper.toc \
		ckpttn-talk.tex ckpttn-talk.aux ckpttn-talk.log ckpttn-talk.out ckpttn-talk.toc ckpttn-talk.nav ckpttn-talk.snm ; true
