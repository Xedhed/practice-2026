import socket
import os

# Настройки хоста и порта
# '0.0.0.0' означает, что сервер будет принимать подключения со всех сетевых интерфейсов
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

# Создаем сокет (AF_INET = IPv4, SOCK_STREAM = TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Разрешаем повторно использовать порт сразу после перезапуска сервера
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Привязываем сокет к хосту и порту
server_socket.bind((SERVER_HOST, SERVER_PORT))
# Слушаем входящие соединения (1 — максимальная очередь ожидающих подключений)
server_socket.listen(1)

print(f"=== Сервер успешно запущен на http://localhost:{SERVER_PORT} ===")

try:
    while True:
        # Ждем подключения клиента (браузера)
        client_connection, client_address = server_socket.accept()

        # Получаем запрос от клиента (считываем первые 1024 байта и декодируем в текст)
        request = client_connection.recv(1024).decode('utf-8', errors='ignore')

        # Если запрос пустой (такое бывает при некоторых проверках браузера), пропускаем
        if not request.strip():
            client_connection.close()
            continue

        print(f"\n[ПОЛУЧЕН ЗАПРОС ОТ {client_address}]:")
        # Печатаем только первую строчку запроса в консоль для наглядности
        print(request.split('\n')[0])

        try:
            # Разбираем HTTP-заголовки, чтобы получить путь к файлу
            headers = request.split('\n')
            # Первая строка выглядит как: "GET /index.html HTTP/1.1", разбиваем её по пробелам
            filename = headers[0].split()[1]

            # Если запрашивают корень "/", перенаправляем на index.html
            if filename == '/':
                filename = '/index.html'

            # Формируем безопасный путь к файлу (убираем начальный слэш)
            filepath = os.path.join('htdocs', filename.lstrip('/'))

            # Попытка открыть и прочитать файл
            with open(filepath, 'r', encoding='utf-8') as fin:
                content = fin.read()

            # Собираем успешный HTTP-ответ (Статус 200 OK)
            # Обязательно указываем Content-Type, чтобы браузер понял, что это HTML в кодировке UTF-8
            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: text/html; charset=utf-8\r\n"
            response += "\r\n"  # Пустая строка — разделитель заголовков от тела
            response += content

        except (FileNotFoundError, IndexError):
            # Если файл не найден на диске, формируем ответ 404
            content = "<h1>404 Not Found</h1><p>Упс! Запрашиваемая страница не найдена на этом сервере.</p>"
            response = "HTTP/1.0 404 NOT FOUND\r\n"
            response += "Content-Type: text/html; charset=utf-8\r\n"
            response += "\r\n"
            response += content

        except Exception as e:
            # На случай любых других непредвиденных ошибок (код 500)
            content = f"<h1>500 Internal Server Error</h1><p>Ошибка на сервере: {e}</p>"
            response = "HTTP/1.0 500 INTERNAL SERVER ERROR\r\n"
            response += "Content-Type: text/html; charset=utf-8\r\n"
            response += "\r\n"
            response += content

        # Отправляем ответ клиенту, закодировав строку обратно в байты
        client_connection.sendall(response.encode('utf-8'))
        # Закрываем соединение с текущим клиентом
        client_connection.close()

except KeyboardInterrupt:
    print("\nСервер останавливается пользователем...")
finally:
    # Закрываем главный серверный сокет при выходе
    server_socket.close()
    print("Сервер остановлен.")