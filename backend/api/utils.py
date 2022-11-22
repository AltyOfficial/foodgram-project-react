# import os

from django.http import FileResponse
from fpdf import FPDF

from recipes.models import IngredientAmount
from backend.settings import BASE_DIR


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

    # Добавление картинки, разберусь позже
    # pdf.image(f'{BASE_DIR}\media\\recipes\image\image_40.png', w=80, h=80)

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


# def remove_pdf_file():
#     file = BASE_DIR / 'shopping_cart.pdf'
#     if file:
#         os.remove(file)
