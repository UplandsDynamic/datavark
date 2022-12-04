import spacy


class Ner:

    """
    Run the NER processes
    """

    nlp = None
    data = []

    def __init__(self, model_name="", model_url="", doc_texts=[]):
        if model_url and doc_texts and model_name == "trf-model-best-tuned":
            self.data = doc_texts
            # swap in untrained components from original model (fixes spaCy frozen components bug)
            self.nlp = spacy.load(
                model_url, exclude="parser,tagger,attribute_ruler,lemmatizer"
            )
            nlp_trf_orig = spacy.load("en_core_web_trf")
            self.nlp.add_pipe("parser", source=nlp_trf_orig, after="transformer")
            self.nlp.add_pipe("tagger", source=nlp_trf_orig, after="parser")
            self.nlp.add_pipe("attribute_ruler", source=nlp_trf_orig, after="tagger")
            self.nlp.add_pipe(
                "lemmatizer", source=nlp_trf_orig, after="attribute_ruler"
            )

    def get_entities(self):
        extracted_entities = []
        processed_doc = None
        for doc in self.data:
            processed_doc = self.nlp(doc)
            ents = []
            if processed_doc.ents:
                for ent in processed_doc.ents:
                    ents.append((ent.text, ent.label_))
            else:
                ents.append(("NO-ENTS", "NONE"))
            extracted_entities.append(ents)
        return extracted_entities
