#!/usr/bin/python3

import os
import pickle

import wordnet_yaml


def save_pickle(wn, repo):
    pickle.dump(wn, open("%s/wn.pickle" % repo, "wb"))


def load_pickle(repo):
    return pickle.load(open("%s/wn.pickle" % repo, "rb"))


def load(repo):
    current_dir = os.getcwd()
    os.chdir(repo)
    wn = wordnet_yaml.load()
    os.chdir(current_dir)
    return wn


def save(wn, out_repo):
    synset_yaml = {}
    for synset in wn.synsets:
        s = {}
        if synset.ili and synset.ili != "in":
            s["ili"] = synset.ili
        s["partOfSpeech"] = synset.part_of_speech.value
        definitions = [wordnet_yaml.definition_to_yaml(wn, d) for d in synset.definitions]
        s["definition"] = definitions
        if synset.examples:
            examples = [wordnet_yaml.example_to_yaml(wn, x) for x in synset.examples]
            s["example"] = examples
        if synset.source:
            s["source"] = synset.source
        if synset.wikidata:
            s["wikidata"] = synset.wikidata
        for r in synset.synset_relations:
            if r.rel_type not in wordnet_yaml.ignored_symmetric_synset_rels:
                if r.rel_type.value not in s:
                    s[r.rel_type.value] = [r.target[wordnet_yaml.KEY_PREFIX_LEN:]]
                else:
                    s[r.rel_type.value].append(r.target[wordnet_yaml.KEY_PREFIX_LEN:])
        if synset.lex_name not in synset_yaml:
            synset_yaml[synset.lex_name] = {}
        synset_yaml[synset.lex_name][synset.id[wordnet_yaml.KEY_PREFIX_LEN:]] = s
        s["members"] = members(wn, synset)
        # BUG : these do not preserve order
        # s["members"] = entries_ordered(wn, synset.id)
        # s["members"] = wn.members_by_id(synset.id)
    for key, synsets in synset_yaml.items():
        with wordnet_yaml.codecs.open("%s/src/yaml/%s.yaml" % (out_repo, key), "w", "utf-8") as output:
            output.write(wordnet_yaml.yaml.dump(synsets, default_flow_style=False, allow_unicode=True))


def members(wn, synset):
    return [wn.id2entry[m].lemma.written_form for m in synset.members]
