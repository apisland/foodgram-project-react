from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag, TagRecipe)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов."""
    name = serializers.CharField(
        required=True,
    )
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientsEditSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления ингредиентов."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецепта и ингредиента"""
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = (
            'id', 'name', 'measurement_unit', 'amount',)


class UserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserListSerializer(UserSerializer):
    """Сериалайзер отображения пользователя"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj: User):
        """Метод для определения подписки пользователя."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()


class UserEditSerializer(serializers.ModelSerializer):
    """Сериализатор редактирования пользователя."""
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'role',)
        model = User
        read_only_fields = ('role',)


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра модели Рецепт. """
    tags = TagSerializer(many=True)
    author = UserListSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        """Метод получения ингредиента."""
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Метод получения избранного."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод добавления в список покупок."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер создания/обновления рецепта."""
    author = UserListSerializer(read_only=True)
    ingredients = IngredientsEditSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        """Метод проверки уникальности ингредиента."""
        ingredients = data['ingredients']
        ingredient_list = []
        for items in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_list.append(ingredient)
        return data

    def validate_tags(self, data):
        """Метод проверки уникальности тега."""
        tags = data['tags']
        tags_list = []
        for items in tags:
            tag = get_object_or_404(
                Tag, id=items['id'])
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Тег должен быть уникальным!')
            tags_list.append(tag)
        if not tags:
            raise serializers.ValidationError(
                'Необходим тэг для рецепта!')
        return data

    def create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиентов в рецепте."""
        for ingredient in ingredients:
            IngredientRecipe.objects.bulk_create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), )

    def create_tags(self, tags, recipe):
        """Метод создания тегов в рецепте."""
        for tag in tags:
            TagRecipe.objects.bulk_create(recipe=recipe, tag=tag)

    def validate_ingredients(self, ingredients):
        """Метод проверки наличия ингредиента."""
        if not ingredients:
            raise serializers.ValidationError(
                'Нужен минимум 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if str(ingredient.get('amount')):
                raise serializers.ValidationError(
                    'Строковое значение недопустимо!')
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть 1!')
        return ingredients

    def validate_cooking_time(self, cooking_time):
        """Метод проверки время приготовления."""
        if str(cooking_time):
            raise serializers.ValidationError(
                    'Строковое значение недопустимо!')
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления больше 1!')
        return cooking_time

    def create(self, validated_data):
        """Метод создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецепта."""
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.create_ingredients(ingredients, instance)
        self.create_tags(tags, instance)
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image'):
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance

    def to_representation(self, instance):
        """Метод представления рецепта."""
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class UserFavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения избранного. """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        """Метод представления корзины покупок."""
        return UserFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Избранное. """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        """Метод представления избранного."""
        return UserFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class UserFollowSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения подписок пользователя. """
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        """Метод получения подписок пользователя."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        """Метод получения рецептов пользователя."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return UserFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        """Метод подсчета рецептов."""
        return Recipe.objects.filter(author=obj).count()


class FollowSerializer(serializers.ModelSerializer):
    """ Сериализатор подписок. """

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
            )
        ]

    def to_representation(self, instance):
        """Метод представления подписок пользователя."""
        return UserFollowSerializer(instance.author, context={
            'request': self.context.get('request')
        }).data
