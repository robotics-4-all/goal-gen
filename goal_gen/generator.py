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


class GeneratorGoalee:
    srcgen_folder = path.join(path.realpath(getcwd()), 'gen')

    @staticmethod
    def generate(model_fpath: str,
                 out_dir: str = None):
        # Create output folder
        if out_dir is None:
            out_dir = GeneratorGoalee.srcgen_folder
        model, imports = build_model(model_fpath)
        if not path.exists(out_dir):
            mkdir(out_dir)

        target = model.target
        middleware = target.middleware
        goals = target.goals

        GeneratorGoalee.report_middleware(middleware)
        GeneratorGoalee.report_goals(goals)

        out_file = path.join(out_dir, "goal_checker.py")
        with open(path.join(out_file), 'w') as f:
            f.write(template.render(middleware=middleware,
                                    target=target,
                                    goals=goals))
        chmod(out_file, 509)

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
    GeneratorGoalee.generate(model._tx_filename)
