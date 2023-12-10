import json
import socket
import threading
import time
#from chatroom import ChatRoom
import uuid

# ここからUDPサーバーの実装
class udp_Server():
    BUFFER_SIZE = 4096
    TIME_OUT = 5

    def __init__(self, server_address='0.0.0.0', server_port=9001):
        # 異なるネットワーク上の通信のためソケットドメイン：AF_INETを選択
        # リアルタイム性が必要であるためソケットタイプ：UDPソケットを選択
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.server_port = server_port
        # ソケットを特殊なアドレス0.0.0.0とポート8080に紐付け
        self.socket.bind((server_address, server_port))
        self.active_clients = {}
        # ユーザー名とトークンを関連付ける
        self.user_tokens = {}
        self.chat_rooms = {} # ToDo:tcp_Serverのchat_roomsを何らかの方法で共有する
        self.room_name = '' # ToDo:tcp_Serverで作成したchat_room_nameを何らかの方法で共有する


    def start(self):
        # 受信を待ち受ける処理とタイムアウトのチェック処理を並列実行する
        # thread_check_timeout = threading.Thread(
        #     target=self.check_timeout, daemon=True)
        # thread_check_timeout.start()
        thread_receive_message = threading.Thread(
            target=self.receive_message, daemon=True)
        thread_receive_message.start()

        thread_check_room_validity = threading.Thread(
            target=self.check_chatroom_validity, args=(self.chat_rooms, self.room_name), daemon=True)
        thread_check_room_validity.start()

        # join()でデーモンスレッド終了を待つ:https://bty.sakura.ne.jp/wp/archives/69
        # thread_check_timeout.join()
        thread_receive_message.join()
        thread_check_room_validity.join()
        return

    def receive_message(self):
        print('starting up on port {}'.format(self.server_port))
        try:
            # データの受信を永久に待ち続ける
            while True:
                print('\nwaiting to receive message')
                data, client_address = self.socket.recvfrom(udp_Server.BUFFER_SIZE)
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
    
    def is_valid_chatroom(self, chat_rooms, room_name_decode):
        # chatroomの有効/無効の判断をhostの存在有無で行う
        try:
            host_info = chat_rooms[room_name_decode]['host']
        except KeyError:
            print('The chatroom is invalid.')
        # hostが存在する場合はTrueを返す
        return bool(host_info)

    def check_chatroom_validity(self, chat_rooms, room_name_decode):
        try:
            while True:
                if self.is_valid_chatroom(chat_rooms, room_name_decode):
                    # chatroomが有効な場合何もしない
                    pass
                else:
                    print('Invalid chatroom. closing socket...')
                    self.socket.close()
        finally:
            print('closing socket')
            self.socket.close()




    #def initialize_chat_room(self,room_name, username, client_address):
        # 即レスポンスを返す処理。
        #print('Start initialize room.')

        #operation_payload = 200
        #operation_payload_tobyte = operation_payload.to_bytes(1, byteorder='big')

        # ルーム名のバイト数が最大バイト数を超えている場合はエラーを返す
        #if len(room_name) > 2**8:
            #raise ValueError('The length of room name is too long.')
        # ペイロードのバイト数が最大バイト数を超えている場合はエラーを返す
        #if len(operation_payload_tobyte) > 2**29:
            #raise ValueError('The length of operation payload is too long.')

        # headerの作成
        #header = self.custom_tcp_header(len(room_name),1,1,len(operation_payload_tobyte))
        # bodyの作成
        #body = self.encoder(room_name, 1) + self.encoder(username, 1)


        #self.socket.sendto(header+body, client_address)
        #host_token = generate_user_token()
        #self.user_tokens[host_token] = username

        # host_tokenを含んだレスポンス返却処理(payloadに入れて送り返す等)
        #token_tobyte = self.encoder(host_token, 1)
        #room_name_tobyte = self.encoder(room_name, 1)
        #token_response_header = self.custom_tcp_header(len(room_name_tobyte),1,2,len(token_tobyte))
        #body = room_name_tobyte + token_tobyte

        #メッセージの送信
        #self.socket.sendto(token_response_header+body, client_address)


    #def custom_tcp_header(self, room_name_size, operation, state, operation_payload_size):
        #room_name_size = room_name_size.to_bytes(1, byteorder='big')
        #operation = operation.to_bytes(1, byteorder='big')
        #state = state.to_bytes(1, byteorder='big')
        #operation_payload_size = operation_payload_size.to_bytes(29, byteorder='big')

        #return room_name_size + operation + state + operation_payload_size




# ここからTCPサーバーの実装
class tcp_Server:
    buffer_size = 4096
    time_out = 5

    def __init__(self, chatroom_list):
        # Initialize the TCP server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = '0.0.0.0'
        self.port = 12345
        self.socket.bind((self.address, self.port))
        self.socket.listen(1)
        self.user_tokens = {}
        self.chat_room_list = chatroom_list

        print('TCP Server started. It is on {}, port {}'.format(self.address, self.port))


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

    def start(self):
        # Start the TCP server
        thread_chat = threading.Thread(target=self.handle_chat_connection, daemon=True)
        thread_chat.start()
        thread_chat.join()
        return

    def handle_chat_connection(self):
        # Handle the client connection
        try:
            while True:
                print('チャットルームの作成をするか、参加するかを選択してください。1か2を選択してください')
                print("1: チャットルームの作成")
                print("2: チャットルームに参加")
                data, client_address = self.socket.accept()
                print('connection from', client_address)
                self.process_message(data, client_address)
        finally:
            print('closing socket')
            self.socket.close()



    def process_message(self, data, client_address):
        # Process the received message

        print('received {} bytes from {}'.format(len(data), client_address))
        # データをheaderとbodyに分割
        header = data[:32]
        body = data[32:]

        # header解析
        room_name_size = int.from_bytes(header[0:1], byteorder='big')
        operation = int.from_bytes(header[1:2], byteorder='big')
        state = int.from_bytes(header[2:3], byteorder='big')
        operation_payload_size = int.from_bytes(header[3:32], byteorder='big')

        # body解析
        room_name = body[:room_name_size]
        operation_payload = body[room_name_size:room_name_size+operation_payload_size]

        # bodyのデコード
        room_name_decode = self.decoder(room_name, 'str')
        operation_payload_decode = self.decoder(operation_payload, 'str')

        # bodyのデコード結果のバイト数をチェック
        if len(room_name_decode) > 2**8:
            raise ValueError('The length of room name is too long.')
        if len(operation_payload_decode) > 2**29:
            raise ValueError('The length of operation payload is too long.')

        # create room
        if operation == 1:
            self.initialize_chat_room(room_name, state, operation_payload, client_address)

        # join room
        elif operation == 2:
            # ToDo：クライアントが保持しているトークンを含むUDPパケットを解析して取得する
            client_token = 'decoded udp packet'
            # chat_roomに参加するための許可トークンとIPアドレスを照合する
            self.authorize_to_join_chatroom(self, client_token, client_address, room_name_decode)

            self.handle_token_response(room_name, state, operation_payload, client_address)

    def initialize_chat_room(self, room_name, state ,username, client_address):
        # 新しいチャットルームを作成したときに呼び出される関数
        print('Start initialize room.')

        operation_payload = 200
        operation_payload_tobyte = operation_payload.to_bytes(1, byteorder='big')

        # Return an error if the length of room name exceeds the maximum byte size
        if len(room_name) > 2**8:
            raise ValueError('The length of room name is too long.')
        # Return an error if the length of operation payload exceeds the maximum byte size
        if len(operation_payload_tobyte) > 2**29:
            raise ValueError('The length of operation payload is too long.')

        # Create the header
        header = self.custom_tcp_header(len(room_name), 1, 1, len(operation_payload_tobyte))
        # Create the body
        body = self.encoder(room_name, 1) + self.encoder(username, 1)

        self.socket.sendto(header + body, client_address)
        host_token = generate_user_token()
        self.user_tokens[host_token] = username

        room_name_decode = self.decoder(room_name, 'str')

        # それぞれのroomに紐づく(token,address)のリストへの追加処理
        # self.chat_rooms[room_name_decode] = {'host' : set(), 'members': set()}
        # self.chat_rooms[room_name_decode]['host'].add((host_token, username))
        # self.chat_rooms[room_name_decode]['members'].add((host_token, client_address))

        try:
            self.chat_room_list.create_chat_room(room_name_decode, username, host_token, client_address)

        except ValueError:
            operation_payload = self.custom_tcp_body_by_json(400,None)
            operation_payload_tobyte = self.encoder(self.encoder(operation_payload))
            header = self.custom_tcp_header(0,1,2,len(operation_payload_tobyte))
            body = operation_payload_tobyte
            self.socket.sendto(header+body, client_address)

        else:
            print( self.chat_room_list)

            # host_tokenを含んだレスポンス返却処理(payloadに入れて送り返す等)
            #token_tobyte = self.encoder(host_token, 1)
            #room_name_tobyte = self.encoder(room_name, 1)

            # レスポンス共通化のためにjsonで返却
            token_json = self.custom_tcp_body_by_json(200,host_token)
            token_json_encoded = self.encoder(self.encoder(token_json))
            token_response_header = self.custom_tcp_header(len(room_name),1,2,len(token_json_encoded))

            # token_response_header = self.custom_tcp_header(len(room_name_tobyte),1,2,len(token_tobyte))
            # body = room_name_tobyte + token_tobyte
            body = room_name + token_json_encoded

            # Send the message
            self.socket.sendto(token_response_header + body, client_address)


    def handle_token_response(self, room_name, state, username, client_address):
        # 新しいユーザーがチャットルームに参加したときに呼び出される関数
        print('Handle token response.')

        # Process the token and perform necessary actions

        operation_payload = 200
        operation_payload_tobyte = operation_payload.to_bytes(1, byteorder='big')

        # Return an error if the length of room name exceeds the maximum byte size
        if len(room_name) > 2**8:
            raise ValueError('The length of room name is too long.')
        # Return an error if the length of operation payload exceeds the maximum byte size
        if len(operation_payload_tobyte) > 2**29:
            raise ValueError('The length of operation payload is too long.')

        # Create the header
        header = self.custom_tcp_header(len(room_name), 1, 1, len(operation_payload_tobyte))
        # Create the body
        body = room_name + self.encoder(username, 1)

        self.socket.sendto(header + body, client_address)

        #roomが見つからなかったとき、404レスポンス
        try:
            member_token = generate_user_token()
            room_name_decode = self.decoder(room_name, 'str')
            #self.chat_rooms[room_name_decode]['members'].add((member_token, client_address))
            self.chat_room_list.add_member_to_chatroom(room_name_decode, member_token, client_address)
        except KeyError:
            print('Chatroom does not exist.')
            operation_payload = self.custom_tcp_body_by_json(404,None)
            operation_payload_tobyte =self.encoder(self.encoder(operation_payload))
            header = self.custom_tcp_header(0,2,2,len(operation_payload_tobyte))
            body = operation_payload_tobyte
            self.socket.sendto(header+body, client_address)

        else:
            body_json = self.custom_tcp_body_by_json(200,member_token)
            body_json_encoded = self.encoder(self.encoder(body_json))

            member_response_header = self.custom_tcp_header(len(room_name),2,2,len(body_json_encoded))
            member_response_body = room_name + body_json_encoded
            self.socket.sendto(member_response_header+member_response_body, client_address)
            print(self.chat_rooms)


    def custom_tcp_header(self, room_name_size, operation, state, operation_payload_size):
        # Create the custom TCP header
        room_name_size = room_name_size.to_bytes(1, byteorder='big')
        operation = operation.to_bytes(1, byteorder='big')
        state = state.to_bytes(1, byteorder='big')
        operation_payload_size = operation_payload_size.to_bytes(29, byteorder='big')

        return room_name_size + operation + state + operation_payload_size

    def custom_tcp_body_by_json(self, status_code, token):
        body_json = {
            "status_code" : status_code,
            "user_token": token
        }
        return body_json
      
    def authorize_to_join_chatroom(self, token, room_name, state, operation_payload, client_address):
        # tokenとaddressがServerで所持しているtokenに紐づくIPアドレスと一致するか確認する
        room_name_decode = self.decoder(room_name, 'str')
        room_members = self.chat_rooms[room_name_decode]['members']
        client_info = (token, client_address)
        if client_info in room_members:
            print('You can join the chatroom.')
        else:
            # 一致しなかった場合チャットルーム作成に戻る
            print('You cannot join the chatroom.')
            self.initialize_chat_room(room_name, state, operation_payload, client_address)
        return

class chat_room:
    def __init__(self):
        self.chat_room_list = {}

    def create_chat_room(self, room_name, username, host_token, client_address):
        if room_name not in self.chat_room_list:
            self.chat_room_list[room_name] = {'host' : set(), 'members': set()}
            self.chat_room_list[room_name]['host'].add((host_token, username))
            self.chat_room_list[room_name]['members'].add((host_token, client_address))
        else:
            raise ValueError(f"Room name: '{room_name}' is already in use.")

    def add_member_to_chatroom(self, room_name, member_token, client_address):
        if room_name in self.chat_room_list:
            self.chat_room_list[room_name]['members'].add((member_token, client_address))
        else:
            raise KeyError

def generate_user_token():
    return str(uuid.uuid4())

def main():
    # udp_server = udp_Server()
    # udp_server.start()
    chat_room_list = chat_room()

    tcp_server = tcp_Server(chat_room_list)
    tcp_server.start()


if __name__ == '__main__':
    main()
