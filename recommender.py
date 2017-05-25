#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para cálculo de recomendaciones
'''
from datastore import *

total_recommendations = 30

def get_recommendations(values):
    request_queue = Queue.Queue()
    values = filter(None, values)
    threads = []
    recommendations = []
    union_recommendations = []
    intersect_recommendations = []
    
    if len(values) > 0:
        rec_per_group = total_recommendations/len(values)
        
    for i in range(len(values)): 
        threads.append( Thread(target = data_handler.retrieve_recommendations,
                              args = [values[i], rec_per_group, request_queue]) )
        threads[i].start()

    for thread in threads:
        thread.join()

    #############################################################
    # Obtenemos las tres listas de recomendaciones de cada grupo 
    # y realizamos la intersección y union de las mismas.
    #############################################################

    first = True
    while not request_queue.empty():
        local_recommendations = request_queue.get()
        union_recommendations = list(set().union(union_recommendations, local_recommendations))
        if first == True:        
            intersect_recommendations = list(local_recommendations)
        else:
            intersect_recommendations = list(set().intersection(intersect_recommendations, local_recommendations))
        first == False

    #############################################################
    # Para cada grupo que no este en la intersección de las listas
    # comprobamos su parecido haciendo uso de sus tags, géneros y 
    # el año
    #############################################################

    union_recommendations = list(set(union_recommendations) - set(intersect_recommendations))

    for recommendation in union_recommendations:
        similarity_genres = 0
        similarity_tags = 0
        for value in values:
            similarity_genres += mean_similarity_genres_of(value, recommendation)
            similarity_tags += mean_similarity_tags_of(value, recommendation)

        similarity_genres = similarity_genres / len(values)
        similarity_tags = similarity_tags / len(values)

        if similarity_tags >= 70 or similarity_genres >= 70:
            recommendations.append(recommendation)
     
    #############################################################
    # Añadimos a las recomendaciones la intersección.
    #############################################################

    recommendations = list(set().union(recommendations, intersect_recommendations))

    #############################################################
    # Eliminamos de la lista los grupos buscados.
    #############################################################

    recommendations = list(set(recommendations) - set(values))

    return recommendations

def mean_similarity_genres_of(artist, recommended_artist):
    genres_similarity = 0
    groups = Group.query(projection = ['name'])
    most_similar = data_handler.most_similar_from_to(groups, artist)
    recommended_most_similar = data_handler.most_similar_from_to(groups, recommended_artist)
    
    if most_similar and recommended_most_similar:
        genres = data_handler.retrieve_data_for(artist).genre
        recommend_genres = data_handler.retrieve_data_for(recommended_artist).genre

        for genre in genres:
            max_similarity = 0
            for recommend_genre in recommend_genres:
                similarity = fuzz.ratio(genre.lower(), recommend_genre.lower())
                if similarity >= max_similarity:
                    max_similarity = similarity
        
            genres_similarity += max_similarity
    
        if len(genres) != 0:
            genres_similarity = genres_similarity / len(genres)
        else:
            genres_similarity = 0
    else:
        genres_similarity = 100

    return genres_similarity


def mean_similarity_tags_of(artist, recommended_artist):
    tags_similarity = 0
    groups = Group.query(projection = ['name'])
    most_similar = data_handler.most_similar_from_to(groups, artist)
    recommended_most_similar = data_handler.most_similar_from_to(groups, recommended_artist)
    
    if most_similar and recommended_most_similar:
        tags = data_handler.retrieve_data_for(artist).tags
        recommend_tags = data_handler.retrieve_data_for(recommended_artist).tags

        for tag in tags:
            max_similarity = 0
            for recommend_tag in recommend_tags:
                similarity = fuzz.ratio(tag.lower(), recommend_tag.lower())
                if similarity >= max_similarity:
                    max_similarity = similarity
        
            tags_similarity += max_similarity
    
        if len(tags) != 0:
            tags_similarity = tags_similarity / len(tags)
        else:
            tags_similarity = 0
    else:
        tags_similarity = 100

    return tags_similarity






