# Additional notes covering the NER process

As per the model training, extracted entities were tokens representing the labels of ‘TYPE’, ‘COLOR’, ‘DATE’, ‘TIME’, ‘GPE’ and ‘LOC’. These corresponded to the database model fields as listed below:

- TYPE label, stored in the obs_types database field, representing type of observation
- COLOR label, stored in the obs_colors	database field, representing an associated colour of observation
- DATE label, stored in the obs_dates database field, representing an associated date of observation
- TIME label, stored in the obs_times database field, representing an associated time of observation
- GPE label, stored in the obs_locs database field,	representing an associated location of observation
- LOC label, stored in the obs_locs	database field, representing an associated place of observation

In cases where the location in the unstructured text fields contained two tokens representing one place – for example, a town and a US state like “Dayton, Ohio” - it was by default extracted as two distinct location entities by the NER model. It was decided that the desirability of that behaviour should a matter for the end user. Thus, a variable was provided in the da_settings.py file, named “restrict_duplicate_location_extractions", to allow configuration of that preference.

If set to “True”, “restrict_duplicate_location_extractions” informed the NER extraction process not to extract two distinct location entities if they appear immediately after one another, but instead to append such additional location entitles to the text of the first, separated by commas. This acts on an assumption that those entitles were likely to be related, due to their relative proximity in the text string. For example, the two entitles “Dayton” and “Ohio” would be combined to form the single location entity “Dayton, Ohio”, which would subsequently be geocoded accordingly.
