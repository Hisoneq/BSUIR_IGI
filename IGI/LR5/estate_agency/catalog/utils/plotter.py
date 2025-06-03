import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from django.db.models import Count
from ..models import Property, PropertyType


def create_property_type_chart():
    """Создает график распределения типов недвижимости"""
    property_types = PropertyType.objects.annotate(count=Count('property'))
    types = [pt.title for pt in property_types]
    counts = [pt.count for pt in property_types]
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(counts)), counts)
    plt.xticks(range(len(types)), types, rotation=15)
    plt.title('Распределение типов недвижимости')
    plt.xlabel('Тип недвижимости')
    plt.ylabel('Количество объектов')
    
    plt.tight_layout()
    plt.savefig('media/property_types_chart.png')
    plt.close('all')


class Plotter:
    @staticmethod
    def plt_bars(data, path=None, categories=None, show=False, x_label=None, y_label=None, title=None):
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(data)), data)
        if x_label:
            plt.xlabel(x_label)
        if y_label:
            plt.ylabel(y_label)
        if categories:
            plt.xticks(range(len(data)), categories, rotation=15)
        if title:
            plt.title(title)

        if path:
            plt.savefig(path)
        if show:
            plt.show()

        plt.close('all')
