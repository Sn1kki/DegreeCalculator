from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
import copy
from django.contrib.sessions.models import Session

def convert_base(num : int | str = 0, from_base : int = 10, to_base : int = 10) -> str:
    """
    Функция convert_base позволяет конвертировать число из одной системы счисления в другую.
    Она принимает число, основание 1, из которого происходит преобразование, и основание 2, в которое нужно преобразовать число.

    :param num: Число, которое необходимо конвертировать. Если оно передано в виде строки, то оно будет преобразованно в формат int.
    :exception num: Ввод числа класса int или Строки класса str
    :type num: int (Желательно)

    :param to_base: Целое число, обозначающее целевую систему счисления, в которую будет преобразовано num. По умолчанию равно 10.
    :exception to_base: Ввод числа класса int, В диапазоне от 2 до 36
    :type to_base: int (Желательно)

    :param from_base: Целое число, обозначающее систему счисления, из которой будет преобразовано num. По умолчанию равно 10.
    :exception from_base: Ввод числа класса int, В диапазоне от 2 до 36
    :type from_base: int (Желательно)

    :return: Возвращает строковое представление числа num, преобразованного в систему счисления с основанием to_base.
    :rtype: str

    :except num ValueError: Ввод некорректных символов в параметр num
    :except to_base ValueError: Ввод некорректных данных в параметр to_base, не соответствующих ожидаемым значениям
    :except from_base ValueError: Ввод некорректных данных в параметр from_base, не соответствующих ожидаемым значениям

    """
    try:
        # Задание постоянных
        alphabet : str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        alphabet_ru : str = "0123456789ФИСВУАПРШОЛДЬТЩЗЙКЫЕГМЦЧНЯ"
        alphabet_wrong : str = "ХЪЖЭБЮЁ"
        is_dot : bool = False

        # --------------------------------
        
        # Проверка на пустые значения
        if num == '':
            raise ValueError(f'''Введино пустое значение''')
        
        if from_base == '': from_base = 10

        if to_base == '': to_base = 10

        # ----------------------------------------------------------------
        
        # Проверка на корректность введенных символов
        
        try:    
            if isinstance(from_base, str):
                from_base : int = int(from_base)

            if isinstance(to_base, str):
                to_base : int = int(to_base)
        except:
            raise ValueError(f'''Значение from_base или to_base нельзя конвертировать в число''')

        # ----------------------------------------------------------------
        
        # Проверка на корректность введенных систем счисления
        
        if to_base < 2 or to_base > 37:
            raise ValueError(f'''to_base должен находиться в диапозоне [2;36]: to_base = {to_base}''')
        
        if from_base < 2 or from_base > 37:
            raise ValueError(f'''from_base должен находиться в диапозоне [2;36]: from_base = {from_base}''')

        # ----------------------------------------------------------------

        # Форматирование num в верхний регистр и удаление пробелов
        try:
            num : str = str(num).upper().replace(" ", "").replace(",", ".") #! Нужно добавит проверку на кол-во спец символов. ( - или . )
            num_uno : str = copy.deepcopy(num)
            
            # Проверка на введение ошибочных символов кириллицы
            for x in range(len(alphabet_wrong)):
                if alphabet_wrong[x] in num:
                    raise ValueError(f'''Некорректные символы в значении "{num}"''')

            # Преобразование ошибочных символов русских букв на корректные символы английского алфавита
            for x in range(len(alphabet)):
                num : str = num.replace(alphabet_ru[x], alphabet[x])
            
            # Разделение числа на числительную и десятичную части
            if "." in num:
                is_dot : bool = True
                num_uno , num_dos =  num.split(".", maxsplit=1)
                num_dos_dec : float = 0.0

        except:
            raise ValueError(f'''Значение "{num}" невозможно преобразовать в строку''') #!!!!

        
        # ----------------------------------------------------------------
        
        # Преобразование числа в десятичную систему счисления
        
        try:
            if isinstance(num_uno, str):
                num_dec : int = abs(int(num_uno, from_base))
            else:
                num_dec : int = abs(int(num_uno))
            
            if is_dot:
                for x in range(len(num_dos)):
                    num_dos_dec += int(num_dos[x], from_base)/(from_base**(x+1))
                print(num_dos_dec)
        except:
            raise ValueError(f'''Значение "{num}" невозможно перевести из системы с основанием {from_base} в десятичную''')

        # ----------------------------------------------------------------
        
        # Генерация ответа

        ans_uno : str = ''
        ans_dos : str = ''
        
        # Перевод целого числа в нужную систему счисления
        while num_dec > 0:
            ans_uno  += alphabet[num_dec%to_base]
            num_dec  //= to_base
        
        # Перевод дробной части в нужную систему счисления
        if is_dot:
            while num_dos_dec > 0 and len(ans_dos) < 12:  # Ограничиваем длину дробной части
                num_dos_dec *= to_base
                digit : int = int(num_dos_dec)
                ans_dos += alphabet[digit]
                num_dos_dec -= digit
        
        
        # ----------------------------------------------------------------
        
        if not is_dot:
            ans : str = ans_uno[::-1]
        else:
            ans : str = ans_uno[::-1] + "." + ans_dos
        
        if "-" in num:
            return "-" + ans
        else:
            return ans
    # Возвращение ошибки при её наличии
    except ValueError as TextError:
        return TextError

def index(request : HttpRequest) -> HttpResponse:
    result = ''
    error = ''
    num_input = '0'
    from_base = 10
    to_base = 10

    if request.method == 'POST':
        num_input = request.POST.get('num', '0')
        from_base = int(request.POST.get('from_base', 10))
        to_base = int(request.POST.get('to_base', 10))

        try:
            result = convert_base(num_input, from_base, to_base)

            history = request.session.get('history', [])
            history_entry = f"{num_input}_{from_base} >> {result}_{to_base}"
            if len(history) >= 10:
                history.pop(0)
            history.append(history_entry)
            request.session['history'] = history
        except ValueError as e:
            error = f'Ошибка: {str(e)}'
            result = '' 

    context = {
        'result': result,
        'error': error,
        'num': num_input,
        'from_base': from_base,
        'to_base': to_base,
    }
    return render(request, 'converter/calc/index.html', context)

def history_view(request : HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        request.session.pop('history', None)
        return JsonResponse({'status': 'success'})

    history = request.session.get('history', [])
    formatted_history = [tuple(item.split(" >> ")) for item in reversed(history)]
    return render(request, 'converter/history/index.html', {'history': formatted_history})