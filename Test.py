import TaskBuilder


def main():
    task_builder = TaskBuilder.TaskBuilder()
    task_one = task_builder.make_new_task('Sum')
    task_two = task_builder.make_new_task('Mult3', lambda x: x*3)
    task_three = task_builder.make_new_task('Mult2', lambda x: x*2)
    # dol grafu, oczywiscie musi miec parametry poczatkowe
    task_four = task_builder.make_new_task('range10', None, range(10))
    # stworzenie zaleznosci
    task_one.add_dependency(task_two)
    task_one.add_dependency(task_three)
    task_two.add_dependency(task_four)
    task_three.add_dependency(task_four)
    # przedstawienie wynikow
    print(task_one.run())
    # zagegowany wynik
    print(TaskBuilder.execute(task_one))

if __name__ == "__main__":
    main()
