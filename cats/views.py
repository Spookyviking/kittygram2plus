from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
# from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import ScopedRateThrottle

from .models import Achievement, Cat, User
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .throttling import WorkingHoursRateThrottle


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Устанавливаем разрешение
    permission_classes = (OwnerOrReadOnly,)
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    throttle_scope = 'low_request' 
    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    ## Добавим в кортеж ещё один бэкенд filters.SearchFilter
    ### filters.OrderingFilter для сортировки
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # Временно отключим пагинацию на уровне вьюсета, 
    # так будет удобнее настраивать фильтрацию
    # pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    # search_fields = ('name',)
    ## Определим, что значение параметра search должно быть началом искомой строки
    ##search_fields = ('^name',)
    """
    Поиск можно проводить и по содержимому полей связанных моделей.
    Доступные для поиска поля связанной модели указываются через нотацию
    с двойным подчёркиванием: ForeignKey текущей модели__имя поля
    в связанной модели.
    """
    search_fields = ('achievements__name', 'owner__username')
    ordering_fields = ('name', 'birth_year')
    ordering = ('birth_year',) # сортировка по умолчанию

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) 
    
    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернем обновленный перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()
    
    # переопределяем метод get_queryset для реализации фильтрации
    def get_queryset(self):
        queryset = Cat.objects.all()
        # Добыть параметр color из GET-запроса
        color = self.request.query_params.get('color')
        if color is not None:
            #  через ORM отфильтровать объекты модели Cat
            #  по значению параметра color, полученнго в запросе
            queryset = queryset.filter(color=color)
        return queryset 


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer