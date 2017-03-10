from collections import defaultdict, namedtuple
from functools import reduce


# Generalnie zadanie to nic innego jak zaimplementowanie acyklicznego grafu
# skierowanego. Ze wzgledu na brak wiekszej ilosci czasu, ponizej prezentuje
# bardzo zubozona mozliwosc rozwiazania tego zadania.
# W przyszlosci nalezaloby dodac weryfikacje acyklicznosci oraz
# kontrole bledow.


def execute(task):
    """Agregacja listy wynikowej z zadania.
    :param task: Zadanie do przetworzenia.
    :return: Zagregowana wartosc z listy przetworzonych wartosci zadania.
    """
    return reduce(lambda fst, snd: fst + snd, task.run())


class Task:
    """Zadanie do wykonania."""

    def __init__(self, task_name, task_builder, func=None, args=None):
        """Konstruktor.
        :param task_name: Nazwa zadania.
        :param task_builder: Instancja TaskBuilder skojarzona z zadaniem.
        :param func: Funkcja wywolywana przez zadanie. Jesli None to funkcja
        zwraca podana wartosc.
        :param args: Lista dodatkowych argumentow do przetworzenia (obok
        argumentow z zadan zaleznosci).
        """
        self.task_name = task_name
        self.task_builder = task_builder
        self.args = args
        self.func = func if func is not None else lambda x: x

    def run(self, dependencies=None):
        """Uruchomienie funkcji zadania, z uzyciem argumentow podanych w
        konstruktorze i argumentow pobranych z wczesniejszych zadan.
        :param dependencies: Lista podzadan. Domyslnie pobierane ze
        skojarzonej instancji TaskBuilder.
        :return: Lista przetworzonych wartosci.
        """
        # najpierw sprawdzenie, czy nie bylismy juz w tym wezle
        prv_done_values = self.task_builder.get_run_task_values(self)
        if prv_done_values is not None:
            return prv_done_values

        if dependencies is None:
            dependencies = self.get_dependencies()

        if len(dependencies) == 0 and \
                (self.args is None or len(self.args) == 0):
            raise ValueError('Task without dependencies must have arguments.')

        dep_list = []  # lista wynikowa z przetworzonymi wartosciami
        # najpierw wartosci z podzadan
        for dependency in dependencies:
            for val in dependency.run():
                dep_list.append(self.func(val))
        # nastepnie wartosci podane, jesli byly
        if self.args is not None:
            for arg in self.args:
                dep_list.append(self.func(arg))

        # dodanie wyniku do listy juz przetworzonych wezlow
        self.task_builder.mark_task_as_run(self, dep_list)

        return dep_list

    def get_dependencies(self):
        """Pobranie podzadan ze skojarzonej instancji TaskBuilder.
        :return: Lista podzadan.
        """
        if self.task_builder is None:
            raise TypeError('No linked TaskBuilder instance.')

        graph = self.task_builder.get_graph()
        return [dep.task for dep in graph.values()
                if dep.task.task_name in graph[self.task_name].dependencies]

    def add_dependency(self, dependency_task):
        """Dodanie podzadania.
        :param dependency_task: Instancja podzadania.
        """
        self.task_builder.add_dependency(self, dependency_task)


class TaskBuilder:
    """Klasa budująca wezly zadan i zaleznosci miedzy nimi."""

    def __init__(self):
        """Konstruktor."""
        # pomocniczy model wezlow zadan
        self._task_node = namedtuple('TaskNode', ['task', 'dependencies'])
        # graf jako słownik
        self._graph = defaultdict()
        self._alreadyRunTasks = defaultdict()

    def reset(self):
        """Resetowanie grafu."""
        self._graph = defaultdict()

    def get_graph(self):
        """Pobranie grafu."""
        return self._graph

    def add_task(self, task):
        """Dodanie zadania po sprawdzeniu czy juz nie istnieje.
        :param task: Zadanie do przydzielenia.
        """
        if task.task_name in self._graph:
            raise KeyError('Task {0} already added.'.format(task.task_name))

        self._graph[task.task_name] = self._task_node(task, set())

    def add_dependency(self, parent_task, dependency_task):
        """Dodanie zaleznosci.
        :param parent_task: Wezel rodzica.
        :param dependency_task: Wezel, od ktorego zalezy rodzic.
        """
        if dependency_task.task_name not in self._graph:
            self.add_task(dependency_task)

        self._graph[parent_task.task_name].dependencies.add(
            dependency_task.task_name)

    def make_new_task(self, task_name, func=None, args=None):
        """Stworzenie nowego zadania zestawionego z instancja TaskBuilder.
        :param task_name: Nazwa nowego zadania.
        :param func: Funkcja wywolywana przez zadanie. Powinna posiadac jeden
        argument i zwracac jedna wartosc.
        :param args: Lista argumentow do przetworzenia.
        :return: Nowo stworzone zadanie polaczone z instancja TaskBuilder.
        :rtype: Task
        """
        task = Task(task_name, self, func, args)
        self.add_task(task)
        return task

    def mark_task_as_run(self, task, values_list):
        """Oznaczenie zadania jako wykonanego.
        :param task: Zadanie do oznaczenia.
        :param values_list: Wartosci zwrocone po wykonaniu wezla.
        """
        self._alreadyRunTasks[task.task_name] = values_list

    def get_run_task_values(self, task):
        """Zwrocenie wartosci wykonanego zadania. None, jesli zadanie nie
        zostalo jeszcze wykonane.
        :param task: Zadanie do sprawdzenia.
        :return: Wczesniej obliczone wartosci lub None, jesli zadanie nie
        zostalo jeszcze wykonane.
        """
        return self._alreadyRunTasks.get(task.task_name)
