#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datastore import *


def admin_update_proc():
    recommendations = Recommendation.query()
    current_date = datetime.utcnow()

    for r in recommendations:
        if (current_date - r.last_update).days >= recom_update_freq:
            current_similar = spotify_handler.spider_of_recommendations(q.name, 10)
            r.similar_groups = set(r.similar_groups + current_similar)

        data_handler.retrieve_data_for(r.name)

        for name in r.similar_groups:
            data_handler.retrieve_data_for(name)
