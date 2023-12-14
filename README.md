# Online Chat Messenger

## 概要
このプロジェクトは、クライアントとサーバ間でTCP通信のチャットルームの作成/参加とUDP通信のメッセージの送受信をするプロジェクトです。CLIで操作をします。
また、3人のチーム開発でこのプロジェクトは完成させました。

### プログラムの流れ


1. クライアントでチャット作成(1)/参加(2)の選択
2. クライアントのCLIに従ってユーザーが入力
3. サーバ側が受け取った情報を元にユーザー・チャットルームを作成/参加
4. サーバが受け取ったデータをクライアントに送信
5. チャットスタート

```mermaid
graph TD
    A[CLI起動] --> B[このプロジェクトをクローン]
    B -- TCP通信 --> C[チャットルーム作成]
    B -- TCP通信 --> D[チャットルーム参加]
    C --> E[チャット名入力/ユーザー名入力]
    D --> E
    E -- UDP通信 --> F[メッセージの送信]
    
    
```

## プロジェクトの創意工夫点
1. このプロジェクトではUDP/TCP通信で処理を進めていることからクラスを
   - server.pyをudp_serverとtcp_server
   - client.pyをudp_clientとtcp_client
   に分けるようにしてTCP→UDPの処理をスムーズに開発できるようにしました。
2. 
## クラス図

### 1. server
```mermaid
classDiagram
    class udp_Server {
        -BUFFER_SIZE: int
        -TIME_OUT: int
        -socket: socket
        -server_address: str
        -server_port: int
        -active_clients: dict
        -user_tokens: dict
        -chat_rooms: list
        -room_name: str
        +__init__(chatroom_list: list, server_address: str, server_port: int)
        +start(): None
        -receive_message(): None
        -multicast_send(message: str, room_name: str): None
        -check_inactive_clients(): None
        -encoder(data: str, intsize: int): bytes
        -decoder(data: bytes, result_type: str): str
        -check_timeout(): None
        -is_valid_chatroom(chat_rooms: dict, room_name_decode: str): bool
        -check_chatroom_validity(chat_rooms: dict, room_name_decode: str): None
    }
 class tcp_Server {
        -buffer_size: int
        -time_out: int
        -socket: socket
        -address: str
        -port: int
        -user_tokens: dict
        -chat_room_list: list
        +__init__(chatroom_list: list)
        +encoder(data: str, intsize: int): bytes
        +decoder(data: bytes, result_type: str): str
        +start(): None
        -handle_chat_connection(): None
        -process_message(data: bytes, client_socket: socket): None
        -initialize_chat_room(room_name: bytes, state: int, username: str, client_socket: socket): None
        -handle_token_response(room_name: bytes, state: int, username: str, client_socket: socket): None
        -custom_tcp_header(room_name_size: int, operation: int, state: int, operation_payload_size: int): bytes
        -custom_tcp_body_by_json(status_code: int, token: str): dict
        -authorize_to_join_chatroom(token: str, room_name: bytes, state: int, operation_payload: str, client_address: tuple): None
    }
class chat_room {
        -chat_room_list: dict
        +__init__(): None
        +create_chat_room(room_name: str, username: str, host_token: str, client_address: tuple): None
        +add_member_to_chatroom(room_name: str, member_token: str, client_address: tuple): None
        +remove_member_from_chatroom(room_name: str, member_token: str, client_address: tuple): None
        +remove_chatroom(room_name: str, member_token: str, client_address: tuple): None
    }
tcp_Server o-- chat_room
udp_Server o-- chat_room

```

## プログラムのデモ

## TCP通信について

## UDP通信について


