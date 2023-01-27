import spacy, logging

logger = logging.getLogger("django")


class Ner:

    """
    Run the NER processes
    """

    def __new__(
        cls, model_name="", model_url="", data_dict=[], restrict_loc_dupes=True
    ):
        obj = super().__new__(cls)
        obj._data_dict = data_dict
        obj._restrict_loc_dupes = restrict_loc_dupes
        obj._get_text()
        obj._init_ner(model_url, model_name)
        obj._get_entities()
        obj._add_ents_to_data()
        return obj._data_dict

    def _init_ner(self, model_url, model_name):
        if model_url and self.doc_texts and model_name == "trf-model-best-tuned":
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

    def _get_entities(self):
        logger.info(f"Running NER on acquired data ...")
        self.extracted_entities = []
        processed_doc = None
        for doc in self.doc_texts:
            processed_doc = self.nlp(
                doc.lower()
            )  # lower case all characters. Found through trial & error to work best.
            ents = []
            if processed_doc.ents:
                for ent in processed_doc.ents:
                    end_char_pos_of_last_loc_ent = 0
                    valid_location_ents = ("GPE", "LOC", "PLACE")
                    processed_doc = self.nlp(doc.lower())
                    # restrict extracting cities & states as separate entities, etc
                    if ent.label_ in valid_location_ents:
                        if (
                            not self._restrict_loc_dupes
                            or ent.start
                            not in range(
                                (end_char_pos_of_last_loc_ent + 1),
                                (end_char_pos_of_last_loc_ent + 5),
                            )
                            or not end_char_pos_of_last_loc_ent
                        ):
                            ents.append((ent.text, ent.label_))
                            end_char_pos_of_last_loc_ent = ent.end
                        else:  # append to previous loc ent for geocoding, as likely to be state
                            ents[-1] = (ents[-1][0] + f", {ent.text}", ents[-1][1])
                    else:
                        ents.append((ent.text, ent.label_))
            else:
                ents.append(("NO-ENTS", "NONE"))
            self.extracted_entities.append(ents)

    # function to extract the raw text from the data
    def _get_text(self):
        self.doc_texts = []
        for doc in self._data_dict:
            self.doc_texts.append(doc["text"])

    # function to add the extracted entities to the data
    def _add_ents_to_data(self):
        for doc, ents in zip(self._data_dict, self.extracted_entities):
            doc["entities"] = ents
