from os import path, mkdir, getcwd, chmod
from textx import generator
import jinja2

from goal_dsl.utils import build_model

_THIS_DIR = path.abspath(path.dirname(__file__))

# Initialize template engine.
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(path.join(_THIS_DIR, 'templates')),
    trim_blocks=True,
    lstrip_blocks=True)

template = jinja_env.get_template('template.tpl')

srcgen_folder = path.join(path.realpath(getcwd()), 'gen')


def generate(model_fpath: str,
             out_dir: str = None):
    # Create output folder
    if out_dir is None:
        out_dir = srcgen_folder
    model, _ = build_model(model_fpath)
    if not path.exists(out_dir):
        mkdir(out_dir)

    target = model.target
    middleware = target.middleware
    goals = target.goals

    report_middleware(middleware)
    report_goals(goals)

    for goal in goals:
        if goal.__class__.__name__ == 'TopicMessageParamGoal':
            cond_expr = parse_topic_condition(goal)
            cond_lambda = make_topic_condition_lambda(cond_expr)
            print(cond_lambda)
            goal.cond_lambda = cond_lambda
        goal = goal_max_min_duration_from_tc(goal)

    out_file = path.join(out_dir, "goal_checker.py")
    with open(path.join(out_file), 'w') as f:
        f.write(template.render(middleware=middleware,
                                target=target,
                                goals=goals))
    chmod(out_file, 509)


def goal_max_min_duration_from_tc(goal):
    max_duration = None
    min_duration = None
    if goal.timeConstraints is None:
        print(f'[*] Goal <{goal.name}> does not have any time constraints.')
    elif len(goal.timeConstraints) == 0:
        print(f'[*] Goal <{goal.name}> does not have any time constraints.')
    else:
        for tc in goal.timeConstraints:
            if tc.__class__.__name__ != 'TimeConstraintDuration':
                continue
            max_duration = tc.time if tc.comparator == '<' else max_duration
            min_duration = tc.time if tc.comparator == '>' else min_duration
    print(f'[*] Goal <{goal.name}> max duration: {max_duration} seconds')
    print(f'[*] Goal <{goal.name}> min duration: {min_duration} seconds')
    goal.max_duration = max_duration
    goal.min_duration = min_duration
    return goal


def to_python_op(op):
    if op == 'AND':
        return 'and'
    elif op == 'OR':
        return 'or'


def make_topic_condition_lambda(expr):
    return f'lambda msg: True if {expr} else False'


def transform_condition(condition):
    expr = ''
    if condition.__class__.__name__ == "ConditionGroup":
        r1 = transform_condition(condition.r1)
        r2 = transform_condition(condition.r2)
        op = condition.operator
        expr = f'({r1} {to_python_op(op)} {r2})'
    elif condition.__class__.__name__ == "StringCondition":
        if condition.operator in ('==', '!='):
            # expr = f'msg["{condition.param}"] == "{condition.val}"'
            expr = f'msg["{condition.param}"] {condition.operator} "{condition.val}"'
        elif condition.operator == '~':
            expr = f'"{condition.val}" in msg["{condition.param}"]'
        elif condition.operator == '!~':
            expr = f'"{condition.val}" not in msg["{condition.param}"]'
    elif condition.__class__.__name__ == "NumericCondition":
        expr = f'msg["{condition.param}"] {condition.operator} {condition.val}'
    return expr


def parse_topic_condition(goal):
    cond = goal.condition
    if cond.__class__.__name__ == "ConditionGroup":
        print(f'[*] - TopicMessageParamGoal for topic <{goal.topic}>' + \
              f' condition is of type <ConditionGroup>')
    elif cond.__class__.__name__ == "StringCondition":
        print(f'[*] - TopicMessageParamGoal for topic <{goal.topic}>' + \
              f' condition is of type <StringCondition>')
    elif cond.__class__.__name__ == "NumericCondition":
        print(f'[*] - TopicMessageParamGoal for topic <{goal.topic}>' + \
              f' condition is of type <NumericCondition>')
    expr = transform_condition(cond)
    return expr


def report_goals(goals: list):
    for goal in goals:
        if goal.__class__.__name__ == 'TopicMessageReceivedGoal':
            print(f'[*]  - Found TopicMessageReceivedGoal')
        elif goal.__class__.__name__ == 'TopicMessageParamGoal':
            print(f'[*]  - Found TopicMessageParamGoal')


def report_middleware(middleware):
    if middleware.__class__.__name__ == 'AMQPBroker':
        print('[*] - Middleware == AMQP Broker')
        print(f'-> host: {middleware.host}')
        print(f'-> port: {middleware.port}')
        print(f'-> vhost: {middleware.vhost}')
        print(f'-> exchange: {middleware.exchange}')
        print(f'-> username: {middleware.auth.username}')
        print(f'-> password: {middleware.auth.password}')
    elif middleware.__class__.__name__ == 'RedisBroker':
        print('[*] - Middleware == Redis Broker')
        print(f'-> host: {middleware.host}')
        print(f'-> port: {middleware.port}')
        print(f'-> db: {middleware.db}')
        print(f'-> username: {middleware.auth.username}')
        print(f'-> password: {middleware.auth.password}')
    elif middleware.__class__.__name__ == 'MQTTBroker':
        print('[*] - Middleware == MQTTBroker Broker')
        print(f'-> host: {middleware.host}')
        print(f'-> port: {middleware.port}')
        print(f'-> username: {middleware.auth.username}')
        print(f'-> password: {middleware.auth.password}')


@generator('goal_dsl', 'goalee')
def goal_dsl_generate_goalee(metamodel, model, output_path, overwrite, debug, **custom_args):
    "Generator for generating goalee from goal_dsl descriptions"
    generate(model._tx_filename)
