#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para cálculo de recomendaciones
'''
from datastore import *

def get_recommendations(values):
    queue = Queue.Queue()
    thread1 = Thread(target = data_handler.thread_retrieve_data_for, args = [values[0], queue])
    thread2 = Thread(target = data_handler.thread_retrieve_data_for, args = [values[1], queue])
    thread3 = Thread(target = data_handler.thread_retrieve_data_for, args = [values[2], queue])
    recommendations = []
    
    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    while not queue.empty():
        artist = queue.get()
        local_recommendations = artist.similar_groups
        recommendations = list(set().union(recommendations, local_recommendations))

    """for value in values:
        artist = data_handler.retrieve_data_for(value)

        local_recommendations = artist.similar_groups
        recommendations = list(set().union(recommendations, local_recommendations))
    """
    return recommendations
