#!/usr/bin/env python3

from goalee import Target, RedisMiddleware
from goalee.topic_goals import TopicMessageReceivedGoal, TopicMessageParamGoal
from goalee.area_goals import RectangleAreaGoal, CircularAreaGoal
from goalee.complex_goal import ComplexGoal, ComplexGoalAlgorithm
from goalee.types import Point


if __name__ == '__main__':
    {% if middleware.__class__.__name__ == 'AMQPBroker' %}
    middleware = AMQPMiddleware()
    {% elif middleware.__class__.__name__ == 'RedisBroker' %}
    middleware = RedisMiddleware()
    {% endif %}
    t = Target(middleware, name='{{ target.name }}',
               score_weights={{ target.scoreWeights }})

    {% for goal in target.goals %}
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
    {% elif goal.__class__.__name__ == 'CircularAreaGoal' %}
    g = CircularAreaGoal(topic='{{ goal.topic }}',
                         name='{{ goal.name }}',
                         center=Point({{ goal.center.x }}, {{ goal.center.y }}),
                         radius={{ goal.radius }},
                         max_duration={{ goal.max_duration }},
                         min_duration={{ goal.min_duration }})
    {% elif goal.__class__.__name__ == 'RectangleAreaGoal' %}
    g = RectangleAreaGoal(topic='{{ goal.topic }}',
                          name='{{ goal.name }}',
                          bottom_left_edge=Point({{ goal.bottomLeftEdge.x }}, {{ goal.bottomLeftEdge.y }}),
                          length_x={{ goal.lengthX }},
                          length_y={{ goal.lengthY }},
                          max_duration={{ goal.max_duration }},
                          min_duration={{ goal.min_duration }})
    {% elif goal.__class__.__name__ == 'ComplexGoal' %}
    g = ComplexGoal(name='{{ goal.name }}',
                    {% if goal.algorithm.__class__.__name__ == 'ALL_ACCOMPLISHED'%}
                    algorithm=ComplexGoalAlgorithm.ALL_ACCOMPLISHED,
                    {% elif goal.algorithm.__class__.__name__ == 'NONE_ACCOMPLISHED'%}
                    algorithm=ComplexGoalAlgorithm.NONE_ACCOMPLISHED,
                    {% endif %}
                    max_duration={{ goal.max_duration }},
                    min_duration={{ goal.min_duration }})
    {% for goal in goal.goals %}
    {% if goal.__class__.__name__ == 'TopicMessageReceivedGoal' %}
    gs = TopicMessageReceivedGoal(topic='{{ goal.topic }}',
                                  name='{{ goal.name }}',
                                  max_duration={{ goal.max_duration }},
                                  min_duration={{ goal.min_duration }})

    {% elif goal.__class__.__name__ == 'TopicMessageParamGoal' %}
    gs = TopicMessageParamGoal(topic='{{ goal.topic }}',
                               name='{{ goal.name }}',
                               condition={{ goal.cond_lambda }},
                               max_duration={{ goal.max_duration }},
                               min_duration={{ goal.min_duration }})
    {% elif goal.__class__.__name__ == 'CircularAreaGoal' %}
    gs = CircularAreaGoal(topic='{{ goal.topic }}',
                          name='{{ goal.name }}',
                          center=Point({{ goal.center.x }}, {{ goal.center.y }}),
                          radius={{ goal.radius }},
                          max_duration={{ goal.max_duration }},
                          min_duration={{ goal.min_duration }})
    {% elif goal.__class__.__name__ == 'RectangleAreaGoal' %}
    gs = RectangleAreaGoal(topic='{{ goal.topic }}',
                           name='{{ goal.name }}',
                           bottom_left_edge=Point({{ goal.bottomLeftEdge.x }}, {{ goal.bottomLeftEdge.y }}),
                           length_x={{ goal.lengthX }},
                           length_y={{ goal.lengthY }},
                           max_duration={{ goal.max_duration }},
                           min_duration={{ goal.min_duration }})
    {% endif %}
    g.add_goal(gs)
    {% endfor %}
    ## More Goals to Generate here
    {% endif %}
    t.add_goal(g)
    {% endfor %}

    {% if target.concurrent == True %}
    t.run_concurrent()
    {% else %}
    t.run_seq()
    {% endif %}

