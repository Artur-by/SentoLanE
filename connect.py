import socket
import yaml

ENQ = '\x05'  # Инициализация обмена данными (транзакции).
ACK = '\x06'  # подтверждение приема.
NAK = '\x15'  # ответ КСА о том что отправленный запрос некорректен.
STX = '\x02'  # стартовый байт пакета данных
ETX = '\x03'  # стоповый байт пакета данных
ETB = '\x17'  # байт отправляется КСА в порт при включении для передачи информации
# оборудованию, что КСА включился.
EOT = '\x04'  # байт окончание обмена данными (транзакции).
WACK = '\x09'  # специальный символ, используемый КСА для передачи ПЭВМ информации
# о том, что КСА занят и ведет обработку данных.Отправляется каждые 1, 5 секунды.
RVI = '\x40'  # байт используется для передачи информации о том, что КСА обнаружил ошибку.
SP = '\x20'  # пробел

with open('ip_port.yaml', 'r') as f:
    ip_port = yaml.safe_load(f)


def answer(data):
    ws = {'ENQ': b'\x05', 'ACK': b'\x06', 'NAK': b'\x15', 'STX': b'\x02',
          'ETX': b'\x03', 'ETB': b'\x17', 'EOT': b'\x04', 'WACK': b'\x09',
          'RVI': b'\x40'}
    for key, value in ws.items():
        if data == value:
            return key
    return data


def string_to_hex(string):
    hex_representation = ''
    for char in string:
        hex_representation += hex(ord(char))[2:]
    return bytes.fromhex(hex_representation)


def crc_result(packet: bytes) -> int:
    """
    функция расчета crc
    :param packet:
    :return: crc
    >>> crc_result(b'S*1                                    \x03')
    219
    """
    crc = 0
    for i in range(len(packet)):
        crc ^= packet[i] << (i % 9)
    return crc


# первичная тестовая функция
# def start_packet(transmition_type: str,
#                  end_byte: bytes,
#                  stx: bytes = STX,
#                  marker: chr = 'S',
#                  task_type: chr = '*',
#                  start_num: bytes = SP * 18,
#                  stop_num: bytes = SP * 18) -> bytes:
#     """функция формирует стартовый пакет"""
#     data = marker + task_type + transmition_type
#     bytes_data = string_to_hex(data)
#     packet = bytes_data + start_num + stop_num + end_byte
#
#     dec_crc = crc_result(packet)
#    # print(dec_crc)
#
#     crc = dec_crc.to_bytes(2, 'big').hex()
#
#     crc = string_to_hex(crc)
#    # print(crc)
#     # print(crc)
#     packet += crc
#     print(packet)
#     return packet


def get_crc(data: str) -> str:
    """
    функция подсчета crc полученных данных data
    :param data: входная строка с данными
    :return: значение crc в шестнадцатиричном виде
    >>> get_crc("S*0                                    ")
    00df
    """
    data_bytes = bytes(data, 'ascii')
    dec_crc = crc_result(data_bytes)
    crc = dec_crc.to_bytes(2, 'big').hex()
    return crc


def get_packet(transmit_type: str, end_byte: str, marker: str = "S",
               task_type: str = '*', start_num: str = 18 * SP, end_num: str = 18 * SP) -> str:
    """
    функция возвразает пакет с сформированным crc
    :param marker: Маркер стартового пакета данных
    :param transmit_type:   ‘0’ (30H) – КСА передает данные на ПЭВМ
                            ‘1’ (31H) – КСА принимает данные от ПЭВМ
                            ‘2’ (32H) - прием данных отчетов с обнулением
    :param end_byte: 03H\17H
    :param task_type: Для режима фр = "*"
    :param start_num: Начальное значение используемое при загрузке отчетов, а также некоторых данных
    :param end_num: Конечное значение используемое при загрузке отчетов, а также некоторых данных
    :return: строковый пакет с сформированным crc
    >>> get_packet(str(1), ETX)
    'S*1                                    00db'
    """
    packet = marker + task_type + transmit_type + start_num + end_num + end_byte
    crc = get_crc(packet)
    packet += crc
    return packet


packet = get_packet('0', ETX)
start_packet = STX + packet

start= bytes(start_packet, 'ascii')
print(start)
s = socket.socket()
s.connect((ip_port['ip'], ip_port['port']))
s.send(bytes(ENQ, 'ascii'))
print(f'Данные отправлены {ENQ}')
data = s.recv(1024)
print(answer(data))
s.send(start)
print(f'Данные отправлены {start}')
data = s.recv(1024)
print(answer(data))




