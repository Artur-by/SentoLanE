class Packet:

    def __init__(self):
        self.ENQ = '\x05'  # Инициализация обмена данными (транзакции).
        self.ACK = '\x06'  # подтверждение приема.
        self.NAK = '\x15'  # ответ КСА о том что отправленный запрос некорректен.
        self.STX = '\x02'  # стартовый байт пакета данных
        self.ETX = '\x03'  # стоповый байт пакета данных
        self.ETB = '\x17'  # байт отправляется КСА в порт при включении для передачи информации
        # оборудованию, что КСА включился.
        self.EOT = '\x04'  # байт окончание обмена данными (транзакции).
        self.WACK = '\x09'  # специальный символ, используемый КСА для передачи ПЭВМ информации
        # о том, что КСА занят и ведет обработку данных.Отправляется каждые 1, 5 секунды.
        self.RVI = '\x40'  # байт используется для передачи информации о том, что КСА обнаружил ошибку.
        self.SP = '\x20'  # пробел

    def crc_result(self, data: bytes) -> int:
        """
        метод расчета crc
        :param packet:
        :return: crc
        >>> crc_result(b'S*1                                    \x03')
        219
        """
        crc = 0
        for i in range(len(data)):
            crc ^= data[i] << (i % 9)
        return crc

    def get_crc(self, data: str) -> str:
        """
        метод подсчета crc полученных данных data
        :param data: входная строка с данными
        :return: значение crc в шестнадцатиричном виде
        >>> get_crc("S*0                                    ")
        00df
        """
        data_bytes = bytes(data, 'ascii')
        dec_crc = self.crc_result(data_bytes)
        crc = dec_crc.to_bytes(2, 'big').hex()
        return crc

    def get_packet(self, *args) -> bytes:
        """
        метод для формирования пакетов
        :param args: все необходимые аргументы для конкретного пакета
        :return: пакет
        """
        data = ''
        for i in args:
            data += i
        crc = self.get_crc(data)
        data += crc
        data = self.STX + data
        return bytes(data, 'ascii')

    def normalize(self, depth: int, value_for_normolize: int) -> str:
        """
        метод дозаполнения пробелами данных
        :param value: данные
        :param depth: разрядность
        :return: в строковом виде с дозаполненными пробелами
        >>> normalize(10,100)
               100
        """
        return self.SP * (depth - len(str(value_for_normolize))) + str(value_for_normolize)


class InOutOpen(Packet):
    """
    класс для формирования пакета данных для операций:
    открытия дня -  type_operation = 0
    внесения - type_operation = 1
    выплаты - type_operation = 2
    value  - Сумма внесения\выплаты наличных в\из денежный ящик КСА
    """
    marker = 'D'
    task_type = '*'
    operation = 'C'  # Операции внесения \ выплаты
    depht_in_out_open = 10  # Число байт в value

    def __init__(self, type_operation, value):
        super().__init__()
        self.type_operation = str(type_operation)
        self.value = value

    def in_out_open_packet(self) -> bytes:
        '''
        метод формирования пакета данных для операций внесения, выплаты и открытия смены
        :return: сформированный пакет данных
        '''
        str_value = self.normalize(self.depht_in_out_open, self.value)
        packet = self.marker + self.task_type + self.operation + self.type_operation + str_value + self.ETX
        return self.get_packet(packet)


if __name__ == '__main__':
    start = InOutOpen(1, 100)
    print(start.in_out_open_packet())
    # print(start.get_packet('D*1', ' ' * 6, '1000', '\x20' * 2, '1', '\x20' * 2, '2217', '\x03'))
