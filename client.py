import json
import socket
import threading

class TCPClient:
    NAME_SIZE = 255
    BUFFER_SIZE = 4096

    def __init__(self, server_address='0.0.0.0', server_port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.server_port = server_port
        self.username = ''
        self.namesize = 0

        #サーバーに接続
        try:
            self.socket.connect((self.server_address, self.server_port))
            print(f"Connected to server at {self.server_address}:{self.server_port}")
        except Exception as e:
                print(f"Error occurred: {e}")


    def start(self):
        print(
            f'server address:{self.server_address}, server port:{self.server_port}')

        #チャットルーム新規作成か参加か選ぶ
        operation_type = self.select_action_mode()

        # ユーザー名セット
        self.set_username()

        chatroom_name = self.input_room_name()
        # ユーザー名送信
        self.send_username(operation_type, chatroom_name)

        thread_receive_message = threading.Thread(
            target=self.receive_message, daemon=True)

        #thread_send_message.start()
        thread_receive_message.start()

        #thread_send_message.join()
        thread_receive_message.join()

    def encoder(self, data, intsize: int = 1):
        if type(data) == str:
            return data.encode(encoding='utf-8') # to bytes
        elif type(data) == int:
            return data.to_bytes(intsize, byteorder='big') # to bytes
        elif type(data) == dict:
            return json.dumps(data) # to str
        else:
            print('Invalid data was specified.')

    # def decoder(self, data: bytes) -> str:
    #     return data.decode(encoding='utf-8')

    def decoder(self, data: bytes, result_type: str = 'str'):
        if result_type == 'str':
            return data.decode(encoding='utf-8')
        elif result_type == 'int':
            return int.from_bytes(data, byteorder='big')
        elif result_type == 'dict':
            return json.loads(data)
        else:
            print('Invalid data was specified.')

    def set_username(self):
        while True:
            username = input("Type in the user name: ")
            if len(self.encoder(username, 1)) > TCPClient.NAME_SIZE:
                print(
                    f'Your name must be equal to or less than {TCPClient.NAME_SIZE} bytes')
                continue
            self.namesize = len(self.encoder(username, 1))
            self.username = username
            break
        return

    def send_username(self, operation, chatroom_name):
        #user_name = self.encoder(self.username)

        #送信の際のheaderの作成
        user_name_to_byte = self.encoder(self.username, 1)
        user_name_byte_size = len(user_name_to_byte)

        chatroom_name_to_byte = self.encoder(chatroom_name, 1)
        chatroom_name_byte_size = len(chatroom_name_to_byte)

        header = self.custom_tcp_header(chatroom_name_byte_size,operation,1,user_name_byte_size)

        body = chatroom_name_to_byte + self.encoder(self.username, 1)

        #メッセージの送信
        print('sending {!r}'.format(header+body))
        self.socket.sendall(header+body)
        print('Send {} bytes'.format(len(header+body)))


        # データ受信
        print('waiting to receive data from server')
        data = self.socket.recv(TCPClient.BUFFER_SIZE)
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
        room_name = self.decoder(body[:room_name_size], 'str')
        print('room_name: received {} bytes data: {}'.format(
            len(body[:room_name_size]), room_name))

        operation_payload_size = int.from_bytes(header[3:32], byteorder='big')
        print('payload_size: received {} bytes data: {}'.format(
            len(header[3:32]), operation_payload_size))

        operation_payload = int.from_bytes(body[room_name_size:room_name_size + operation_payload_size], byteorder='big')
        print('user_name: received {} bytes data: {}'.format(len(body[room_name_size:room_name_size + operation_payload_size]), operation_payload))

        return

    def receive_message(self):
        try:
            while True:
                # 応答を受信
                #data, _ = self.socket.recvfrom(UDPClient.BUFFER_SIZE)
                data = self.socket.recv(TCPClient.BUFFER_SIZE)
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
                room_name = self.decoder(body[:room_name_size], 'str')
                print('room_name: received {} bytes data: {}'.format(
                    len(body[:room_name_size]), room_name))

                #operation_payload = self.decoder(body[room_name_size:room_name_size + operation_payload_size], 'str')
                operation_payload = self.decoder(body[room_name_size:room_name_size + operation_payload_size],'dict')
                print('user_name: received {} bytes data: {}'.format(
                    len(body[room_name_size:room_name_size + operation_payload_size]), operation_payload))

                if state == 2 and operation_payload["status_code"] == 200:
                    self.user_token = operation_payload["user_token"]
                    print(self.user_token)
                    print('closing socket')
                    self.socket.close()
                    udp_client = UDPClient(room_name=room_name, user_token=self.user_token)
                    udp_client.start()
                    break
                elif state == 2 and operation_payload["status_code"] == 404:
                    print("チャットルームが存在しません、最初からやり直します。")
                    self.start()
                    break
                elif state == 2 and operation_payload["status_code"] == 400:
                    print("処理に失敗しました、最初からやり直します。")
                    self.start()
                    break

        finally:
            print('closing socket')
            # self.socket.close()




    def custom_tcp_header(self, room_name_size, operation, state, operation_payload_size):
        room_name_size = room_name_size.to_bytes(1, byteorder='big')
        operation = operation.to_bytes(1, byteorder='big')
        state = state.to_bytes(1, byteorder='big')
        operation_payload_size = operation_payload_size.to_bytes(29, byteorder='big')

        return room_name_size + operation + state + operation_payload_size


    def select_action_mode(self):
        while True:
            type = input('チャットルームを新規作成する場合は「1」、チャットルームに参加する場合は「2」を入力してください: ')
            if type == "1" :
                return 1
            elif type == "2" :
                return 2
            else:
               print('入力を受け取ることができませんでした。')

    def input_room_name(self):
        while True:
            room_name = input('チャットルームの名前を入力してください。: ')
            if room_name:
                return room_name
            else:
                print('ルーム名が確認できません。')

class UDPClient:
    BUFFER_SIZE = 4094
    def __init__(self, server_address='0.0.0.0', server_port=9001, room_name = '', user_token = ''):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.server_port = server_port

        self.client_address = self.socket.getsockname()[0]
        self.client_port = self.socket.getsockname()[1]
        self.username = ''
        self.room_name = room_name
        self.user_token = user_token
        self.namesize = 0

        #サーバーに接続
        # self.socket.connect((self.server_address, self.server_port))
    def start(self):
        print('UDP Client started.')
        print(
            f'server address:{self.server_address}, server port:{self.server_port}')


        #メッセージの送信
        thread_send_message = threading.Thread(target=self.send_message, args=(self.room_name, self.user_token))
        thread_receive_message = threading.Thread(target=self.receive_message)

        thread_send_message.start()
        thread_receive_message.start()

        thread_send_message.join()
        thread_receive_message.join()

    def encoder(self, data, intsize: int = 1):
        if type(data) == str:
            return data.encode(encoding='utf-8') # to bytes
        elif type(data) == int:
            return data.to_bytes(intsize, byteorder='big') # to bytes
        elif type(data) == dict:
            return json.dumps(data) # to str
        else:
            print('Invalid data was specified.')

    # def decoder(self, data: bytes) -> str:
    #     return data.decode(encoding='utf-8')

    def decoder(self, data: bytes, result_type: str = 'str'):
        if result_type == 'str':
            return data.decode(encoding='utf-8')
        elif result_type == 'int':
            return int.from_bytes(data, byteorder='big')
        elif result_type == 'dict':
            return json.loads(data)
        else:
            print('Invalid data was specified.')


    def send_message(self, room_name, token):
        try:
            while True:
                message_body = input("Type in the message: ")

                # # 送信データの準備
                # # to_bytes()でint→16進数のbyte列に変換
                # message = self.namesize.to_bytes(length=1, byteorder='big')
                # message += self.encoder(self.username, 1)
                # message += self.encoder(message_body, 1)
                # print('sending {!r}'.format(message))
                

                room_name_size = len(self.encoder(room_name, 1))
                token_size = len(self.encoder(token, 1))

                message = room_name_size.to_bytes(length=1, byteorder='big')
                message += token_size.to_bytes(length=1, byteorder='big')
                message += self.encoder(message_body, 1)
                print('sending {!r}'.format(message))

                # udpサーバへのデータ送信
                print("udp_client_socket: ", self.socket)
                sent = self.socket.sendto(
                    message, (self.server_address, self.server_port))
                print('Send {} bytes'.format(sent))
        finally:
            print('closing socket')
            # self.socket.close()

    def receive_message(self):
        try:
            while True:
                # 応答を受信
                data, _ = self.socket.recvfrom(UDPClient.BUFFER_SIZE)
                print('\n received {!r}'.format(data))
                 # データをheaderとbodyに分割
                header = data[:2]
                body = data[2:]

                # header解析
                room_name_size = int.from_bytes(header[0:1], byteorder='big')
                token_size = int.from_bytes(header[1:2], byteorder='big')
                print('\nroom_size: received {} bytes data: {}'.format(
                     len(header[0:1]), room_name_size))
                print('\ntoken_size: received {} bytes data: {}'.format(
                     len(body[0:1]), token_size))

                # body解析
                room_name = body[:room_name_size]
                token = body[room_name_size:room_name_size+token_size]
                message_body = body[room_name_size+token_size:]

                # bodyのデコード
                room_name_decode = self.decoder(room_name, 'str')
                token_decode = self.decoder(token, 'str')
                message_body_decode = self.decoder(message_body, 'str')
                print('room_name: received {} bytes data: {}'.format(
                     len(room_name), room_name_decode))
                print('token: received {} bytes data: {}'.format(
                     len(token), token_decode))
                print('message_body: received {} bytes data: {}'.format(
                     len(message_body), message_body_decode))
                # # データ解析
                # header = data[:32]
                # body = data[32:]

                # # header解析
                # room_name_size =  int.from_bytes(header[:1], byteorder='big')
                # print('\nroom_size: received {} bytes data: {}'.format(
                #     len(header[:1]), room_name_size))
                # operation = int.from_bytes(header[1:2],byteorder='big')
                # print('operation: received {} bytes data: {}'.format(
                #     len(header[1:2]), operation))
                # state = int.from_bytes(header[2:3], byteorder='big')
                # print('state: received {} bytes data: {}'.format(
                #     len(header[2:3]), state))

                # operation_payload_size = int.from_bytes(header[3:32], byteorder='big')
                # print('payload_size: received {} bytes data: {}'.format(
                #     len(header[3:32]), operation_payload_size))

                # # body解析
                # room_name = self.decoder(body[:room_name_size], 'str')
                # print('room_name: received {} bytes data: {}'.format(
                #     len(body[:room_name_size]), room_name))

                # #operation_payload = self.decoder(body[room_name_size:room_name_size + operation_payload_size], 'str')
                # operation_payload = self.decoder(body[room_name_size:room_name_size + operation_payload_size],'dict')
                # print('user_name: received {} bytes data: {}'.format(
                #     len(body[room_name_size:room_name_size + operation_payload_size]), operation_payload))

                # if state == 2 and operation_payload["status_code"] == 200:
                #     self.user_token = operation_payload["user_token"]
                #     print(self.user_token)
                #     break
                # elif state == 2 and operation_payload["status_code"] == 404:
                #     print("チャットルームが存在しません、最初からやり直します。")
                #     self.start()
                #     break
                # elif state == 2 and operation_payload["status_code"] == 400:
                #     print("処理に失敗しました、最初からやり直します。")
                #     self.start()
                #     break

        finally:
            print('closing socket')
            # self.socket.close()






def main():
    # チャットルーム新規作成か参加か選ぶ
    tcp_client = TCPClient()
    tcp_client.start()

    # メッセージの送受信
    #udp_client = UDPClient()
    #udp_client.start()


if __name__ == '__main__':
    main()
