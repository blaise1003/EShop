Script di servizio. Permette di generare i template in HTML con degli inclusion tag.

Parte dall'esigenza di Cinzia di avere dei template "dinamici" nel momento in cui ha iniziato a skinnare per XDV.

Per utilizzarlo basta semplicemente:

. creare i template html in source_templates
. nel template html includere snippet esterni con la seguente riga: @@include "nomefile.html"
. in snippets creare il file nomefile.html
. l'inclusion è ricorsiva per cui in nomefile.html possono trovarsi altri @@include
. lanciare il compile.py
. per ogni template in source_templates verrà creato nella cartella un template con tutte le sostituzione

Basta eseguire il comando: python bin/compile.py

Prerequisiti
------------
Per utilizzare le diverse funzionalità lo script necessita dei seguenti pacchetti
aggiuntivi:

* BeautifulSoup
* cssmin

Per installare le dipendenze eseguire il comando:

$ easy_install BeautifulSoup && easy_install cssmin

LESS
====
Per gestire in modo più efficace i CSS è stata aggiunta la possibilità di utilizzare less.js (http://lesscss.org/)
basato su node.js (http://nodejs.org/)

Per abilitare il supporto di less lanciare lo script:

$ /bin/sh bin/enable_less.sh

verrà creata la cartella ./less con all'interno tutto l'occorrente per la compilazione dei file ".less"

A questo punto è possibile inserire i file ".less" in /static/theme/styles e verranno automaticamente compilati dal compile.py in file .css


SERVE
========
E' possibile utilizzare la modalità "serve".
Lanciando il comando

$ python bin/serve.py

Verrà avviato un server sulla porta 8000.

A questo punto sarà possibile accedere con il browser all'indirizzo:

http://localhost:8000/

Ad ogni refresh del browser il sistema provvederà a ricompilare il template ed i css coinvolti, rendendo inutile eseguire
il compile.py manualmente 

PRODUZIONE
---------------
All'atto della messa online si consiglia di compilare il tema nel seguente modo:

$ python bin/compile.py -m -p

in modo da:

-p -> eseguire il prettify del codice
-m -> minimizzare il css

That's all folks :)

DUMP
===========
E' possibile per lo sviluppatore mettere a disposizione del grafico i template
statici dumpati dalla sua istanza o dallo staging per facilitarne lo skinning.

Per fare ciò basta elencare nel file dump.cfg, nella folder dumped_templates, 
l'elenco delle url da dumpare con relativo nome del template, nel seguente formato:

index.html = http://biagiogrimaldi.netsons.org

e lanciare il comando

python bin/dump.py

RISORSE STATICHE
===============
Nel linkare le risorse statiche fare attenzione a questo aspetto.

Se il tema è per plone (da utilizzare con plone.app.theming) le risorse
statiche (css/js) vanno riferite con url relative ("./static/...").

Se il tema è per django o simili vanno utilizzate url assolute ("/static/...")

In entrambi i casi il bin/serve.py funzionerà correttamente nel rendere i
template.
