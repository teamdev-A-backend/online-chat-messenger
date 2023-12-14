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
## ER図

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

```

## プログラムのデモ

## TCP通信について

## UDP通信について


