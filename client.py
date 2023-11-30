import socket
import threading


class Client():
    NAME_SIZE = 255
    BUFFER_SIZE = 4096

    def __init__(self, server_address='0.0.0.0', server_port=9001):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.server_port = server_port
        self.client_address = self.socket.getsockname()[0]
        self.client_port = self.socket.getsockname()[1]
        self.username = ''
        self.namesize = 0

        self.socket.bind((self.client_address, self.client_port))

    def start(self):
        print(
            f'client address:{self.client_address}, client port:{self.client_port}')

        # ユーザー名セット
        self.set_username()

        # ユーザー名送信
        self.send_username()

        # ユーザーからの入力を送信する処理とサーバーから受信する処理を並列実行する
        thread_send_message = threading.Thread(
            target=self.send_message, daemon=True)
        thread_receive_message = threading.Thread(
            target=self.receive_message, daemon=True)

        thread_send_message.start()
        thread_receive_message.start()

        thread_send_message.join()
        thread_receive_message.join()

    def encoder(self, data: str) -> bytes:
        return data.encode(encoding='utf-8')

    def decoder(self, data: bytes) -> str:
        return data.decode(encoding='utf-8')

    def set_username(self):
        while True:
            username = input("Type in the user name: ")
            if len(self.encoder(username)) > Client.NAME_SIZE:
                print(
                    f'Your name must be equal to or less than {Client.NAME_SIZE} bytes')
                continue
            self.namesize = len(self.encoder(username))
            self.username = username
            break
        return

    def send_username(self):
        user_name = self.encoder(self.username)

        sent_user_name = self.socket.sendto(
            user_name, (self.server_address, self.server_port))
        print('Send {} bytes'.format(sent_user_name))

        # ユーザー名受信
        print('waiting to receive username')
        data, _ = self.socket.recvfrom(Client.BUFFER_SIZE)
        print('\n received username {!r}'.format(data))
        return

    def send_message(self):
        try:
            while True:
                message_body = input("Type in the message: ")

                # 送信データの準備
                # to_bytes()でint→16進数のbyte列に変換
                message = self.namesize.to_bytes(length=1, byteorder='big')
                message += self.encoder(self.username)
                message += self.encoder(message_body)
                print('sending {!r}'.format(message))

                # サーバへのデータ送信
                sent = self.socket.sendto(
                    message, (self.server_address, self.server_port))
                print('Send {} bytes'.format(sent))
        finally:
            print('closing socket')
            self.socket.close()

    def receive_message(self):
        try:
            while True:
                # 応答を受信
                data, _ = self.socket.recvfrom(Client.BUFFER_SIZE)
                print('\n received {!r}'.format(data))
        finally:
            print('closing socket')
            self.socket.close()


def main():
    client = Client()
    client.start()


if __name__ == '__main__':
    main()
