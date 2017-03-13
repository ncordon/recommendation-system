DIAGRAMS_FOLDER:=./diagramas
DIAGRAMS:=$(patsubst $(DIAGRAMS_FOLDER)/%.dia, $(DIAGRAMS_FOLDER)/%.png, $(wildcard $(DIAGRAMS_FOLDER)/*.dia))

PDF:=./memoria.pdf

all: $(DIAGRAMS) $(PDF)

%.png: %.dia
	dia $< -e $@ -t png

%.pdf: %.md	$(DIAGRAMS)
	pandoc -V lang=spanish $< -o $@  --template default.latex -N
