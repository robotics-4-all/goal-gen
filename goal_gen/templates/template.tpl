#!/usr/bin/env python3

from goalee import Target, RedisMiddleware
from goalee.topic_goals import TopicMessageReceivedGoal, TopicMessageParamGoal


if __name__ == '__main__':
    {% if middleware.__class__.__name__ == 'AMQPBroker' %}
    middleware = AMQPMiddleware()
    {% elif middleware.__class__.__name__ == 'RedisBroker' %}
    middleware = RedisMiddleware()
    {% endif %}
    t = Target(middleware, name='{{ target.name }}',
               score_weights={{ target.scoreWeights }})

    {% for goal in goals %}
    {% if goal.__class__.__name__ == 'TopicMessageReceivedGoal' %}
    g = TopicMessageReceivedGoal(topic='{{ goal.topic }}',
                                 name='{{ goal.name }}',
                                 max_duration={{ goal.max_duration }},
                                 min_duration={{ goal.min_duration }})

    {% elif goal.__class__.__name__ == 'TopicMessageParamGoal' %}
    g = TopicMessageParamGoal(topic='{{ goal.topic }}',
                              name='{{ goal.name }}',
                              condition={{ goal.cond_lambda }},
                              max_duration={{ goal.max_duration }},
                              min_duration={{ goal.min_duration }})
    {% endif %}
    t.add_goal(g)
    {% endfor %}

    {% if target.concurrent == True %}
    t.run_concurrent()
    {% else %}
    t.run_seq()
    {% endif %}

