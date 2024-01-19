# Online Chat Messenger

## 概要
チャットができるアプリケーションを開発しました。これはクライアントがサーバーのリソースを使用して独自のチャットルームを開始および提供できる
分散システムです。ユーザー管理には、各クライアントに対して一意のトークンを割り当て、安全な識別のためにユーザーをメモリ内のハッシュテーブル
で追跡しています。通信には、ソケットプログラミングを利用してプロセス間通信を可能にしました。チャットルームの参加や作成、トークン生成などの
重要な操作では、SOCK_STREAM型ソケットを選択しました。これらのTCP接続は、順序が保証され、信頼性があり、双方向通信が可能であり、アクセ
ストークンの取得が保証されるのに役立ちます。

初期接続を確立した後、チャットルーム内でのメッセージのライブ中継にはSOCK_DGRAM型ソケットに切り替えます。このUDP接続への切り替えは、リアルタ
イム通信のコストとして、TCPの信頼性よりも速度と効率を優先するトレードオフです。パケットロスのわずかな可能性を受け入れつつも、リアルタイム通信
を行います。

アプリケーションの特徴の一つは、言語に依存しない設計です。異なるプログラミング言語間で通信できるクライアントサーバープログラムを作成し、自身で
設計したアプリケーションレイヤープロトコルを介して相互運用性を確保しました。このプロトコルは、データストリーム内のビットの解釈方法を詳細
に説明し、構造化されたヘッダーとボディを備え、受信したビットをデータに変換する標準的な方法を提供しています。すべてのクライアント/サーバーは、トー
クンの取得後にメッセージの送受信のための異なるプロトコルと、部屋の初期化および作成のためのユニークなリクエスト/レスポンスプロトコルに従います。


## デモ
<img width="530" alt="online_chat_messenger" src="https://github.com/teamdev-A-backend/online-chat-messenger/assets/112442087/c3397d01-24fa-4897-8173-c57485d20750">

## 説明
このアプリケーションは、グループチャットができるアプリケーションです。
グループチャットができるアプリケーションと言えば、日本ではLINEが有名です。
このアプリケーションでは、例に挙げたアプリケーションのメイン機能であるリアルタイムでのグループチャットを楽しむことができます。

アプリケーションは簡単に起動でき、友達を招待してすぐにグループチャットを始めることができます。
アプリケーションの実行には、ターミナルという黒い画面にコマンドを入力します。
基本的な機能として、チャットルームの作成/参加/ユーザー同士でのグループチャットができます。


## インストール
### クローン
このアプリケーションをあなたのPCで実行するために、クローンします。

クローンとは、このアプリケーションの実行に必要なファイル(リポジトリのコンテンツ)をあなたのPCのローカル環境へコピーすることです。

下記手順でクローンしてください。

1. リポジトリをクローンする
```
git clone https://github.com/teamdev-A-backend/online-chat-messenger.git
```

2. クローンしたリポジトリへ移動する
```
cd yourdir
```


## 使用方法
1. ターミナルを3つ起動します。<br>起動した3つのターミナルについては、以降の手順では下記名称で呼ぶこととします。

| ターミナル | 名称 |
| ------- | ------- |
| ターミナル1 | サーバ用ターミナル |
| ターミナル2 | クライアント用ターミナル1 |
| ターミナル3 | クライアント用ターミナル2 |

2. サーバ用ターミナルに下記コマンドを入力する
```
python3 server.py
```
3. クライアント用ターミナル1に下記コマンドを入力する
```
python3 client.py
```
4. クライアント用ターミナルに表示される指示に従い、チャットルームを作成する
5. クライアント用ターミナル2に下記コマンドを入力する
```
python3 client.py
```
6. クライアント用ターミナルに表示される指示に従い、手順4.で作成したチャットルームに参加する
7. ユーザー同士でグループチャットを楽しむ


## 使用例


1. ターミナルを3つ起動します。<br>起動した3つのターミナルについては、以降の手順では下記名称で呼ぶこととします。

| ターミナル | 名称 |
| ------- | ------- |
| ターミナル1 | サーバ用ターミナル |
| ターミナル2 | クライアント用ターミナル1 |
| ターミナル3 | クライアント用ターミナル2 |

2. サーバ用ターミナルに下記コマンドを入力する
```
python3 server.py
```
3. クライアント用ターミナル1に下記コマンドを入力する
```
python3 client.py
```
4. ユーザーがチャットルームを作成する。
```
python3 client.py
```
5. 別のユーザーががチャットルームに参加する
6. ユーザー同士でグループチャットを楽しむ。

### ユーザー入力について
| 用語 | 意味 |
| ------- | ------- |
| チャットルームを新規作成する場合は「1」、チャットルームに参加するには「2」を入力してください: | チャットルームの参加・作成操作です |
| Typr in the user name:| チャットルーム名を入力してください。。<br>入力例. kanata |
|チャットルームの名前を入力してください| <br>入力例,testroom|

## 使用技術
<table>
<tr>
  <th>カテゴリ</th>
  <th>技術スタック</th>
</tr>
<tr>
  <td>開発言語</td>
  <td>Python</td>
</tr>
<tr>
  <td rowspan=2>インフラ</td>
  <td>Ubuntu</td>
</tr>
<tr>
  <td>VirtualBox</td>
</tr>
<tr>
  <td rowspan=2>その他</td>
  <td>Git</td>
</tr>
<tr>
  <td>Github</td>
</tr>
</table>


## プログラムの流れ

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
   
2. chat_roomクラスを別で作ってユーザーを各クラス間で伝達しやすくしました。
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
### client
```mermaid
classDiagram
    class TCPClient {
        -NAME_SIZE: int
        -BUFFER_SIZE: int
        -socket: socket
        -server_address: str
        -server_port: int
        -username: str
        -namesize: int
        +__init__(server_address: str, server_port: int): None
        +start(): None
        +encoder(data: Any, intsize: int): bytes
        +decoder(data: bytes, result_type: str): Any
        +set_username(): None
        +send_username(operation: int, chatroom_name: str): None
        +receive_message(): None
        +custom_tcp_header(room_name_size: int, operation: int, state: int, operation_payload_size: int): bytes
        +select_action_mode(): int
        +input_room_name(): str
    }

class UDPClient {
        -BUFFER_SIZE: int
        -socket: socket
        -server_address: str
        -server_port: int
        -client_address: str
        -client_port: int
        -username: str
        -room_name: str
        -user_token: str
        -namesize: int
        +__init__(server_address: str, server_port: int, room_name: str, user_token: str): None
        +start(): None
        +encoder(data: Any, intsize: int): bytes
        +decoder(data: bytes, result_type: str): Any
        +send_message(room_name: str, token: str): None
        +receive_message(): None
    }

```


## TCP通信について
-  TCP（Transmission Control Protocol）は、インターネットプロトコルスイートの一部であり、ネットワークを介してデータを送受信するためのプロトコルの一つです。
-  TCPは、データの送受信を確実に行うための信頼性の高い接続を提供します。今回のchat room作成/接続は送受信の確実性が重要なため採用しました。


- ヘッダー（32バイト）：RoomNameSize（1バイト） | Operation（1バイト） | State（1バイト） | OperationPayloadSize（29バイト）
- ボディ：最初のRoomNameSizeバイトがルーム名で、その後にOperationPayloadSizeバイトが続きます。ルーム名の最大バイト数は2^8バイトであり、OperationPayloadSizeの最大バイト数は2^29バイトです。


## UDP通信について
- UDP（User Datagram Protocol）は、インターネットプロトコルスイートの一部であり、ネットワークを介してデータを送受信するためのプロトコルの一つです。
- UDPは、データの送受信を高速に行うためのシンプルな接続を提供します。


- Client側でメッセージのサイズを検証。4096を超えたら再入力を促す。
- ヘッダー：RoomNameSize（1バイト）| TokenSize（1バイト）
- ボディ：最初のRoomNameSizeバイトはルーム名、次のTokenSizeバイトはトークン文字列、そしてその残りが実際のメッセージです。







