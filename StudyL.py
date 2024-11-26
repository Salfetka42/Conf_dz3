import sys
import re
import toml


class ConfigSyntaxError(Exception):
    # Кастомное исключение для синтаксических ошибок
    pass


def parse_custom_config(input_text):
    # Парсинг текста на учебном конфигурационном языке и преобразование в структуру данных Python
    lines = input_text.strip().split("\n")
    result = {}
    constants = {}

    def evaluate_constant(expression):
        for const, value in constants.items():
            expression = expression.replace(f"|{const}|", str(value))
        try:
            return eval(expression, {"__builtins__": None}, {})
        except Exception as e:
            raise ConfigSyntaxError(f"Ошибка вычисления выражения '{expression}': {e}")

    stack = []
    current_dict = result

    for line_no, line in enumerate(lines, start=1):
        line = line.strip()

        # Пропуск пустых строк
        if not line:
            continue

        # Пропуск комментариев
        if line.startswith("//"):
            continue

        # Обработка начала словаря
        if line.endswith("{"):
            key = line[:-1].strip()  # ключ для вложенного словаря
            if key:  # проверка на непустой ключ
                new_dict = {}
                current_dict[key] = new_dict
                stack.append(current_dict)  # сохраняем текущий словарь в стеке
                current_dict = new_dict  # переключаемся на новый словарь
            else:
                # Если ключ пустой, просто обрабатываем как вложенный словарь
                stack.append(current_dict)
            continue

        # Обработка конца словаря
        if line == "}":
            if stack:
                current_dict = stack.pop()  # возвращаемся к родительскому словарю
            else:
                raise ConfigSyntaxError(f"Лишний символ '}}' на строке {line_no}.")
            continue

        # Обработка объявления констант (с учетом символа ; в конце)
        if line.startswith("var "):
            match = re.match(r"var\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+);?", line)
            if not match:
                raise ConfigSyntaxError(f"Ошибка синтаксиса в объявлении константы на строке {line_no}: {line}")
            const_name, const_value = match.groups()
            constants[const_name] = evaluate_constant(const_value)
            continue

        # Обработка ключей и значений (с учетом символа ';' в конце)
        match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*'([^']*)'\s*;?,?", line)  # Строковые значения
        if match:
            key, value = match.groups()
            current_dict[key] = value
            continue

        match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(\d+)\s*;?,?", line)  # Целые числа
        if match:
            key, value = match.groups()
            current_dict[key] = int(value)
            continue

        match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(\d+\.\d+)\s*;?,?", line)  # Дробные числа
        if match:
            key, value = match.groups()
            current_dict[key] = float(value)
            continue

        match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*\|([a-zA-Z_][a-zA-Z0-9_]*)\|\s*;?,?", line)  # Ссылки на константы
        if match:
            key, const_name = match.groups()
            if const_name not in constants:
                raise ConfigSyntaxError(f"Неизвестная константа '{const_name}' на строке {line_no}.")
            current_dict[key] = constants[const_name]
            continue

        raise ConfigSyntaxError(f"Ошибка синтаксиса на строке {line_no}: {line}")

    return result


def convert_to_toml(parsed_data):
    return toml.dumps(parsed_data)


def main():
    if len(sys.argv) != 2:
        print("Использование: python script.py <путь_к_файлу>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r") as file:
            input_text = file.read()
        parsed_data = parse_custom_config(input_text)
        toml_output = convert_to_toml(parsed_data)
        print(toml_output)
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
        sys.exit(1)
    except ConfigSyntaxError as e:
        print(f"Ошибка синтаксиса: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
