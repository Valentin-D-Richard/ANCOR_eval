# Evaluation of ANCOR regarding anaphoric chains containing interrogative words

This repository gathers the commands and statistics realized on the spoken French corpus ANCOR for the study of anaphoric chains containing an interrogative word.

This repository falls under the CC-BY 4.0 licence.

## How to cite this work

This repository includes two separate studies that were published in the following publications:

* [1] Dynamic and Presuppositional Aspects of Questions. Valentin D. Richard, PhD thesis. 2025. Universiteit van Amsterdam and Université de Lorraine, Amsterdam, The Netherlands.
* [2] Évaluation d'un corpus annoté en anaphores, le cas des chaines contenant un mot interrogatif. Valentin D. Richard. In 6èmes journées du Groupement de Recherche CNRS “Linguistique Informatique, Formelle et de Terrain” (LIFT 2025), to appear, Paris, France, October 2025. CNRS 


## Requirements

For the commands to work, [ANCOR tei version](https://www.ortolang.fr/market/corpora/ortolang-000903) is supposed to be downloaded in the folder `corpus`. The file tree must therefore be:

```
ANCOR_eval
├──README.md
├──...
├───corpus
|   ├───corpus_ELSO
|   |   ├──004_-1.tei
|   |   └──...
|   ├───corpus_ELSO_CO2
|   |   └──...
|   ├───corpus_OTG
|   |   └──...
|   └───corpus_UBS
|       └──...
├──fudia
└──...
```

Python requirements: `lxml`, `pyconll`, `pandas`, `seaborn`, `csv`

## First study: How are the chains containing an interrogative annotated in ANCOR?

### Commands

Here is the command used to extract the non-trivial chains in ANCOR that contain a QU word as antecedent (feature `NEW=YES`), including both identity and associative (aka. bridging) chains. Chains that are strictly included in other chains or removed. This command only processes the ELSO subsorpus. It prints in markdown the sentences that contain the mentions in this chain and a given context window, formatted to highlight the mentions.

```bash
python3 extract1.py --incass --prooff corpus/corpus_ESLO > int_ana/new_ESLO.md
```

### Annotations

The identity chains were annotated by hand in the file `study1_annotations.ods`.

* `fileid`: id of the file
* ``chainid`: id of the chain
* `wh_context`: syntactic context of the interrogative
 * `hedge`: hedging device, e.g. `I would like to know whether [ Int ]`
 * `verb:...`: embedded under a verb, but not hedging
 * `q`: root interrogative
* `chain`: type of anaphoric relation with the mentions. See the second study for the classification.
* `first_ana_expr`: the first mention in the chain following the one containing the interrogative word
* `comment`: optional comment
* `pro`:
 * `1` if the first anaphoric expression is a pronoun
 * but `-` if the chain is excluded from the subcorpus because it is a propositional anaphora (`prop`), a domain anaphora (`domain`), a reparandum (`rep`) or the wh-word is embedded
* `inst`: Whether the sentence containing the first anaphoric expression also contains an instantiation of the wh-word. Only annotated for the part of the subcorpus where the first anaphoric expression is a demonstrative pronoun
 * `0`: no instantiation
 * `bridging`: instantiation annotated as a bridging anaphora
 * `coref`: instantiation annotated as a co-reference (i.e. identity chain)


## Second study: Evaluation of missing chains with an interrogative words

### Commands

Example for the directory corpus_OTG:

 1. Convert the files into conllu files, preserving the initial tokenization and putting the word ids as a Misc feature
  * `./export_text.py corpus/corpus_OTG`
  * `mkdir conllu/corpus_OTG`
  * `mv corpus/corpus_OTG/*.conllu conllu/corpus_OTG/`
 2. Upload all the files on Arborator-Grew
 3. Parse them with the parser fine-tuned on Rhapsodie and ParisStories (see FUDIA article cited in [2])
  * search for FUDIA: then takes the latest with LAS=0.8180 (FUDIA_eval_2023-09-13_16:56:24.726)
  * The Arborator repository for `UBS` can be browsed in https://arborator.grew.fr/#/projects/UD-ANCOR
 4. Download the parses in parser/corpus_OTG
 5. Apply FUDIA to obtain better annotations for interrogative words
  * `mkdir fudia/corpus_OTG`
  * `./fudia.sh parsed/corpus_OTG/ -o fudia/corpus_OTG/`

### Annotation

The `stats2.ipynb` python notebook was used to extract the chains (given by the tei files) that contain an interrogative word (feature `PronType='Int'`in the fudia files). The notebook also generates formatted markdown files displaying the chains withing a context window (necessary to properly annotated the chains). Finally, the notebook presents statistics and charts to assess the number of chains of each type (annotated in ANCOR `inchain.csv` or missing: missing but in a lone mention `notinchain` or missing and not even annotated as a mention `notmentioned`). The file `count2.ods` summarizes the occurrence numbers for the table presented in publication [2].

Here is the annotation schema for the csv files `notmentioned.csv`, `notinchain.csv` and `inchain_noquel.csv`.

False positives `fp`:
 * `nimporte`, e.g. *n'importe où*
 * `rsa`: relative word in a free relative
 * `rel`: relative word with an antecedent
 * `disc`: discourse marker, e.g. *quoi*
 * `ceque`: present in a *ce que/qui* expression
 * `excl`: exclamative
 * `trans`: transcription mistake
 * `expr`: in a fixed expression, e.g. *quoi que des fois...*, *je sais pas quoi*

Syntactic context of the wh word `wh_context`:
 * `q` : root question
 * embedding `verb:` + verb lemma
 * `hedge`: hedging, ex. *Est-ce que vous pouvez me dire quel est le montant d'une bourse?*
 * `rep`: reparandum: included in the previous chain
 * `quoted`: word used in an expression in the meta-language, not annotated, e.g. *je ne sais plus quel mot employer*
 * `cond`: conditional question
   * `ex`: conditional on the existence of a non-null answer

Anaphoric chains `chain`: (separated by semi-columns) -> glossed in bold in the file
 * `0`: no (in a lookup window of 20 sentences)
 * `sta`: singleton exhaustive true answer
   * `asker`: answered by the asker
   * `gq`: answer is a generalized quantifier, e.g. *A: **qui** est -ce qui s' en sert le plus souvent à la maison ? B: bah un peu **tous**.*
 * `plta` (pair) list of true answers, e.g.
   * *A: où est-ce que vous les gardez ?*
   * *B: à l'entrée*
   * *A: et puis les autres*
   * *B: les enfants ont dans leur bibliothèque*
 * `pta`: possible true answer:
   * `modadv`: with a modal adverb in the answer
   * `cond`: exemple given under the antecedent of a conditional
   * `q`: exemple given a subsequent question
   * `unsure`: expresses some uncertainty later in the discourse, e.g. *je sais pas*
   * `dep`: gives one or several potential answers based on a dependence factor, e.g. 
     * in a way, (pair) list readings and dependent answers can be seen as special cases of quantified answers, using a quantification provided in the question or brought up by the responder
   * `modatt`: under a modal attitude, e.g. *je crois que X*
   * `modverb`: modal verb, e.g. *ce serait X*
   * `neg`: under a negation
 * mention-some answer(s) `ms`
 * `spec`: specific mention in the subsequent discourse
   * `dem`: the referring expression is a demonstrative NP or pronoun
   * `def`: a definite article or NP
   * `poss`: a possessive pronoun or determiner
 * `cta` conjunction of true answer
 * `cest`: demonstrative pronoun introducing an answer in a copular sentence, typically with *c'est X*
 * `dta`: disjunction of true answers
   * `irr`: irrelevance (high scope)
   * `ign`: ignorance (high scope)
   * `qg`: low scope under a model or other quantifier
 * `nonspec`: non specific (lower scope) indefinite, e.g.
   * ***quelle*** *est la personne qui parle le meilleur français ?*
   * *vous ne voyez pas **quelqu'un** qui*
   * ----
   * ***quel genre de chose*** *oui vous avez dit cela dé- est -ce qu' il y a **des mots** que vous interdisez de prononcer à vos enfants ?*
 * `rep`: interrogative word repeated
 * `gq`: generalized quantifier or pronoun (not in a `sta`)
 * `domain`: domain of quantification
 * `rhet`: rhetorical question: the identity of the individual is deducible from the context

Comment `comment` (may be underannotated):
 * degree questions `degree`: e.g. *à quel point*, usually not answered with a degree, but with examples of things -> annotated as 0 in that last case
 * propositional interrogative word `prop`, e.g. *ça tient à quoi ?* -> annotated as 0 if the answer is a whole explanation, and not just 1 clause
 * `negociation`: common to discuss the potential answers, and to reject them -> should that count as a form of local context, then evaluating to the actual world
 * `parexemple`: *par exemple*
 * `null`: direct or indirect null answer
 * `clar`: answer to a clarification question
 * `rep`: reparandum (file `026_C-3` and after), but the question can still be reconstructed and, if applicable, be in a chain with the answers given to the repaired question
 * `discont`: discontinuous mention, spanning on several speech turns
 * `gran`, granularity increase, e.g.
 * *euh ça se passera **[où]** ?*
 * *c' est euh enfin c' est **à Orléans** c' est juste **à côté du place De Gaulle**.*
* `presuppneg`: negation of a presupposition of the question
* `mismatch`: ontological mismatch between the question's variable and the actual answer (although it could be inferred / coerced), e.g.
* *et jusqu' à **[quel âge]** est -ce qu' il faudrait que les enfants continuent leurs études ?* -> asked: an age
 * *ben je crois que ben le plus longtemps possible.* -> given: a time
* `qreading`: asks about the reading / details about a question
* `genmod`: quantificational force adverbs like *surtout, plutôt*
* `notnew`: the wh-word is not the first mention in the chain

In `inchain_noquel.csv`, the column `actual` contains my annotation regarding the annotation given by ANCOR. The possible values are the same as for the column `chain`. 

### Observations

Markers to indicate mention-some answers: *(il) y a*, *(des X) comme ça*, *par exemple*, *quels genres de X* e.g.
 * *bon alors écoutez e ça il y a **quoi** dedans.*
 * *c' est un guide d' informations sur la ville donc **ce qu' on peut trouver dans la ville** **les musées** **les choses comme ça**.*
But sometimes, it's hard to tease apart a conjunctive list of true answer from a list of mention-some answers. Although the question is open to mention-some answers, the responder might be exhaustive.

Among *quel*, a vast majority of adjective *quel* in copular questions are not in a mention.
A large among of *quel genre de* are not in a chain.

Some bad annotations of discourse marker *quoi* anchor relation lead to an incorrect annotation as PronType=Int by FUDIA, especially after an adverb or in long sentences

Example general questions:
 * Quel est votre avis sur la question ?
 * Quel est la différence entre le droite et la gauche, selon vous ?

Some false negatives due to incorrect PronType=Ind (e.g. on *quoi*) by the parser.

---

Usually, the responder makes explicit a reading or detail unspecified in the question, or changes the interpretation to something they can answer, e.g. 
 * quel est le plus difficile pour un étranger dans la langue française ?.
 * la prononciation **pour moi**

Example split into 2 readings and answering each reading
 * *et parmi vos connaissances **quelle** est la personne qui parle le mieux le français ?*
 * *qui parle le mieux c'est-à-dire **qui** s' exprime le plus clairement ou **qui** a le français le plus pur ?*
	* *euh les deux si vous pouvez les ?*
	* *non c' est j- non c' est deux personnes différentes pour moi.*
	* *ah bon c' est bon alors.*
	* *c' est **quelqu'un de ma famille** pour le français le plus pur et le plus clairement c' est **un de mes collègues de Paris**.*

Should they be annotated as two different chains, one for each reading?
Currently, ANCOR would annotate each as associative, and demonstratives as co-references, as in the following (but *une petite école de campagne* is missing)
 * *et ils avaient été à l' école dans une des dans quel euh dans **[quel type d' école]_u** **[c']_u** était **[[une école publique]_u'** **privée]_u''** ?*
 * ***[c']_u*** *était **[une petite école de campagne]_?** sûrement.*

Should anaphora be about individuals or identities ?
Same problem with indefinites: we can talk about different granularities, identification methods

---

Some interrogative words can be in several mentions, e.g. *à [la suite de [quelle circonstance]]*. In this example, only *quelle circonstance* is in a non-trivial chain.

Other difficulties: questions asking about the reading of a question, e.g.
 * *oui alors qu' est -ce qui compte le plus pour vous dans votre travail ?*
 * *n- a à **quel point de vue** ?*
 * *ah c'est-à-dire qu' est -ce qui.*
 * *qu' est -ce que je préfère faire ?*
 * *oui oui oui c' est ça ah bon ?*

Some questions ask for complex propositions, e.g.
 * *les différences dans la façon de parler c' est **quel genre de différences** enfin vous voyez ? [...]*
	* *ben **y a des personnes qui ne sauront vous parler que euh que du temps que euh que de leurs voisins euh des choses euh banales tout à fait**.*
	* *hm ?.*
	* *et puis alors par contre euh **vous avez des personnes qui qui s' intéressent à à beaucoup de choses** [...]*


