#!/usr/bin/python3

import os
import pickle

import wordnet_yaml


def load(repo):
    """ Load model from repo (home, not src/yaml dir)"""
    current_dir = os.getcwd()
    os.chdir(repo)
    wn = wordnet_yaml.load()
    os.chdir(current_dir)
    return wn


def save(wn, out_repo):
    """ Save model to repo (home, not src/yaml dir) """
    current_dir = os.getcwd()
    os.chdir(out_repo)
    wordnet_yaml.save(wn)
    os.chdir(current_dir)


def normalize(repo):
    """ Normalize repo (home, not src/yaml dir)"""
    for f in glob(f"{repo}/src/yaml/*.yaml"):
        data = yaml.load(open(f), Loader=yaml.CLoader)
        with open(f, "w") as out:
            out.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))


def load_pickle(path, file='wn.pickle'):
    """ Load model from pickle file in path """
    return pickle.load(open(f"{path}/{file}", "rb"))


def save_pickle(wn, path, file='wn.pickle'):
    """ Save model to pickle file in path """
    pickle.dump(wn, open(f"{path}/{file}", "wb"))
