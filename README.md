# ♟️ Socket Chess — Multiplayer Chess Over the Internet

A Python chess game with full legal move logic (except En Passant, because honestly — who uses it?)  
Built with `pygame`, powered by sockets, and playable over the internet using `ngrok`.

## 📦 Features

- Classic 2-player **chess** with rules enforced (check, checkmate, castling, promotion — all there)
- **Custom knight** design (no horses — just war)
- **Pass-and-play** local mode
- **Multiplayer mode** over LAN or internet (using `ngrok` tunneling)
- Sockets handled using Python's `socket` and `_thread`
- Auto-assigns White/Black to players on connection

---

## 🧠 Architecture

### 💾 Server (Multiplayer Chess Host)
- Manages two clients via sockets
- Sends color assignment to each player
- Forwards moves to the opposing player in real time

```python
server = "127.0.0.1"  # Can be replaced with public IP/ngrok tunnel
port = 5000

s.bind((server, port))
s.listen(2)  # Waits for two clients
```

### 🧠 Client Network Wrapper

- Connects to remote host (server/ngrok address)
- Sends and receives moves
- Plugged into the main game loop via a `Network` class

```python
network = Network("your-ngrok-address")
my_color = network.get_pos()  # 'white' or 'black'
```

---

## 🔌 How Multiplayer Works

1. Run the **server** on your host machine:

   ```bash
   python server.py
   ```

2. If playing over the internet:

   - Start a TCP tunnel with `ngrok`:

     ```bash
     ngrok tcp 5000
     ```

   - It will generate a forwarding address like `0.tcp.ngrok.io:15124`

3. On both clients, update the network connection:

   ```python
   network = Network("0.tcp.ngrok.io")
   ```

4. Run the **client chess GUI** on both ends:

   ```bash
   python client.py
   ```

5. Play begins when both clients are connected. The server assigns `"white"` to the first and `"black"` to the second.

---

## 🛠️ How to Run (Complete Setup)

```bash
# 1. Clone the repository
git clone https://github.com/yourname/socket-chess.git
cd socket-chess

# 2. Install dependencies
pip install pygame

# 3. Start the server (on the host machine)
python server.py

# 4. If online play is needed (host only):
ngrok tcp 5000

# 5. On both clients:
#    Update the Network class with the ngrok hostname (e.g., 0.tcp.ngrok.io)
#    Ensure the correct port is set (e.g., 15124)

# 6. Run the client GUI
python client.py
```

---

## 🎮 Controls

| Action       | Key / Input    |
| ------------ | -------------- |
| Select Piece | Left-click     |
| Move Piece   | Left-click     |
| Quit         | Window close   |

---

## ⚠️ Limitations

- No AI — strictly 2-player
- En passant is not implemented (by choice 😌)
- No move history or undo
- No game clock

---

## 💡 Behind the Scenes

This project uses:

- **Python Sockets** — for real-time move transmission
- **Multithreading** — handles multiple players without blocking the main loop
- **Pygame** — for GUI, drawing the board, and piece movement
- **Ngrok** — for bypassing firewalls and NAT in multiplayer mode

---

## 🧠 Network Classes

### `Network` (Client)

```python
def send(self, data):
    self.client.send(str.encode(data))

def receive(self):
    return self.client.recv(2048).decode()
```

### `server.py` (Host)

- Accepts 2 connections
- Sends player color
- Forwards all messages between the two sockets

---

## 📸 Screenshots

### Custom pieces
![White Knight](data/images/w_knight.png)
*The custom white Knight*

![Black Knight](data/images/b_knight.png)
*The custom black Knight*

---

## 🔮 What's Next?

This was just the beginning.
Stay tuned for:

- ✨ Custom UI themes
- 🎙️ Voice-based move input
- 🌐 Spectator mode
- 🤖 AI opponent (Minimax incoming?)

---

## 📜 License

MIT License © 2025 Ibtasaam Amjad

---

## ❤️ Special Mention

To the knight who gave up his horse… and chose a warrior's helmet instead.

---
