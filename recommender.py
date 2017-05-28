#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para cálculo de recomendaciones
'''
from datastore import *

total_recommendations = 30


"""
Devuelve recomendaciones para unos grupos pasados como parámetros

Args:
    values (str): lista de nombres de grupos
Return:
    recommendations: lista de nombres de grupos recomendados
"""
def get_recommendations(values):
    request_queue = Queue.Queue()
    values = [ group for group in values if group != None ]
    threads = []
    recommendations = []
    union_recommendations = []
    intersect_recommendations = []

    if len(values) > 0:
        rec_per_group = total_recommendations/len(values)


    # Obtenemos las recomendaciones de spotify prealmacenadas o las solicitamos a la API
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
            intersect_recommendations = list(set().intersection(intersect_recommendations,
                                                                local_recommendations))
            first = False

    #############################################################
    # Para cada grupo que no este en la intersección de las listas
    # comprobamos su parecido haciendo uso de sus tags, géneros y
    # el año
    #############################################################

    union_recommendations = list(set(union_recommendations) - set(intersect_recommendations))

    for recommendation in union_recommendations:
        similarity_genres = 0
        similarity_tags = 0
        similarity_year_area = 0

        for value in values:
            similarity_genres += mean_similarity_of(value, recommendation, lambda g: g.tags)
            similarity_tags += mean_similarity_of(value, recommendation, lambda g: g.genres)
            similarity_year_area += mean_similarity_year_area(value, recommendation)

        similarity_genres = similarity_genres / len(values)
        similarity_tags = similarity_tags / len(values)
        similarity_year_area = similarity_year_area / len(values)

        if similarity_tags >= 70 or similarity_genres >= 70 or similarity_year_area >= 95:
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


"""
Devuelve la media de similaridad entre los atributos de artist y los
de recommended_artist

Args:
    artist (str): nombre del grupo para el que recomendar
    recommended_artist (str): candidato a recomendación
    extract_attribute(group -> group.attribute): función que indica el atributo a extraer
Return:
    tags_similarity(int): similaridad de 0 a 100 al grupo
"""
def mean_similarity_of(artist, recommended_artist, extract_attribute):
    tags_similarity = 0
    most_similar = data_handler.most_similar_group_to(artist)
    recommended_most_similar = data_handler.most_similar_group_to(recommended_artist)

    #############################################################
    # Si ambos grupos están en base de datos, extraemos el
    # atributo indicado por la función extract_attibute (e.g.
    # tags, géneros)
    #############################################################
    if most_similar and recommended_most_similar:
        tags = extract_attribute(data_handler.retrieve_data_for(artist))
        recommend_tags = extract_attribute(data_handler.retrieve_data_for(recommended_artist))

        # Calculamos la media de similaridad de los tags con
        # distancia de Levenstein, esto es, definimos la similaridad
        # como el ratio Levenshtein entre dos tags
        for tag in tags:
            max_similarity = 0
            for recommend_tag in recommend_tags:
                similarity = fuzz.ratio(tag.lower(), recommend_tag.lower())
                if similarity >= max_similarity:
                    max_similarity = similarity

            tags_similarity += max_similarity

        if len(tags) != 0:
            tags_similarity = tags_similarity / len(tags)
        #############################################################
        # Si no tenemos tags para el grupo para el que estamos
        # recomendando, no nos fiamos de la recomendación hecha por
        # spotify
        #############################################################
        else:
            tags_similarity = 0
    #############################################################
    # Si alguno de ambos grupos no está en base de datos, nos fiamos
    # de la recomendación dada por spotify
    #############################################################
    else:
        tags_similarity = 100

    return tags_similarity



"""
Devuelve la similaridad para el área y año de un grupo respecto a una
recomendación

Args:
    artist (str): nombre del grupo para el que recomendar
    recommended_artist (str): candidato a recomendación
Return:
    similarity(int): similaridad de 0 a 100 al grupo
"""
def mean_similarity_year_area(artist, recommended_artist):
    similarity = 0
    most_similar = data_handler.most_similar_group_to(artist)
    recommended_most_similar = data_handler.most_similar_group_to(recommended_artist)

    if most_similar and recommended_most_similar:
        group = data_handler.retrieve_data_for(artist)
        recommended = data_handler.retrieve_data_for(recommended_artist)

        if group.begin_year and recommended.begin_year:
            similarity += max(0, 100 - abs(group.begin_year - recommended.begin_year))
        if group.area and recommended.area:
            similarity += fuzz.ratio((group.area).lower(), (recommended.area).lower())

        similarity /= 2
    #############################################################
    # Si alguno de ambos grupos no está en base de datos, nos fiamos
    # de la recomendación dada por spotify
    #############################################################
    else:
        similarity = 100

    return similarity
