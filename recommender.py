#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para cálculo de recomendaciones
'''
from datastore import *

def get_recommendations(values):
    recommendations = []
    for value in values:
        query = data_handler.retrieve_data_for(value)
        for artist in query:
            local_recommendations = artist.similar_groups
            recommendations = list(set().union(recommendations,local_recommendations))
    return recommendations
