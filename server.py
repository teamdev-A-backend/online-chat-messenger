import json
import socket
import threading
import time
#from chatroom import ChatRoom
import uuid

class Server():
    BUFFER_SIZE = 4096
    TIME_OUT = 5

    def __init__(self, server_address='0.0.0.0', server_port=9001):
        # 異なるネットワーク上の通信のためソケットドメイン：AF_INETを選択
        # リアルタイム性が必要であるためソケットタイプ：UDPソケットを選択
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.server_port = server_port
        # ソケットを特殊なアドレス0.0.0.0とポート9001に紐付け
        self.socket.bind((server_address, server_port))
        self.active_clients = {}
        # ユーザー名とトークンを関連付ける
        self.user_tokens = {}

    def start(self):
        # 受信を待ち受ける処理とタイムアウトのチェック処理を並列実行する
        # thread_check_timeout = threading.Thread(
        #     target=self.check_timeout, daemon=True)
        # thread_check_timeout.start()
        thread_receive_message = threading.Thread(
            target=self.receive_message, daemon=True)
        thread_receive_message.start()

        # join()でデーモンスレッド終了を待つ:https://bty.sakura.ne.jp/wp/archives/69
        # thread_check_timeout.join()
        thread_receive_message.join()
        return

    def receive_message(self):
        print('starting up on port {}'.format(self.server_port))
        try:
            # データの受信を永久に待ち続ける
            while True:
                print('\nwaiting to receive message')
                data, client_address = self.socket.recvfrom(Server.BUFFER_SIZE)
                # 同一PC内の場合はループバックアドレス(127.0.0.1), clientのportが返却
                print('received {} bytes from {}'.format(
                    len(data), client_address))
                print(data)

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

                operation_payload = self.decoder(body[room_name_size:room_name_size + operation_payload_size], 'str')
                print('user_name: received {} bytes data: {}'.format(
                    len(body[room_name_size:room_name_size + operation_payload_size]), operation_payload))

                if operation == 1:
                    self.initialize_chat_room(room_name, operation_payload, client_address)

                print(self.user_tokens)

                # データ準備
                # username_len = int.from_bytes(data[:1], byteorder='big')
                # username = self.decoder(data[1:1 + username_len])
                # message_body = f"{username}: {self.decoder(data[1 + username_len:])}"

                # データ受信後アクティブなクライアント情報をメモリ上保存
                # self.active_clients[client_address] = {
                #     'username': username, 'last_time': time.time()}

                # if data:
                #     # マルチキャストで送信
                #     self.multicast(self.encoder(message_body))
                #     # sent = self.socket.sendto(data, client_address)
                #     # print('sent {} bytes back to {}'.format(
                #     #     sent, client_address))
        finally:
            print('closing socket')
            self.socket.close()

    def multicast(self, body: bytes) -> None:
        for address in self.active_clients:
            sent = self.socket.sendto(body, address)
            print('sent {} bytes to {}'.format(sent, address))
        return

    # def encoder(self, data: str) -> bytes:
    #     return data.encode(encoding='utf-8')

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

    def check_timeout(self):
        try:
            while True:
                # クライアント情報が全く無くなった場合何もしない
                if not self.active_clients:
                    pass
                else:
                    # 各クライアントのタイムアウトをチェックし、しばらくメッセージ送信がない場合削除する
                    current = time.time()
                    # ToDo:下記エラーを解消してタイムアウト処理を実施する
                    # RuntimeError: dictionary changed size during iteration
                    for client, client_info in self.active_clients.items():
                        if current < client_info['last_time'] + self.TIME_OUT:
                            del self.active_clients[client]
                        else:
                            pass
        finally:
            print('closing socket')
            self.socket.close()




    def initialize_chat_room(self,room_name, username, client_address):
        # 即レスポンスを返す処理。
        print('Start initialize room.')

        operation_payload = 200
        operation_payload_tobyte = operation_payload.to_bytes(1, byteorder='big')

        # headerの作成
        header = self.custom_tcp_header(len(room_name),1,1,len(operation_payload_tobyte))
        # bodyの作成
        body = self.encoder(room_name, 1) + self.encoder(username, 1)
        

        self.socket.sendto(header+body, client_address)
        host_token = generate_user_token()
        self.user_tokens[host_token] = username

        # host_tokenを含んだレスポンス返却処理(payloadに入れて送り返す等)
        token_tobyte = self.encoder(host_token, 1)
        room_name_tobyte = self.encoder(room_name, 1)
        token_response_header = self.custom_tcp_header(len(room_name_tobyte),1,2,len(token_tobyte))
        body = room_name_tobyte + token_tobyte

        #メッセージの送信
        self.socket.sendto(token_response_header+body, client_address)


    def custom_tcp_header(self, room_name_size, operation, state, operation_payload_size):
        room_name_size = room_name_size.to_bytes(1, byteorder='big')
        operation = operation.to_bytes(1, byteorder='big')
        state = state.to_bytes(1, byteorder='big')
        operation_payload_size = operation_payload_size.to_bytes(29, byteorder='big')

        return room_name_size + operation + state + operation_payload_size


def generate_user_token():
    return str(uuid.uuid4())

def main():
    server = Server()
    server.start()


if __name__ == '__main__':
    main()

