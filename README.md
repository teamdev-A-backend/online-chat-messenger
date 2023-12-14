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
class tcp_Server {
  +BUFFER_SIZE: int
  +TIME_OUT: int
  +server_address: str
  +server_port: int
  +socket: socket.socket
  +chat_room_list: dict
  +active_clients: dict
  +user_token: dict
  +room_name: str

  +init(tcp_address: tuple, udp_address: tuple): None
  +start(): None
  +receive_message(): None
  +multicast_send()
  +check_inactive_clients(): None
  +encoder()
  +decoder()
  +check_timeout()
  +is_valid_chatroom()
  +check_chatroom_validity()
}

class udp_Server {
  +BUFFER_SIZE: int
  +TIME_OUT: int
  +server_address: str
  +server_port: int
  +socket: socket.socket
  +chat_room_list: dict
  +active_clients: dict
  +user_token: dict
  +room_name: str

  +init(tcp_address: tuple, udp_address: tuple): None
  +start(): None
  +receive_message(): None
  +multicast_send()
  +check_inactive_clients(): None
  +encoder()
  +decoder()
  +check_timeout()
  +is_valid_chatroom()
  +check_chatroom_validity()

}
class ChatRoom {
  -TIMEOUT: int
  -clients: dict
  -verified_token_to_address: dict
  -name: str
  -is_password_required: bool
  -password: str

  +init(name: str, password: str)
  +add_client(client: ChatClient): bool
  +remove_client(name: str): None
  +remove_all_clients(): None
  +check_timeout(): None
  +notify_disconnection(client: ChatClient): None
  +broadcast(address: str, token: str, msg: str): bool
  +is_authenticated(address: str, token: str): bool
  +get_client_by_name(name: str): ChatClient
  +delete_inactive_clients(address: str, token: str): None
}

ChatRoom o-- udp_Server
ChatRoom o-- tcp_Server

```

## プログラムのデモ

## TCP通信について

## UDP通信について


