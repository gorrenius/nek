from sshtunnel import SSHTunnelForwarder

from config import (
    SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS, PG_HOST, PG_PORT, logger,
)


class SSH:

    def __init__(self):
        # Объект подключения к серверу SSH
        self.client = None

    def ssh_session(self):
        """
        Функция открывает подключение по протоколу SSH к серверу SSH
        :return:
        local_host: str - IP адрес сервера БД со стороны сервера SSH
        local_port: int - порт сервера БД со стороны сервера SSH
        """
        local_host, local_port = None, None
        try:
            address = (SSH_HOST, SSH_PORT)
            bind_address = (PG_HOST, PG_PORT)
            user, password = SSH_USER, SSH_PASS
            # Создаёт объект подключения к серверу SSH
            self.client = SSHTunnelForwarder(
                address, ssh_username=user, ssh_password=password,
                remote_bind_address=bind_address
            )
            # Старт сессии подключения к серверу SSH
            self.client.start()
            # local_host = self.client.local_bind_host # it is for Linux
            local_host = '127.0.0.1'  # it is for Windows
            local_port = self.client.local_bind_port
        except Exception as ex:
            logger.error(str(ex))
            print(str(ex))
        return local_host, local_port

    def ssh_close(self):
        """
        Закрытие сессии подключения к серверу SSH
        """
        if self.client is not None:
            self.client.close()


if __name__ == '__main__':
    print('This is no execute file.')
