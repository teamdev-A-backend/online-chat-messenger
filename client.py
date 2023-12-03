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
        #user_name = self.encoder(self.username)

        #送信の際のheaderの作成
        user_name_to_byte = self.encoder(self.username)
        user_name_byte_size = len(user_name_to_byte)

        header = self.custom_tcp_header(user_name_byte_size,1,1,user_name_byte_size)

        body = self.encoder(self.username) + self.encoder(self.username)

        # user name
        sent_user_name = self.socket.sendto(
            header+body, (self.server_address, self.server_port))
        print('Send {} bytes'.format(sent_user_name))

        # sent_user_name = self.socket.sendto(
        #     user_name, (self.server_address, self.server_port))
        # print('Send {} bytes'.format(sent_user_name))


        # ユーザー名受信
        print('waiting to receive username')
        data, _ = self.socket.recvfrom(Client.BUFFER_SIZE)
        print('\n received username {!r}'.format(data))
        header = data[:32]
        body = data[32:]

        # header解析
        room_name_size =  int.from_bytes(header[:1], byteorder='big')
        print('\nroom_size: received {} bytes data: {}'.format(
            len(header[:1]), room_name_size))
        operation = int.from_bytes(header[1:2],byteorder='big')
        print('operation: received {} bytes data: {}'.format(
            len(header[1:2]), operation))
        state = int.from_bytes(header[2:3], byteorder='big')
        print('state: received {} bytes data: {}'.format(
            len(header[2:3]), state))

        # body解析
        room_name = self.decoder(body[:room_name_size])
        print('room_name: received {} bytes data: {}'.format(
            len(body[:room_name_size]), room_name))

        operation_payload_size = int.from_bytes(header[3:32], byteorder='big')
        print('payload_size: received {} bytes data: {}'.format(
            len(header[3:32]), operation_payload_size))

        operation_payload = int.from_bytes(body[room_name_size:room_name_size + operation_payload_size], byteorder='big')
        print('user_name: received {} bytes data: {}'.format(len(body[room_name_size:room_name_size + operation_payload_size]), operation_payload))

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
                # データ解析
                header = data[:32]
                body = data[32:]

                # header解析
                room_name_size =  int.from_bytes(header[:1], byteorder='big')
                print('\nroom_size: received {} bytes data: {}'.format(
                    len(header[:1]), room_name_size))
                operation = int.from_bytes(header[1:2],byteorder='big')
                print('operation: received {} bytes data: {}'.format(
                    len(header[1:2]), operation))
                state = int.from_bytes(header[2:3], byteorder='big')
                print('state: received {} bytes data: {}'.format(
                    len(header[2:3]), state))

                operation_payload_size = int.from_bytes(header[3:32], byteorder='big')
                print('payload_size: received {} bytes data: {}'.format(
                    len(header[3:32]), operation_payload_size))

                # body解析
                room_name = self.decoder(body[:room_name_size])
                print('room_name: received {} bytes data: {}'.format(
                    len(body[:room_name_size]), room_name))

                operation_payload = self.decoder(body[room_name_size:room_name_size + operation_payload_size])
                print('user_name: received {} bytes data: {}'.format(
                    len(body[room_name_size:room_name_size + operation_payload_size]), operation_payload))

        finally:
            print('closing socket')
            self.socket.close()

    def custom_tcp_header(self, room_name_size, operation, state, operation_payload_size):
        room_name_size = room_name_size.to_bytes(1, byteorder='big')
        operation = operation.to_bytes(1, byteorder='big')
        state = state.to_bytes(1, byteorder='big')
        operation_payload_size = operation_payload_size.to_bytes(29, byteorder='big')

        return room_name_size + operation + state + operation_payload_size




def main():
    client = Client()
    client.start()


if __name__ == '__main__':
    main()
