from ilc_core.work.task_queue import TaskQueue, TaskDescriptor


def test_task_queue_fifo_order():
    q = TaskQueue()

    t1 = TaskDescriptor(task_id="t1", task_type="claim.submit")
    t2 = TaskDescriptor(task_id="t2", task_type="claim.submit")
    t3 = TaskDescriptor(task_id="t3", task_type="refute.attempt")

    q.add_task(t1)
    q.add_task(t2)
    q.add_task(t3)

    assert len(q) == 3
    assert not q.is_empty()

    out1 = q.pop_next()
    out2 = q.pop_next()
    out3 = q.pop_next()
    out4 = q.pop_next()  # should be None

    assert out1 is t1
    assert out2 is t2
    assert out3 is t3
    assert out4 is None
    assert q.is_empty()


def test_task_queue_drain():
    q = TaskQueue()
    tasks = [
        TaskDescriptor(task_id=f"t{i}", task_type="claim.submit")
        for i in range(5)
    ]
    for t in tasks:
        q.add_task(t)

    drained = q.drain()
    assert drained == tasks
    assert q.is_empty()
    assert len(q) == 0
