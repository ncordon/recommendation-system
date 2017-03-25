DIAGRAMS_FOLDER:=./diagramas
DIAGRAMS:=$(patsubst $(DIAGRAMS_FOLDER)/%.dia, $(DIAGRAMS_FOLDER)/%.png, $(wildcard $(DIAGRAMS_FOLDER)/*.dia))

PDF:=./arquitectura.pdf ./presupuesto.pdf

all: $(DIAGRAMS) $(PDF)

%.png: %.dia
	dia $< -e $@ -t png

%.pdf: %.md	$(DIAGRAMS)
	pandoc -V lang=spanish $< -o $@  --template default.latex -N

clean:
	rm -r $(PDF)
