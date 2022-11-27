import base64

from django.core.files.base import ContentFile
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from fpdf import FPDF
from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import IngredientAmount, Recipe
from backend.settings import BASE_DIR


def execute_cart_favorite(request, pk, serializer, model):
    if request.method == 'POST':
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)
    obj = get_object_or_404(model, user=user, recipe=recipe)
    obj.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def create_pdf_file(request):
    objects = IngredientAmount.objects.filter(
        recipe__is_in_shopping_cart__user=request.user
    )
    product_list = {}
    for obj in objects:
        name = obj.ingredient.name
        amount = obj.amount
        measurement_unit = obj.ingredient.measurement_unit
        if name in product_list:
            product_list[name]['amount'] += amount
        else:
            product_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }

    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.add_font(
        'DejaVu', '', f'{BASE_DIR}/fonts/DejaVuSansCondensed.ttf', uni=True
    )
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(40, 10, 'Ваш список покупок', 0, 1)
    pdf.cell(40, 10, '', 0, 1)
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(
        200, 8, f"{'Ингредиент'.ljust(30)} {'Количество'.rjust(20)}", 0, 1
    )
    pdf.line(10, 30, 150, 30)
    pdf.line(10, 38, 150, 38)
    for line in product_list:
        name = line
        measurement_unit = product_list[name]['measurement_unit']
        amount = str(product_list[name]['amount'])
        amount_string = f"{amount} {measurement_unit}"
        string = f"{name.ljust(30)} {amount_string.rjust(20)}"
        pdf.cell(200, 9, string, 0, 1)

    pdf.output('shopping_cart.pdf', 'F')
    return FileResponse(
        open('shopping_cart.pdf', 'rb'),
        as_attachment=True,
        content_type='application/pdf'
    )


def create_text_file(request):
    objects = IngredientAmount.objects.filter(
        recipe__is_in_shopping_cart__user=request.user
    )
    product_list = {}
    for obj in objects:
        name = obj.ingredient.name
        amount = obj.amount
        measurement_unit = obj.ingredient.measurement_unit
        if name in product_list:
            product_list[name]['amount'] += amount
        else:
            product_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }
    
    final_list = ''
    for line in product_list:
        name = line
        measurement_unit = product_list[name]['measurement_unit']
        amount = str(product_list[name]['amount'])
        amount_string = f"{amount} {measurement_unit}"
        string = f"{name.ljust(30)} {amount_string.rjust(20)}"
        final_list += string + '\n'
    return HttpResponse(final_list, content_type='text/plain; charset=utf8')
