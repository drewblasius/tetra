from tetra.tasks.manager import TaskManager

task_manager = TaskManager(broker=None, namespace="test_task_manager")

HELLO_WORLD_STR = "hello world"


@task_manager.register
def hello_world():
    return HELLO_WORLD_STR


@task_manager.register(hello="world")
def hello_world_with_args():
    return HELLO_WORLD_STR


def test_task():
    """Check that the function runs normally when called"""
    assert HELLO_WORLD_STR == hello_world()


def test_task_with_args():
    """Check that the function runs normally 
    when wrapped with task and task has args"""
    assert HELLO_WORLD_STR == hello_world_with_args()


def test_task_manager_repr():
    assert "test_task_manager" in task_manager.__repr__()
