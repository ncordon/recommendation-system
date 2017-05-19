#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para cálculo de recomendaciones
'''
from datastore import *

def get_recommendations(values):
    recommendations = []
    
    for value in values:
        artist = data_handler.retrieve_data_for(value)
        local_recommendations = artist.similar_groups
        recommendations = list(set().union(recommendations, local_recommendations))

    return recommendations
